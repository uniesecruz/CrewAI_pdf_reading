"""
Sistema de monitoramento e observabilidade para LLM PDF Reading

Este módulo fornece ferramentas completas para:
- Monitoramento em tempo real de modelos LLM
- Rastreamento de experimentos com MLflow
- Análise de performance detalhada
- Coleta de métricas de sistema
- Dashboard interativo
- Sistema de alertas

Exemplo de uso básico:
    from llm_pdf_reading.monitoring import model_monitor
    
    # Iniciar monitoramento
    model_monitor.start_monitoring()
    
    # Usar decoradores para monitoramento automático
    from llm_pdf_reading.monitoring.decorators import monitor_llm_operation
    
    @monitor_llm_operation(operation_name="minha_operacao")
    def minha_funcao():
        return resultado

Configuração rápida:
    # Execute o script de configuração automática
    python llm_pdf_reading/monitoring/setup_monitoring.py
    
    # Ou manualmente:
    from llm_pdf_reading.monitoring.start_monitoring import start_monitoring
    start_monitoring()
"""

try:
    from .config import MLFLOW_CONFIG, PERFORMANCE_CONFIG, METRICS_CONFIG
    from .metrics_collector import MetricsCollector, SystemMetrics, LLMMetrics, PDFMetrics, QualityMetrics
    from .performance_tracker import PerformanceTracker
    from .experiment_manager import ExperimentManager
    from .model_monitor import ModelMonitor
    from .decorators import (
        monitor_llm_operation,
        monitor_pdf_operation, 
        monitor_qa_operation,
        monitor_complete_operation
    )
    
    # Lazy initialization para evitar problemas de import
    _instances = {}
    
    def get_metrics_collector():
        if 'metrics_collector' not in _instances:
            _instances['metrics_collector'] = MetricsCollector()
        return _instances['metrics_collector']
    
    def get_performance_tracker():
        if 'performance_tracker' not in _instances:
            _instances['performance_tracker'] = PerformanceTracker()
        return _instances['performance_tracker']
    
    def get_experiment_manager():
        if 'experiment_manager' not in _instances:
            _instances['experiment_manager'] = ExperimentManager()
        return _instances['experiment_manager']
    
    def get_model_monitor():
        if 'model_monitor' not in _instances:
            _instances['model_monitor'] = ModelMonitor()
        return _instances['model_monitor']
    
    # Criar instâncias globais de forma segura
    metrics_collector = get_metrics_collector()
    performance_tracker = get_performance_tracker()
    experiment_manager = get_experiment_manager()
    model_monitor = get_model_monitor()
    
    __all__ = [
        # Configurações
        'MLFLOW_CONFIG',
        'PERFORMANCE_CONFIG', 
        'METRICS_CONFIG',
        
        # Classes de métricas
        'SystemMetrics',
        'LLMMetrics',
        'PDFMetrics',
        'QualityMetrics',
        
        # Classes principais
        'MetricsCollector',
        'PerformanceTracker',
        'ExperimentManager',
        'ModelMonitor',
        
        # Instâncias globais
        'metrics_collector',
        'performance_tracker',
        'experiment_manager',
        'model_monitor',
        
        # Decoradores
        'monitor_llm_operation',
        'monitor_pdf_operation',
        'monitor_qa_operation',
        'monitor_complete_operation'
    ]

except ImportError as e:
    # Em caso de dependências faltando, fornecer versões básicas
    print(f"Aviso: Algumas funcionalidades de monitoramento podem estar limitadas - {e}")
    
    # Versões mínimas para compatibilidade
    class DummyMonitor:
        def start_monitoring(self): pass
        def stop_monitoring(self): pass
        def record_request(self, model_name): pass
        def get_system_status(self): return {}
        def get_real_time_metrics(self): return {}
    
    def dummy_decorator(operation_name=None):
        def decorator(func):
            return func
        return decorator
    
    # Criar instâncias dummy
    model_monitor = DummyMonitor()
    performance_tracker = DummyMonitor()
    experiment_manager = DummyMonitor()
    metrics_collector = DummyMonitor()
    
    # Decoradores dummy
    monitor_llm_operation = dummy_decorator
    monitor_pdf_operation = dummy_decorator
    monitor_qa_operation = dummy_decorator
    monitor_complete_operation = dummy_decorator
    
    __all__ = [
        'model_monitor',
        'performance_tracker',
        'experiment_manager', 
        'metrics_collector',
        'monitor_llm_operation',
        'monitor_pdf_operation',
        'monitor_qa_operation',
        'monitor_complete_operation'
    ]
