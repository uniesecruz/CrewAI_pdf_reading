# Guia de Configuração e Uso do Sistema de Monitoramento

## 📋 Visão Geral

Este sistema de monitoramento fornece observabilidade completa para o projeto LLM PDF Reading, incluindo:

- 📊 **Monitoramento em tempo real** de modelos LLM e operações
- 📈 **Rastreamento de experimentos** com MLflow
- ⚡ **Análise de performance** detalhada
- 🔧 **Métricas de sistema** (CPU, GPU, memória)
- 🚨 **Sistema de alertas** configurável
- 📱 **Dashboard web** interativo

## 🚀 Instalação e Configuração

### 1. Dependências Opcionais

```bash
# Para MLflow (recomendado)
pip install mlflow

# Para métricas de sistema
pip install psutil

# Para monitoramento de GPU
pip install GPUtil

# Para dashboard web
pip install streamlit plotly pandas

# Instalar tudo de uma vez
pip install mlflow psutil GPUtil streamlit plotly pandas
```

### 2. Configuração Inicial

```python
from llm_pdf_reading.monitoring import model_monitor, experiment_manager

# Iniciar monitoramento
model_monitor.start_monitoring()

# Configurar MLflow (opcional)
if experiment_manager.mlflow_available:
    run_id = experiment_manager.start_run(
        run_name="minha_sessao",
        tags={"project": "llm_pdf_reading"}
    )
```

## 📊 Uso Básico

### 1. Monitoramento Automático com Decoradores

**Aplicar ao `local_llm.py`:**

```python
from llm_pdf_reading.monitoring.decorators import monitor_llm_operation

class LocalLLMManager:
    
    @monitor_llm_operation(operation_name="ollama_generate")
    def generate_with_ollama(self, prompt: str, model_name: str = None) -> str:
        # Seu código existente - nada muda!
        # O decorator automaticamente:
        # - Mede tempo de execução
        # - Coleta métricas LLM
        # - Registra no MLflow
        # - Monitora performance
        return response
```

**Aplicar ao `orchestrator.py`:**

```python
from llm_pdf_reading.monitoring.decorators import (
    monitor_pdf_operation, 
    monitor_complete_operation
)

class PDFOrchestrator:
    
    @monitor_pdf_operation(operation_name="extract_text")
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        # Código existente inalterado
        return extracted_text

    @monitor_complete_operation(operation_name="full_pipeline")
    def process_pdf_and_answer(self, pdf_path: str, question: str) -> dict:
        # Monitora toda a operação end-to-end
        return result
```

### 2. Monitoramento Manual

```python
from llm_pdf_reading.monitoring import performance_tracker, model_monitor

# Monitorar operação específica
with performance_tracker.track_operation("minha_operacao"):
    # Sua operação aqui
    resultado = fazer_algo()

# Registrar requisição de modelo
model_monitor.record_request("llama2:7b")
```

## 📱 Dashboard Web

### Iniciar Dashboard

```bash
# Navegar para o diretório do projeto
cd pdf_reading/llm_pdf_reading/monitoring

# Executar dashboard
streamlit run dashboard.py
```

### Funcionalidades do Dashboard

- **📊 Visão Geral**: Status geral, métricas principais, gráficos em tempo real
- **🤖 Modelos**: Status individual de cada modelo, performance comparativa
- **⚡ Performance**: Análise detalhada de tempos de execução, percentis
- **📈 MLflow**: Gerenciamento de experimentos, comparação de modelos
- **🔧 Sistema**: Métricas de CPU, GPU, memória, disco

## 🔧 Configuração Avançada

### 1. Personalizar Configurações

```python
from llm_pdf_reading.monitoring.config import PERFORMANCE_CONFIG

# Modificar configurações
PERFORMANCE_CONFIG['ALERT_THRESHOLDS']['response_time'] = 10.0  # 10 segundos
PERFORMANCE_CONFIG['MONITORING_INTERVAL'] = 30  # 30 segundos
```

### 2. Callbacks de Alerta

```python
from llm_pdf_reading.monitoring import model_monitor

def alerta_customizado(model_name: str, response_time: float):
    print(f"⚠️ ALERTA: {model_name} demorou {response_time:.2f}s")
    # Enviar para Slack, Discord, email, etc.

model_monitor.add_alert_callback("high_response_time", alerta_customizado)
```

### 3. Exportar Dados

```python
from llm_pdf_reading.monitoring import model_monitor, experiment_manager
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Exportar dados de monitoramento
model_monitor.export_monitoring_data(f"monitoring_{timestamp}.json")

# Exportar dados do MLflow
experiment_manager.export_experiment_data(f"experiments_{timestamp}.csv")
```

## 📊 MLflow - Rastreamento de Experimentos

### 1. Configurar Servidor MLflow

```bash
# Instalar MLflow
pip install mlflow

# Iniciar servidor local
mlflow ui --port 5000

# Acessar: http://localhost:5000
```

### 2. Rastreamento Automático

Com os decoradores aplicados, todas as operações são automaticamente logadas no MLflow:

- **Parâmetros**: modelo, provider, configurações
- **Métricas**: tempo de resposta, tokens, qualidade
- **Artefatos**: prompts, respostas, arquivos processados

### 3. Comparar Modelos

```python
from llm_pdf_reading.monitoring import experiment_manager

# Comparar modelos por métrica
comparison = experiment_manager.compare_models(
    ["llama2:7b", "mistral:7b", "gpt-3.5-turbo"],
    metric="response_time"
)

# Encontrar melhor modelo
best_model = experiment_manager.get_best_model("tokens_per_second")
```

## 📈 Métricas Coletadas

### LLM Metrics
- Tempo de resposta
- Tokens de entrada/saída
- Tokens por segundo
- Taxa de erro
- Custo estimado

### PDF Metrics
- Tamanho do arquivo
- Número de páginas
- Tempo de processamento
- Método de extração
- Taxa de sucesso

### System Metrics
- CPU, GPU, Memória
- Disco, Rede
- Processos ativos
- Temperatura (se disponível)

### Quality Metrics
- Relevância da resposta
- Completude
- Acurácia
- Coerência

## 🚨 Sistema de Alertas

### Tipos de Alerta
- **Alto tempo de resposta** (>5s por padrão)
- **Baixa disponibilidade** (<95% por padrão)
- **Erro de modelo**
- **Alto uso de recursos** (>90% CPU/GPU)
- **Falha de operação**

### Configurar Alertas

```python
from llm_pdf_reading.monitoring import model_monitor

# Configurar thresholds personalizados
model_monitor.configure_alerts({
    'response_time_threshold': 3.0,  # 3 segundos
    'availability_threshold': 0.99,  # 99%
    'memory_threshold': 0.85  # 85%
})
```

## 🔄 Integração com Código Existente

### Método 1: Decoradores (Recomendado)

```python
# Adicione apenas 1 linha ao seu código existente
@monitor_llm_operation(operation_name="minha_funcao")
def minha_funcao_existente():
    # Todo o código permanece igual
    return resultado
```

### Método 2: Context Managers

```python
from llm_pdf_reading.monitoring import performance_tracker

def minha_funcao():
    with performance_tracker.track_operation("operacao_manual"):
        # Seu código aqui
        return resultado
```

### Método 3: Chamadas Manuais

```python
from llm_pdf_reading.monitoring import model_monitor, metrics_collector

# No início da operação
start_time = time.time()
model_monitor.record_request("meu_modelo")

# Sua operação
resultado = fazer_algo()

# No final
end_time = time.time()
metrics = metrics_collector.collect_llm_metrics(
    model_name="meu_modelo",
    response_time=end_time - start_time,
    # ... outras métricas
)
```

## 🛠️ Troubleshooting

### Problemas Comuns

1. **MLflow não disponível**:
   ```bash
   pip install mlflow
   ```

2. **Métricas de GPU não funcionam**:
   ```bash
   pip install GPUtil
   ```

3. **Dashboard não carrega**:
   ```bash
   pip install streamlit plotly pandas
   ```

4. **Permissões de arquivo**:
   - Verificar permissões de escrita na pasta `monitoring_data/`

### Logs e Debug

```python
from llm_pdf_reading.monitoring.config import PERFORMANCE_CONFIG

# Ativar logs detalhados
PERFORMANCE_CONFIG['DEBUG'] = True

# Verificar status
from llm_pdf_reading.monitoring import model_monitor
print(model_monitor.get_system_status())
```

## 📚 Exemplos Completos

Veja o arquivo `integration_examples.py` para exemplos detalhados de:
- Integração com código existente
- Configuração de alertas
- Uso manual do sistema
- Dashboard de linha de comando

## 🎯 Melhores Práticas

1. **Inicie o monitoramento** no início da aplicação
2. **Use decoradores** para integração simples
3. **Configure alertas** para métricas críticas
4. **Exporte dados** regularmente para análise
5. **Monitore recursos** do sistema constantemente
6. **Use tags no MLflow** para organizar experimentos
7. **Documente experimentos** com descrições claras

## 📞 Suporte

Para questões ou problemas:
1. Verifique os logs em `monitoring_data/logs/`
2. Consulte `integration_examples.py`
3. Execute `python integration_examples.py` para teste
4. Verifique configurações em `config.py`
