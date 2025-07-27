"""
Coletor de métricas para modelos LLM e processamento de PDF
"""
import time
import psutil
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import json

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

from .config import METRICS_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class LLMMetrics:
    """Métricas específicas para modelos LLM"""
    model_name: str
    provider: str  # 'ollama', 'huggingface', 'openai', etc.
    response_time: float
    token_count_input: int
    token_count_output: int
    model_load_time: Optional[float] = None
    inference_time: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    gpu_utilization: Optional[float] = None
    cost_estimation: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class PDFMetrics:
    """Métricas para processamento de PDF"""
    file_name: str
    file_size_mb: float
    page_count: int
    word_count: int
    character_count: int
    chunk_count: int
    processing_time: float
    extraction_time: float
    extraction_quality: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    gpu_memory: Optional[float] = None
    gpu_utilization: Optional[float] = None
    network_io: Optional[Dict[str, float]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class QualityMetrics:
    """Métricas de qualidade"""
    coherence_score: Optional[float] = None
    relevance_score: Optional[float] = None
    completeness_score: Optional[float] = None
    accuracy_score: Optional[float] = None
    user_satisfaction: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class MetricsCollector:
    """Coletor principal de métricas"""
    
    def __init__(self):
        self.enabled_metrics = METRICS_CONFIG
        self.metrics_history: List[Dict[str, Any]] = []
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            # CPU e Memória
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # GPU (se disponível)
            gpu_memory = None
            gpu_utilization = None
            if GPU_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Primeira GPU
                        gpu_memory = gpu.memoryUtil * 100
                        gpu_utilization = gpu.load * 100
                except Exception as e:
                    logger.debug(f"Erro ao coletar métricas GPU: {e}")
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            }
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                gpu_memory=gpu_memory,
                gpu_utilization=gpu_utilization,
                network_io=network_io
            )
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return SystemMetrics(cpu_usage=0, memory_usage=0, disk_usage=0)
    
    def collect_llm_metrics(
        self,
        model_name: str,
        provider: str,
        response_time: float,
        token_count_input: int,
        token_count_output: int,
        **kwargs
    ) -> LLMMetrics:
        """Coleta métricas específicas do LLM"""
        
        # Estimar custo (simplificado)
        cost_estimation = self._estimate_cost(
            provider, token_count_input, token_count_output
        )
        
        return LLMMetrics(
            model_name=model_name,
            provider=provider,
            response_time=response_time,
            token_count_input=token_count_input,
            token_count_output=token_count_output,
            cost_estimation=cost_estimation,
            **kwargs
        )
    
    def collect_pdf_metrics(
        self,
        file_name: str,
        file_size_mb: float,
        page_count: int,
        word_count: int,
        character_count: int,
        chunk_count: int,
        processing_time: float,
        extraction_time: float,
        **kwargs
    ) -> PDFMetrics:
        """Coleta métricas de processamento de PDF"""
        
        # Calcular qualidade da extração (simplificado)
        extraction_quality = self._calculate_extraction_quality(
            page_count, word_count, character_count
        )
        
        return PDFMetrics(
            file_name=file_name,
            file_size_mb=file_size_mb,
            page_count=page_count,
            word_count=word_count,
            character_count=character_count,
            chunk_count=chunk_count,
            processing_time=processing_time,
            extraction_time=extraction_time,
            extraction_quality=extraction_quality,
            **kwargs
        )
    
    def _estimate_cost(
        self, 
        provider: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> Optional[float]:
        """Estima custo baseado no provedor e tokens"""
        
        # Tabela de preços simplificada (USD por 1K tokens)
        pricing = {
            'openai': {
                'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
                'gpt-4': {'input': 0.03, 'output': 0.06}
            },
            'anthropic': {
                'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
                'claude-3-sonnet': {'input': 0.003, 'output': 0.015}
            },
            'ollama': {'input': 0, 'output': 0},  # Gratuito
            'huggingface': {'input': 0, 'output': 0}  # Gratuito
        }
        
        if provider in pricing:
            if provider in ['ollama', 'huggingface']:
                return 0.0
            
            # Para APIs comerciais, usar preço médio
            provider_pricing = pricing[provider]
            avg_input_price = sum(p['input'] for p in provider_pricing.values()) / len(provider_pricing)
            avg_output_price = sum(p['output'] for p in provider_pricing.values()) / len(provider_pricing)
            
            cost = (input_tokens / 1000 * avg_input_price) + (output_tokens / 1000 * avg_output_price)
            return round(cost, 6)
        
        return None
    
    def _calculate_extraction_quality(
        self, 
        page_count: int, 
        word_count: int, 
        character_count: int
    ) -> float:
        """Calcula score de qualidade da extração (simplificado)"""
        
        # Heurística simples: palavras por página
        if page_count == 0:
            return 0.0
        
        words_per_page = word_count / page_count
        
        # Assumir que 100-500 palavras por página é normal
        if 100 <= words_per_page <= 500:
            quality = 1.0
        elif words_per_page < 100:
            quality = words_per_page / 100
        else:
            quality = min(1.0, 500 / words_per_page)
        
        return round(quality, 2)
    
    def store_metrics(self, metrics_dict: Dict[str, Any]):
        """Armazena métricas no histórico"""
        metrics_dict['timestamp'] = datetime.now().isoformat()
        self.metrics_history.append(metrics_dict)
        
        # Manter apenas últimas 1000 métricas na memória
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas coletadas"""
        if not self.metrics_history:
            return {}
        
        # Calcular estatísticas básicas
        response_times = [m.get('response_time', 0) for m in self.metrics_history if 'response_time' in m]
        processing_times = [m.get('processing_time', 0) for m in self.metrics_history if 'processing_time' in m]
        
        summary = {
            'total_requests': len(self.metrics_history),
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'avg_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0,
            'last_update': self.metrics_history[-1].get('timestamp'),
            'metrics_count': len(self.metrics_history)
        }
        
        return summary
    
    def export_metrics(self, file_path: str):
        """Exporta métricas para arquivo JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.metrics_history, f, indent=2, default=str)
            logger.info(f"Métricas exportadas para: {file_path}")
        except Exception as e:
            logger.error(f"Erro ao exportar métricas: {e}")

# Instância global
metrics_collector = MetricsCollector()
