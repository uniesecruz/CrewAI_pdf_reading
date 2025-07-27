"""
Monitor de modelos em tempo real
"""
import time
import threading
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from collections import deque
import json

from .metrics_collector import MetricsCollector, metrics_collector
from .performance_tracker import PerformanceTracker, performance_tracker
from .config import PERFORMANCE_CONFIG

logger = logging.getLogger(__name__)

class ModelMonitor:
    """Monitor de modelos em tempo real"""
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        performance_tracker: Optional[PerformanceTracker] = None
    ):
        # Importar e criar dependências se não fornecidas
        if metrics_collector is None:
            from .metrics_collector import MetricsCollector
            metrics_collector = MetricsCollector()
        
        if performance_tracker is None:
            from .performance_tracker import PerformanceTracker
            performance_tracker = PerformanceTracker(metrics_collector)
        
        self.metrics_collector = metrics_collector
        self.performance_tracker = performance_tracker
        
        # Estado do monitor
        self.is_monitoring = False
        self.monitor_thread = None
        self.monitoring_interval = PERFORMANCE_CONFIG.get('metrics_interval', 1.0)
        
        # Alertas e thresholds
        self.alert_callbacks: List[Callable] = []
        self.thresholds = {
            'response_time_threshold': PERFORMANCE_CONFIG.get('response_time_threshold', 30.0),
            'memory_threshold': PERFORMANCE_CONFIG.get('memory_threshold', 0.8),
            'error_rate_threshold': 0.1,  # 10%
            'availability_threshold': 0.95  # 95%
        }
        
        # Buffers para dados em tempo real
        self.response_times = deque(maxlen=100)
        self.error_counts = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        
        # Estatísticas
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'current_memory_usage': 0.0,
            'uptime_start': datetime.now(),
            'last_error': None
        }
        
        # Estados dos modelos
        self.model_states: Dict[str, Dict[str, Any]] = {}
    
    def start_monitoring(self):
        """Inicia o monitoramento em tempo real"""
        if self.is_monitoring:
            logger.warning("Monitoramento já está ativo")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoramento parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.is_monitoring:
            try:
                # Coletar métricas do sistema
                system_metrics = self.metrics_collector.collect_system_metrics()
                self.memory_usage.append(system_metrics.memory_usage)
                
                # Atualizar estatísticas
                self._update_stats(system_metrics)
                
                # Verificar alertas
                self._check_alerts(system_metrics)
                
                # Verificar estado dos modelos
                self._check_model_health()
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
            
            time.sleep(self.monitoring_interval)
    
    def _update_stats(self, system_metrics):
        """Atualiza estatísticas internas"""
        self.stats['current_memory_usage'] = system_metrics.memory_usage
        
        # Calcular média de tempo de resposta
        if self.response_times:
            self.stats['avg_response_time'] = sum(self.response_times) / len(self.response_times)
        
        # Calcular uptime
        uptime = datetime.now() - self.stats['uptime_start']
        self.stats['uptime_seconds'] = uptime.total_seconds()
    
    def _check_alerts(self, system_metrics):
        """Verifica condições de alerta"""
        alerts = []
        
        # Alerta de memória
        if system_metrics.memory_usage > self.thresholds['memory_threshold'] * 100:
            alerts.append({
                'type': 'memory_high',
                'message': f"Uso de memória alto: {system_metrics.memory_usage:.1f}%",
                'severity': 'warning',
                'threshold': self.thresholds['memory_threshold'] * 100
            })
        
        # Alerta de tempo de resposta
        if self.response_times and self.stats['avg_response_time'] > self.thresholds['response_time_threshold']:
            alerts.append({
                'type': 'response_time_high',
                'message': f"Tempo de resposta alto: {self.stats['avg_response_time']:.2f}s",
                'severity': 'warning',
                'threshold': self.thresholds['response_time_threshold']
            })
        
        # Alerta de taxa de erro
        if self.stats['total_requests'] > 0:
            error_rate = self.stats['failed_requests'] / self.stats['total_requests']
            if error_rate > self.thresholds['error_rate_threshold']:
                alerts.append({
                    'type': 'error_rate_high',
                    'message': f"Taxa de erro alta: {error_rate:.1%}",
                    'severity': 'critical',
                    'threshold': self.thresholds['error_rate_threshold']
                })
        
        # Disparar callbacks de alerta
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _check_model_health(self):
        """Verifica saúde dos modelos"""
        for model_id, state in self.model_states.items():
            last_activity = state.get('last_activity')
            if last_activity:
                time_since_activity = datetime.now() - last_activity
                
                # Marcar como inativo se não usado por 5 minutos
                if time_since_activity > timedelta(minutes=5):
                    state['status'] = 'inactive'
                else:
                    state['status'] = 'active'
    
    def _trigger_alert(self, alert: Dict[str, Any]):
        """Dispara alertas para callbacks registrados"""
        alert['timestamp'] = datetime.now()
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Erro ao executar callback de alerta: {e}")
        
        # Log do alerta
        severity = alert.get('severity', 'info')
        message = alert.get('message', 'Alerta desconhecido')
        
        if severity == 'critical':
            logger.error(f"ALERTA CRÍTICO: {message}")
        elif severity == 'warning':
            logger.warning(f"ALERTA: {message}")
        else:
            logger.info(f"INFO: {message}")
    
    def register_alert_callback(self, callback: Callable):
        """Registra callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def record_request(self, success: bool, response_time: float, model_name: Optional[str] = None):
        """Registra uma requisição"""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
            self.response_times.append(response_time)
        else:
            self.stats['failed_requests'] += 1
            self.error_counts.append(1)
            self.stats['last_error'] = datetime.now()
        
        # Atualizar estado do modelo
        if model_name:
            self._update_model_state(model_name, success, response_time)
    
    def _update_model_state(self, model_name: str, success: bool, response_time: float):
        """Atualiza estado de um modelo específico"""
        if model_name not in self.model_states:
            self.model_states[model_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time': 0.0,
                'last_activity': None,
                'status': 'unknown',
                'response_times': deque(maxlen=50)
            }
        
        state = self.model_states[model_name]
        state['total_requests'] += 1
        state['last_activity'] = datetime.now()
        
        if success:
            state['successful_requests'] += 1
            state['response_times'].append(response_time)
            
            # Recalcular média
            if state['response_times']:
                state['avg_response_time'] = sum(state['response_times']) / len(state['response_times'])
        else:
            state['failed_requests'] += 1
    
    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Retorna status de um modelo específico"""
        if model_name not in self.model_states:
            return {'status': 'unknown', 'message': 'Modelo não encontrado'}
        
        state = self.model_states[model_name]
        
        # Calcular métricas
        total = state['total_requests']
        success_rate = state['successful_requests'] / total if total > 0 else 0
        
        return {
            'status': state['status'],
            'total_requests': total,
            'success_rate': success_rate,
            'avg_response_time': state['avg_response_time'],
            'last_activity': state['last_activity'],
            'is_healthy': success_rate > 0.9 and state['avg_response_time'] < self.thresholds['response_time_threshold']
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status geral do sistema"""
        # Calcular availability
        total = self.stats['total_requests']
        availability = self.stats['successful_requests'] / total if total > 0 else 1.0
        
        # Calcular uptime
        uptime = datetime.now() - self.stats['uptime_start']
        
        return {
            'monitoring_active': self.is_monitoring,
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': str(uptime).split('.')[0],  # Remove microseconds
            'total_requests': total,
            'availability': availability,
            'avg_response_time': self.stats['avg_response_time'],
            'current_memory_usage': self.stats['current_memory_usage'],
            'active_models': len([m for m in self.model_states.values() if m.get('status') == 'active']),
            'last_error': self.stats['last_error'],
            'health_status': 'healthy' if availability > self.thresholds['availability_threshold'] else 'degraded'
        }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Retorna métricas em tempo real"""
        return {
            'timestamp': datetime.now().isoformat(),
            'response_times': list(self.response_times),
            'memory_usage': list(self.memory_usage),
            'error_counts': list(self.error_counts),
            'current_operations': self.performance_tracker.get_current_operations(),
            'model_states': {
                name: {
                    'status': state['status'],
                    'total_requests': state['total_requests'],
                    'avg_response_time': state['avg_response_time'],
                    'last_activity': state['last_activity'].isoformat() if state['last_activity'] else None
                }
                for name, state in self.model_states.items()
            }
        }
    
    def reset_stats(self):
        """Reseta estatísticas"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'current_memory_usage': 0.0,
            'uptime_start': datetime.now(),
            'last_error': None
        }
        
        self.response_times.clear()
        self.error_counts.clear()
        self.memory_usage.clear()
        self.model_states.clear()
        
        logger.info("Estatísticas de monitoramento resetadas")
    
    def export_monitoring_data(self, file_path: str):
        """Exporta dados de monitoramento"""
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'system_status': self.get_system_status(),
            'model_states': self.model_states,
            'performance_summary': self.performance_tracker.get_performance_summary(),
            'metrics_summary': self.metrics_collector.get_metrics_summary()
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Dados de monitoramento exportados para: {file_path}")
        except Exception as e:
            logger.error(f"Erro ao exportar dados de monitoramento: {e}")

# Instância global
model_monitor = ModelMonitor()

# Callback de exemplo para alertas
def default_alert_handler(alert: Dict[str, Any]):
    """Handler padrão para alertas"""
    print(f"🚨 ALERTA [{alert['severity'].upper()}]: {alert['message']}")

# Registrar handler padrão
model_monitor.register_alert_callback(default_alert_handler)
