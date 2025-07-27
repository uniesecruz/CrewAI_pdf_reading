"""
Gerenciador de experimentos MLflow
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None

from .config import MLFLOW_CONFIG, EXPERIMENT_CONFIG
from .metrics_collector import MetricsCollector, metrics_collector

logger = logging.getLogger(__name__)

class ExperimentManager:
    """Gerenciador de experimentos MLflow para modelos LLM"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        # Importar e criar MetricsCollector se não fornecido
        if metrics_collector is None:
            from .metrics_collector import MetricsCollector
            metrics_collector = MetricsCollector()
        
        self.metrics_collector = metrics_collector
        self.mlflow_available = MLFLOW_AVAILABLE
        self.current_run = None
        self.experiment_id = None
        
        if self.mlflow_available:
            self._setup_mlflow()
        else:
            logger.warning("MLflow não disponível. Instale com: pip install mlflow")
    
    def _setup_mlflow(self):
        """Configura MLflow"""
        try:
            # Configurar tracking URI
            mlflow.set_tracking_uri(MLFLOW_CONFIG['tracking_uri'])
            
            # Criar ou obter experimento
            experiment_name = MLFLOW_CONFIG['experiment_name']
            
            try:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if experiment is None:
                    self.experiment_id = mlflow.create_experiment(
                        experiment_name,
                        artifact_location=MLFLOW_CONFIG.get('artifact_location'),
                        tags=EXPERIMENT_CONFIG['experiment_tags']
                    )
                    logger.info(f"Experimento criado: {experiment_name}")
                else:
                    self.experiment_id = experiment.experiment_id
                    logger.info(f"Usando experimento existente: {experiment_name}")
                    
            except Exception as e:
                logger.error(f"Erro ao configurar experimento: {e}")
                self.experiment_id = None
                
        except Exception as e:
            logger.error(f"Erro ao configurar MLflow: {e}")
            self.mlflow_available = False
    
    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Inicia uma nova execução MLflow"""
        if not self.mlflow_available or self.experiment_id is None:
            return None
        
        try:
            # Combinar tags padrão com tags personalizadas
            all_tags = {**EXPERIMENT_CONFIG['run_tags']}
            if tags:
                all_tags.update(tags)
            
            # Adicionar timestamp
            if run_name is None:
                run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_run = mlflow.start_run(
                experiment_id=self.experiment_id,
                run_name=run_name,
                tags=all_tags
            )
            
            logger.info(f"Execução MLflow iniciada: {run_name}")
            return self.current_run.info.run_id
            
        except Exception as e:
            logger.error(f"Erro ao iniciar execução MLflow: {e}")
            return None
    
    def end_run(self):
        """Finaliza a execução atual"""
        if self.mlflow_available and self.current_run:
            try:
                mlflow.end_run()
                logger.info("Execução MLflow finalizada")
                self.current_run = None
            except Exception as e:
                logger.error(f"Erro ao finalizar execução: {e}")
    
    def log_llm_experiment(
        self,
        model_name: str,
        provider: str,
        model_params: Dict[str, Any],
        performance_metrics: Dict[str, float],
        artifacts: Optional[Dict[str, str]] = None
    ):
        """Log de experimento específico para LLM"""
        if not self.mlflow_available:
            return
        
        try:
            # Log de parâmetros do modelo
            mlflow.log_params({
                'model_name': model_name,
                'provider': provider,
                **model_params
            })
            
            # Log de métricas de performance
            mlflow.log_metrics(performance_metrics)
            
            # Log de artefatos (se fornecidos)
            if artifacts:
                for name, path in artifacts.items():
                    if os.path.exists(path):
                        mlflow.log_artifact(path, name)
            
            # Log de métricas do sistema
            system_metrics = self.metrics_collector.collect_system_metrics()
            mlflow.log_metrics({
                'system_cpu_usage': system_metrics.cpu_usage,
                'system_memory_usage': system_metrics.memory_usage,
                'system_disk_usage': system_metrics.disk_usage
            })
            
            if system_metrics.gpu_utilization:
                mlflow.log_metric('system_gpu_utilization', system_metrics.gpu_utilization)
            
            logger.info(f"Experimento LLM logado: {model_name} ({provider})")
            
        except Exception as e:
            logger.error(f"Erro ao logar experimento LLM: {e}")
    
    def log_pdf_experiment(
        self,
        file_info: Dict[str, Any],
        processing_metrics: Dict[str, float],
        extraction_config: Dict[str, Any],
        quality_metrics: Optional[Dict[str, float]] = None
    ):
        """Log de experimento para processamento de PDF"""
        if not self.mlflow_available:
            return
        
        try:
            # Log de parâmetros do arquivo e configuração
            mlflow.log_params({
                'file_name': file_info.get('file_name', 'unknown'),
                'file_size_mb': file_info.get('file_size_mb', 0),
                'page_count': file_info.get('page_count', 0),
                **extraction_config
            })
            
            # Log de métricas de processamento
            mlflow.log_metrics(processing_metrics)
            
            # Log de métricas de qualidade (se disponíveis)
            if quality_metrics:
                mlflow.log_metrics(quality_metrics)
            
            logger.info(f"Experimento PDF logado: {file_info.get('file_name', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Erro ao logar experimento PDF: {e}")
    
    def log_qa_experiment(
        self,
        question: str,
        answer: str,
        context_info: Dict[str, Any],
        performance_metrics: Dict[str, float],
        quality_scores: Optional[Dict[str, float]] = None
    ):
        """Log de experimento para Q&A"""
        if not self.mlflow_available:
            return
        
        try:
            # Log de parâmetros
            mlflow.log_params({
                'question_length': len(question),
                'answer_length': len(answer),
                'context_chunks': context_info.get('chunk_count', 0),
                'context_size': context_info.get('context_size', 0)
            })
            
            # Log de métricas de performance
            mlflow.log_metrics(performance_metrics)
            
            # Log de scores de qualidade (se disponíveis)
            if quality_scores:
                mlflow.log_metrics(quality_scores)
            
            # Log de texto como artefato
            qa_data = {
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            }
            
            temp_file = f"temp_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(qa_data, f, indent=2, ensure_ascii=False)
            
            mlflow.log_artifact(temp_file, "qa_data")
            
            # Limpar arquivo temporário
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            logger.info("Experimento Q&A logado")
            
        except Exception as e:
            logger.error(f"Erro ao logar experimento Q&A: {e}")
    
    def compare_models(self, model_names: List[str], metric_name: str = 'response_time') -> Dict[str, Any]:
        """Compara performance de diferentes modelos"""
        if not self.mlflow_available:
            return {}
        
        try:
            # Buscar runs do experimento atual
            runs = mlflow.search_runs(
                experiment_ids=[self.experiment_id],
                filter_string=f"params.model_name IN {tuple(model_names)}",
                order_by=[f"metrics.{metric_name} ASC"]
            )
            
            comparison = {}
            for _, run in runs.iterrows():
                model_name = run.get(f'params.model_name')
                if model_name:
                    comparison[model_name] = {
                        'run_id': run['run_id'],
                        metric_name: run.get(f'metrics.{metric_name}'),
                        'start_time': run['start_time'],
                        'status': run['status']
                    }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Erro ao comparar modelos: {e}")
            return {}
    
    def get_best_model(self, metric_name: str = 'response_time', ascending: bool = True) -> Optional[Dict[str, Any]]:
        """Retorna o melhor modelo baseado em uma métrica"""
        if not self.mlflow_available:
            return None
        
        try:
            order = "ASC" if ascending else "DESC"
            runs = mlflow.search_runs(
                experiment_ids=[self.experiment_id],
                order_by=[f"metrics.{metric_name} {order}"],
                max_results=1
            )
            
            if not runs.empty:
                best_run = runs.iloc[0]
                return {
                    'run_id': best_run['run_id'],
                    'model_name': best_run.get('params.model_name'),
                    'provider': best_run.get('params.provider'),
                    metric_name: best_run.get(f'metrics.{metric_name}'),
                    'start_time': best_run['start_time']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar melhor modelo: {e}")
            return None
    
    def export_experiment_data(self, output_path: str):
        """Exporta dados do experimento para arquivo"""
        if not self.mlflow_available:
            return
        
        try:
            runs = mlflow.search_runs(experiment_ids=[self.experiment_id])
            runs.to_csv(output_path, index=False)
            logger.info(f"Dados do experimento exportados para: {output_path}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar dados do experimento: {e}")
    
    def cleanup_old_runs(self, days_to_keep: int = 30):
        """Remove execuções antigas"""
        if not self.mlflow_available:
            return
        
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            runs = mlflow.search_runs(experiment_ids=[self.experiment_id])
            
            for _, run in runs.iterrows():
                run_date = run['start_time'].timestamp()
                if run_date < cutoff_date:
                    mlflow.delete_run(run['run_id'])
                    logger.info(f"Execução removida: {run['run_id']}")
            
        except Exception as e:
            logger.error(f"Erro ao limpar execuções antigas: {e}")

# Instância global
experiment_manager = ExperimentManager()
