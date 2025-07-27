"""
Configurações para monitoramento e MLflow
"""
import os
from pathlib import Path

# Configurações MLflow
MLFLOW_CONFIG = {
    'tracking_uri': os.getenv('MLFLOW_TRACKING_URI', 'file:./mlruns'),
    'experiment_name': os.getenv('MLFLOW_EXPERIMENT_NAME', 'llm_pdf_reading'),
    'artifact_location': os.getenv('MLFLOW_ARTIFACT_LOCATION', './mlflow_artifacts'),
    'backend_store_uri': os.getenv('MLFLOW_BACKEND_STORE_URI', None),
    'default_artifact_root': os.getenv('MLFLOW_DEFAULT_ARTIFACT_ROOT', None)
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    'enable_monitoring': True,
    'log_level': 'INFO',
    'metrics_interval': 1.0,  # segundos
    'memory_threshold': 0.8,  # 80% da memória
    'response_time_threshold': 30.0,  # 30 segundos
    'batch_size_threshold': 100,
    'auto_log_models': True,
    'track_system_metrics': True
}

# Métricas a serem coletadas
METRICS_CONFIG = {
    'llm_metrics': [
        'response_time',
        'token_count_input',
        'token_count_output', 
        'model_load_time',
        'inference_time',
        'memory_usage',
        'gpu_utilization',
        'cost_estimation'
    ],
    'pdf_metrics': [
        'processing_time',
        'extraction_time',
        'file_size',
        'page_count',
        'word_count',
        'character_count',
        'chunk_count',
        'extraction_quality'
    ],
    'system_metrics': [
        'cpu_usage',
        'memory_usage',
        'disk_usage',
        'gpu_memory',
        'network_io'
    ],
    'quality_metrics': [
        'coherence_score',
        'relevance_score',
        'completeness_score',
        'accuracy_score',
        'user_satisfaction'
    ]
}

# Configurações de Experimentos
EXPERIMENT_CONFIG = {
    'auto_create_experiments': True,
    'experiment_tags': {
        'project': 'llm_pdf_reading',
        'version': '2.0',
        'framework': 'crewai'
    },
    'run_tags': {
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'user': os.getenv('USER', 'unknown')
    }
}

# Diretórios
MONITORING_DIRS = {
    'logs': Path('logs/monitoring'),
    'artifacts': Path('artifacts/models'),
    'metrics': Path('metrics'),
    'reports': Path('reports/monitoring'),
    'exports': Path('exports/metrics')
}

# Criar diretórios se não existirem
for dir_path in MONITORING_DIRS.values():
    dir_path.mkdir(parents=True, exist_ok=True)
