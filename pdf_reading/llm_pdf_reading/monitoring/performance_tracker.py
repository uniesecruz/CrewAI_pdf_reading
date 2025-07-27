"""
Rastreador de performance para monitoramento em tempo real
"""
import time
import threading
import logging
from typing import Dict, Any, Callable, Optional
from contextlib import contextmanager
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics

from .metrics_collector import MetricsCollector, metrics_collector
from .config import PERFORMANCE_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class PerformanceStats:
    """Estatísticas de performance"""
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    memory_start: Optional[float] = None
    memory_end: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def finish(self, metadata: Optional[Dict[str, Any]] = None):
        """Finaliza a medição"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        if metadata:
            self.metadata = {**(self.metadata or {}), **metadata}

class PerformanceTracker:
    """Rastreador de performance para operações LLM e PDF"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        # Importar e criar MetricsCollector se não fornecido
        if metrics_collector is None:
            from .metrics_collector import MetricsCollector
            metrics_collector = MetricsCollector()
        
        self.metrics_collector = metrics_collector
        self.active_operations: Dict[str, PerformanceStats] = {}
        self.completed_operations: list[PerformanceStats] = []
        self.thresholds = PERFORMANCE_CONFIG
        self._lock = threading.Lock()
        
        # Histórico de performance
        self.operation_history: Dict[str, list[float]] = {}
        
    @contextmanager
    def track_operation(self, operation_name: str, **metadata):
        """Context manager para rastrear uma operação"""
        
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        # Coletar métricas do sistema no início
        system_metrics = self.metrics_collector.collect_system_metrics()
        
        stats = PerformanceStats(
            operation=operation_name,
            start_time=datetime.now(),
            memory_start=system_metrics.memory_usage,
            metadata=metadata
        )
        
        with self._lock:
            self.active_operations[operation_id] = stats
        
        try:
            yield stats
            
        except Exception as e:
            stats.metadata = {**(stats.metadata or {}), 'error': str(e)}
            raise
            
        finally:
            # Finalizar medição
            system_metrics_end = self.metrics_collector.collect_system_metrics()
            stats.memory_end = system_metrics_end.memory_usage
            stats.finish()
            
            with self._lock:
                self.active_operations.pop(operation_id, None)
                self.completed_operations.append(stats)
                
                # Manter apenas últimas 100 operações
                if len(self.completed_operations) > 100:
                    self.completed_operations = self.completed_operations[-100:]
            
            # Adicionar ao histórico
            self._add_to_history(operation_name, stats.duration)
            
            # Verificar thresholds
            self._check_thresholds(stats)
            
            # Log da operação
            self._log_operation(stats)
    
    def track_llm_generation(self, model_name: str, provider: str):
        """Decorator para rastrear geração de LLM"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                with self.track_operation(
                    f"llm_generation_{provider}",
                    model_name=model_name,
                    provider=provider
                ) as stats:
                    
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    
                    # Coletar métricas específicas do LLM
                    response_time = end_time - start_time
                    
                    # Estimar tokens (simplificado)
                    prompt = kwargs.get('prompt', args[0] if args else '')
                    response = result if isinstance(result, str) else str(result)
                    
                    input_tokens = len(prompt.split()) * 1.3  # Estimativa
                    output_tokens = len(response.split()) * 1.3
                    
                    llm_metrics = self.metrics_collector.collect_llm_metrics(
                        model_name=model_name,
                        provider=provider,
                        response_time=response_time,
                        token_count_input=int(input_tokens),
                        token_count_output=int(output_tokens),
                        inference_time=response_time
                    )
                    
                    # Armazenar métricas
                    self.metrics_collector.store_metrics(vars(llm_metrics))
                    
                    stats.metadata = {
                        **stats.metadata,
                        'response_time': response_time,
                        'input_tokens': int(input_tokens),
                        'output_tokens': int(output_tokens)
                    }
                    
                    return result
            return wrapper
        return decorator
    
    def track_pdf_processing(self, file_name: str):
        """Decorator para rastrear processamento de PDF"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                with self.track_operation(
                    "pdf_processing",
                    file_name=file_name
                ) as stats:
                    
                    result = func(*args, **kwargs)
                    
                    # Extrair métricas do resultado
                    if isinstance(result, dict) and 'success' in result:
                        if result['success']:
                            analysis = result.get('analysis', {})
                            
                            pdf_metrics = self.metrics_collector.collect_pdf_metrics(
                                file_name=file_name,
                                file_size_mb=kwargs.get('file_size_mb', 0),
                                page_count=analysis.get('page_count', 0),
                                word_count=analysis.get('word_count', 0),
                                character_count=analysis.get('character_count', 0),
                                chunk_count=len(result.get('chunks', [])),
                                processing_time=stats.duration or 0,
                                extraction_time=stats.duration or 0
                            )
                            
                            # Armazenar métricas
                            self.metrics_collector.store_metrics(vars(pdf_metrics))
                            
                            stats.metadata = {
                                **stats.metadata,
                                'success': True,
                                'word_count': analysis.get('word_count', 0),
                                'page_count': analysis.get('page_count', 0)
                            }
                        else:
                            stats.metadata = {
                                **stats.metadata,
                                'success': False,
                                'error': result.get('error', 'Unknown error')
                            }
                    
                    return result
            return wrapper
        return decorator
    
    def _add_to_history(self, operation: str, duration: float):
        """Adiciona duração ao histórico"""
        if operation not in self.operation_history:
            self.operation_history[operation] = []
        
        self.operation_history[operation].append(duration)
        
        # Manter apenas últimas 50 medições
        if len(self.operation_history[operation]) > 50:
            self.operation_history[operation] = self.operation_history[operation][-50:]
    
    def _check_thresholds(self, stats: PerformanceStats):
        """Verifica se algum threshold foi ultrapassado"""
        
        if stats.duration and stats.duration > self.thresholds['response_time_threshold']:
            logger.warning(
                f"Operação {stats.operation} demorou {stats.duration:.2f}s "
                f"(threshold: {self.thresholds['response_time_threshold']}s)"
            )
        
        if stats.memory_end and stats.memory_start:
            memory_increase = stats.memory_end - stats.memory_start
            if memory_increase > 20:  # 20% de aumento
                logger.warning(
                    f"Operação {stats.operation} aumentou memória em {memory_increase:.1f}%"
                )
    
    def _log_operation(self, stats: PerformanceStats):
        """Log da operação concluída"""
        if stats.duration:
            logger.info(
                f"Operação {stats.operation} concluída em {stats.duration:.2f}s"
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance"""
        summary = {}
        
        for operation, durations in self.operation_history.items():
            if durations:
                summary[operation] = {
                    'count': len(durations),
                    'avg_duration': statistics.mean(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'median_duration': statistics.median(durations),
                    'last_duration': durations[-1]
                }
                
                # Calcular percentis se houver dados suficientes
                if len(durations) >= 5:
                    sorted_durations = sorted(durations)
                    summary[operation]['p95'] = sorted_durations[int(0.95 * len(sorted_durations))]
                    summary[operation]['p99'] = sorted_durations[int(0.99 * len(sorted_durations))]
        
        return summary
    
    def get_current_operations(self) -> Dict[str, Dict[str, Any]]:
        """Retorna operações atualmente em execução"""
        current = {}
        
        with self._lock:
            for op_id, stats in self.active_operations.items():
                current[op_id] = {
                    'operation': stats.operation,
                    'start_time': stats.start_time.isoformat(),
                    'duration_so_far': (datetime.now() - stats.start_time).total_seconds(),
                    'metadata': stats.metadata
                }
        
        return current
    
    def clear_history(self):
        """Limpa histórico de performance"""
        with self._lock:
            self.operation_history.clear()
            self.completed_operations.clear()
        logger.info("Histórico de performance limpo")

# Instância global
performance_tracker = PerformanceTracker()
