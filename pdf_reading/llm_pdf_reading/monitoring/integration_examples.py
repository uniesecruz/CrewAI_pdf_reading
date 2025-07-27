"""
Exemplo de integração dos decoradores com código existente
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Exemplo de como aplicar os decoradores aos códigos existentes

from llm_pdf_reading.monitoring.decorators import (
    monitor_llm_operation,
    monitor_pdf_operation,
    monitor_qa_operation,
    monitor_complete_operation
)

# ====================================================================
# EXEMPLO 1: Aplicação ao local_llm.py (LocalLLMManager)
# ====================================================================

"""
No arquivo llm_pdf_reading/local_llm.py, você pode aplicar os decoradores assim:

```python
from llm_pdf_reading.monitoring.decorators import monitor_llm_operation

class LocalLLMManager:
    
    @monitor_llm_operation(operation_name="ollama_generate")
    def generate_with_ollama(self, prompt: str, model_name: str = None) -> str:
        # Código existente permanece inalterado
        model = model_name or self.default_model
        
        # ... resto do código
        
        return response

    @monitor_llm_operation(operation_name="huggingface_generate")
    def generate_with_huggingface(self, prompt: str, model_name: str = None) -> str:
        # Código existente permanece inalterado
        
        # ... resto do código
        
        return response
```
"""

# ====================================================================
# EXEMPLO 2: Aplicação ao orchestrator.py
# ====================================================================

"""
No arquivo llm_pdf_reading/orchestrator.py, você pode aplicar os decoradores assim:

```python
from llm_pdf_reading.monitoring.decorators import (
    monitor_pdf_operation, 
    monitor_qa_operation,
    monitor_complete_operation
)

class PDFOrchestrator:
    
    @monitor_pdf_operation(operation_name="extract_text")
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        # Código existente permanece inalterado
        
        # ... resto do código
        
        return extracted_text

    @monitor_qa_operation(operation_name="answer_question")
    def answer_question(self, question: str, context: str) -> str:
        # Código existente permanece inalterado
        
        # ... resto do código
        
        return answer

    @monitor_complete_operation(operation_name="process_pdf_complete")
    def process_pdf_and_answer(self, pdf_path: str, question: str) -> Dict[str, Any]:
        # Este decorator monitora toda a operação completa
        
        # Código existente permanece inalterado
        
        # ... resto do código
        
        return result
```
"""

# ====================================================================
# EXEMPLO 3: Aplicação ao streamlit_app.py
# ====================================================================

"""
No arquivo streamlit_app.py, você pode aplicar monitoramento assim:

```python
from llm_pdf_reading.monitoring.decorators import monitor_complete_operation
from llm_pdf_reading.monitoring import model_monitor

# No início do app
if not model_monitor.is_monitoring:
    model_monitor.start_monitoring()

@monitor_complete_operation(operation_name="streamlit_pdf_processing")
def process_pdf_with_monitoring(pdf_file, question, model_name):
    # Sua função existente de processamento
    
    # ... código existente
    
    return result

# Nas suas funções do Streamlit:
def main():
    # ... código existente do Streamlit
    
    if st.button("Processar PDF"):
        with st.spinner("Processando..."):
            result = process_pdf_with_monitoring(
                uploaded_file, 
                user_question, 
                selected_model
            )
            
            # Exibir resultado
            st.success("Processamento concluído!")
            st.write(result)
```
"""

# ====================================================================
# EXEMPLO 4: Integração Manual (sem decoradores)
# ====================================================================

def example_manual_integration():
    """
    Exemplo de como usar o sistema de monitoramento manualmente
    """
    from llm_pdf_reading.monitoring import (
        performance_tracker,
        experiment_manager,
        metrics_collector,
        model_monitor
    )
    
    # Iniciar monitoramento se não estiver ativo
    if not model_monitor.is_monitoring:
        model_monitor.start_monitoring()
    
    # Exemplo 1: Monitoramento manual de operação LLM
    with performance_tracker.track_operation("manual_llm_operation"):
        # Simular operação LLM
        model_name = "llama2:7b"
        prompt = "Qual é o conteúdo do PDF?"
        
        # Registrar início da requisição
        model_monitor.record_request(model_name)
        
        # Sua operação LLM aqui
        response = "Esta é uma resposta simulada"
        
        # Coletar métricas LLM
        llm_metrics = metrics_collector.collect_llm_metrics(
            model_name=model_name,
            provider="ollama",
            prompt_length=len(prompt),
            response_length=len(response),
            response_time=1.5,
            input_tokens=20,
            output_tokens=30
        )
        
        # Log no MLflow (se disponível)
        if experiment_manager.mlflow_available:
            experiment_manager.log_llm_experiment(
                model_name=model_name,
                provider="ollama",
                prompt=prompt,
                response=response,
                metrics=llm_metrics
            )
    
    # Exemplo 2: Monitoramento de processamento PDF
    with performance_tracker.track_operation("manual_pdf_operation"):
        pdf_path = "example.pdf"
        
        # Coletar métricas PDF
        pdf_metrics = metrics_collector.collect_pdf_metrics(
            file_path=pdf_path,
            file_size=1024*1024,  # 1MB
            num_pages=10,
            processing_time=2.0,
            extraction_method="pymupdf"
        )
        
        # Log no MLflow (se disponível)
        if experiment_manager.mlflow_available:
            experiment_manager.log_pdf_experiment(
                file_path=pdf_path,
                metrics=pdf_metrics
            )

# ====================================================================
# EXEMPLO 5: Configuração Inicial
# ====================================================================

def setup_monitoring():
    """
    Função para configurar o monitoramento inicialmente
    """
    from llm_pdf_reading.monitoring import (
        model_monitor,
        experiment_manager
    )
    
    # Configurar callbacks de alerta (opcional)
    def on_high_response_time(model_name: str, response_time: float):
        print(f"⚠️ ALERTA: {model_name} com tempo alto: {response_time:.2f}s")
    
    def on_model_error(model_name: str, error: str):
        print(f"❌ ERRO: {model_name} - {error}")
    
    def on_low_availability(model_name: str, availability: float):
        print(f"📉 DISPONIBILIDADE BAIXA: {model_name} - {availability:.1%}")
    
    # Registrar callbacks
    model_monitor.add_alert_callback("high_response_time", on_high_response_time)
    model_monitor.add_alert_callback("model_error", on_model_error)
    model_monitor.add_alert_callback("low_availability", on_low_availability)
    
    # Iniciar monitoramento
    model_monitor.start_monitoring()
    
    # Configurar experimento MLflow (se disponível)
    if experiment_manager.mlflow_available:
        run_id = experiment_manager.start_run(
            run_name="pdf_reading_session",
            tags={
                "project": "llm_pdf_reading",
                "environment": "development"
            }
        )
        print(f"📊 MLflow run iniciado: {run_id}")
    
    print("✅ Monitoramento configurado e iniciado!")

# ====================================================================
# EXEMPLO 6: Dashboard de Linha de Comando
# ====================================================================

def show_monitoring_status():
    """
    Função para mostrar status do monitoramento no terminal
    """
    from llm_pdf_reading.monitoring import model_monitor
    
    print("\n" + "="*50)
    print("🔍 STATUS DO MONITORAMENTO")
    print("="*50)
    
    status = model_monitor.get_system_status()
    
    print(f"Status: {'🟢 Ativo' if status['monitoring_active'] else '🔴 Inativo'}")
    print(f"Uptime: {status['uptime_formatted']}")
    print(f"Disponibilidade: {status['availability']:.1%}")
    print(f"Tempo médio de resposta: {status['avg_response_time']:.2f}s")
    print(f"Total de requisições: {status['total_requests']}")
    
    # Status dos modelos
    real_time_data = model_monitor.get_real_time_metrics()
    model_states = real_time_data['model_states']
    
    if model_states:
        print("\n📊 MODELOS:")
        for name, state in model_states.items():
            status_icon = "🟢" if state['status'] == 'active' else "🔴"
            print(f"  {status_icon} {name}: {state['total_requests']} req, {state['avg_response_time']:.2f}s avg")
    
    # Operações em andamento
    current_operations = real_time_data['current_operations']
    if current_operations:
        print("\n⏳ OPERAÇÕES EM ANDAMENTO:")
        for op_id, op_data in current_operations.items():
            print(f"  🔄 {op_data['operation']}: {op_data['duration_so_far']:.2f}s")
    
    print("="*50)

if __name__ == "__main__":
    # Exemplo de uso
    print("🚀 Configurando monitoramento...")
    setup_monitoring()
    
    print("\n📊 Executando exemplo manual...")
    example_manual_integration()
    
    print("\n📈 Status atual:")
    show_monitoring_status()
