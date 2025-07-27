"""
Decoradores para integração automática de monitoramento
"""
import functools
import time
import logging
from typing import Callable, Any, Optional

from .performance_tracker import performance_tracker
from .model_monitor import model_monitor
from .experiment_manager import experiment_manager

logger = logging.getLogger(__name__)

def monitor_llm_operation(
    model_name: str,
    provider: str,
    track_mlflow: bool = True,
    monitor_performance: bool = True
):
    """
    Decorator para monitorar operações de LLM automaticamente
    
    Args:
        model_name: Nome do modelo
        provider: Provedor (ollama, huggingface, openai, etc.)
        track_mlflow: Se deve logar no MLflow
        monitor_performance: Se deve monitorar performance
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = False
            result = None
            error = None
            
            try:
                # Executar função original
                result = func(*args, **kwargs)
                success = True
                return result
                
            except Exception as e:
                error = e
                logger.error(f"Erro em operação LLM {model_name}: {e}")
                raise
                
            finally:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Registrar no monitor
                if monitor_performance:
                    model_monitor.record_request(
                        success=success,
                        response_time=response_time,
                        model_name=f"{provider}:{model_name}"
                    )
                
                # Log no MLflow se solicitado
                if track_mlflow and success and result:
                    try:
                        # Extrair informações da resposta
                        prompt = kwargs.get('prompt', args[0] if args else '')
                        response = result if isinstance(result, str) else str(result)
                        
                        # Estimar tokens
                        input_tokens = len(prompt.split()) * 1.3
                        output_tokens = len(response.split()) * 1.3
                        
                        # Parâmetros do modelo
                        model_params = {
                            'temperature': kwargs.get('temperature', 0.7),
                            'max_length': kwargs.get('max_length', 1024),
                            'top_p': kwargs.get('top_p', 0.9)
                        }
                        
                        # Métricas de performance
                        performance_metrics = {
                            'response_time': response_time,
                            'input_tokens': int(input_tokens),
                            'output_tokens': int(output_tokens),
                            'tokens_per_second': int(output_tokens) / response_time if response_time > 0 else 0
                        }
                        
                        # Iniciar run se não houver um ativo
                        if not experiment_manager.current_run:
                            experiment_manager.start_run(
                                run_name=f"llm_{provider}_{model_name}_{int(time.time())}",
                                tags={'operation_type': 'llm_generation', 'auto_tracked': 'true'}
                            )
                        
                        # Log do experimento
                        experiment_manager.log_llm_experiment(
                            model_name=model_name,
                            provider=provider,
                            model_params=model_params,
                            performance_metrics=performance_metrics
                        )
                        
                    except Exception as e:
                        logger.error(f"Erro ao logar experimento LLM: {e}")
        
        return wrapper
    return decorator

def monitor_pdf_operation(
    track_mlflow: bool = True,
    monitor_performance: bool = True
):
    """
    Decorator para monitorar operações de processamento de PDF
    
    Args:
        track_mlflow: Se deve logar no MLflow
        monitor_performance: Se deve monitorar performance
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = False
            result = None
            file_path = args[0] if args else kwargs.get('pdf_path', 'unknown')
            
            try:
                # Executar função original com tracking de performance
                if monitor_performance:
                    with performance_tracker.track_operation(
                        "pdf_processing",
                        file_path=file_path
                    ) as stats:
                        result = func(*args, **kwargs)
                        success = result.get('success', False) if isinstance(result, dict) else True
                else:
                    result = func(*args, **kwargs)
                    success = result.get('success', False) if isinstance(result, dict) else True
                
                return result
                
            except Exception as e:
                logger.error(f"Erro em processamento PDF {file_path}: {e}")
                raise
                
            finally:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Log no MLflow se solicitado e bem-sucedido
                if track_mlflow and success and isinstance(result, dict):
                    try:
                        # Extrair informações do resultado
                        analysis = result.get('analysis', {})
                        
                        file_info = {
                            'file_name': file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1],
                            'file_size_mb': kwargs.get('file_size_mb', 0),
                            'page_count': analysis.get('page_count', 0)
                        }
                        
                        processing_metrics = {
                            'processing_time': processing_time,
                            'word_count': analysis.get('word_count', 0),
                            'character_count': analysis.get('character_count', 0),
                            'chunk_count': len(result.get('chunks', [])),
                            'extraction_time': processing_time  # Simplificado
                        }
                        
                        extraction_config = {
                            'chunk_size': kwargs.get('chunk_size', 1000),
                            'chunk_overlap': kwargs.get('chunk_overlap', 200)
                        }
                        
                        # Iniciar run se não houver um ativo
                        if not experiment_manager.current_run:
                            experiment_manager.start_run(
                                run_name=f"pdf_{file_info['file_name']}_{int(time.time())}",
                                tags={'operation_type': 'pdf_processing', 'auto_tracked': 'true'}
                            )
                        
                        # Log do experimento
                        experiment_manager.log_pdf_experiment(
                            file_info=file_info,
                            processing_metrics=processing_metrics,
                            extraction_config=extraction_config
                        )
                        
                    except Exception as e:
                        logger.error(f"Erro ao logar experimento PDF: {e}")
        
        return wrapper
    return decorator

def monitor_qa_operation(
    track_mlflow: bool = True,
    monitor_performance: bool = True
):
    """
    Decorator para monitorar operações de Q&A
    
    Args:
        track_mlflow: Se deve logar no MLflow
        monitor_performance: Se deve monitorar performance
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = False
            result = None
            
            # Extrair pergunta dos argumentos
            question = kwargs.get('question', args[1] if len(args) > 1 else 'unknown')
            
            try:
                # Executar função original
                if monitor_performance:
                    with performance_tracker.track_operation(
                        "qa_operation",
                        question_length=len(question)
                    ) as stats:
                        result = func(*args, **kwargs)
                        success = bool(result and len(str(result)) > 0)
                else:
                    result = func(*args, **kwargs)
                    success = bool(result and len(str(result)) > 0)
                
                return result
                
            except Exception as e:
                logger.error(f"Erro em operação Q&A: {e}")
                raise
                
            finally:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Registrar no monitor
                if monitor_performance:
                    model_monitor.record_request(
                        success=success,
                        response_time=response_time,
                        model_name="qa_system"
                    )
                
                # Log no MLflow se solicitado
                if track_mlflow and success and result:
                    try:
                        # Extrair contexto dos argumentos
                        context = args[0] if args else kwargs.get('pdf_content', '')
                        answer = str(result)
                        
                        context_info = {
                            'context_size': len(context),
                            'chunk_count': context.count('\n\n') + 1  # Estimativa simples
                        }
                        
                        performance_metrics = {
                            'response_time': response_time,
                            'question_length': len(question),
                            'answer_length': len(answer),
                            'context_processing_ratio': len(answer) / len(context) if context else 0
                        }
                        
                        # Iniciar run se não houver um ativo
                        if not experiment_manager.current_run:
                            experiment_manager.start_run(
                                run_name=f"qa_{int(time.time())}",
                                tags={'operation_type': 'qa', 'auto_tracked': 'true'}
                            )
                        
                        # Log do experimento
                        experiment_manager.log_qa_experiment(
                            question=question,
                            answer=answer,
                            context_info=context_info,
                            performance_metrics=performance_metrics
                        )
                        
                    except Exception as e:
                        logger.error(f"Erro ao logar experimento Q&A: {e}")
        
        return wrapper
    return decorator

# Decorator combinado para operações completas
def monitor_complete_operation(
    operation_type: str = "complete",
    track_mlflow: bool = True,
    monitor_performance: bool = True,
    auto_end_run: bool = True
):
    """
    Decorator para monitorar operações completas (PDF + LLM + Q&A)
    
    Args:
        operation_type: Tipo da operação
        track_mlflow: Se deve logar no MLflow
        monitor_performance: Se deve monitorar performance
        auto_end_run: Se deve finalizar run automaticamente
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Iniciar run MLflow se necessário
            run_started = False
            if track_mlflow and not experiment_manager.current_run:
                experiment_manager.start_run(
                    run_name=f"{operation_type}_{int(time.time())}",
                    tags={'operation_type': operation_type, 'auto_tracked': 'true'}
                )
                run_started = True
            
            try:
                # Executar função original
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                logger.error(f"Erro em operação completa {operation_type}: {e}")
                raise
                
            finally:
                # Finalizar run se foi iniciado por este decorator
                if track_mlflow and run_started and auto_end_run:
                    experiment_manager.end_run()
        
        return wrapper
    return decorator
