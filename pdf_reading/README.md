# 🤖 LLM PDF Reading - Análise Inteligente de PDFs

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>
<img src="https://img.shields.io/badge/Python-3.12+-blue.svg" />
<img src="https://img.shields.io/badge/License-MIT-green.svg" />
<img src="https://img.shields.io/badge/Streamlit-1.47+-red.svg" />

Este projeto desenvolve uma solução de **Large Language Model (LLM)** projetada para extração, análise e sumarização eficiente e inteligente de conteúdo de documentos PDF. O objetivo principal é transformar informações estáticas de PDFs em insights dinâmicos e acionáveis, reduzindo significativamente o esforço manual tipicamente envolvido no processamento desses documentos.

## ✨ Funcionalidades

- 📄 **Extração Inteligente de PDF**: Suporte para múltiplas bibliotecas (PyMuPDF, PyPDF2, pdfplumber)
- 🤖 **LLMs Locais Gratuitos**: Integração com Ollama e Hugging Face Transformers
- ☁️ **APIs Comerciais**: Suporte para OpenAI, Anthropic e Google
- 🎯 **Análise Avançada**: Extração de tópicos principais, resumos automáticos e métricas
- ❓ **Sistema de Q&A**: Faça perguntas sobre o documento e obtenha respostas contextuais
- 🖥️ **Interface Web**: Aplicação Streamlit intuitiva e responsiva
- 🔄 **Processamento por Chunks**: Otimizado para documentos grandes
- 📊 **Visualizações**: Métricas de palavras, caracteres e tempo de leitura estimado

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.12+
- GPU NVIDIA (opcional, para melhor performance)

### Instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/uniesecruz/CrewAI_pdf_reading.git
cd CrewAI_pdf_reading
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure modelos locais** (opcional):
```bash
# Para Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2:7b

# Para Hugging Face (automático na primeira execução)
python scripts/setup_local_llm.py
```

### Uso

#### Interface Web (Recomendado)

```bash
streamlit run pdf_reading/apps/streamlit_app.py
```

Acesse `http://localhost:8501` no seu navegador.

#### Uso Programático

```python
from llm_pdf_reading.orchestrator import PDFReadingOrchestrator

# Configurar orquestrador
orchestrator = PDFReadingOrchestrator(use_local_models=True)

# Processar PDF
result = orchestrator.process_pdf("caminho/para/seu/arquivo.pdf")

# Fazer perguntas
answer = orchestrator.answer_question(
    result["content"], 
    "Qual é o tema principal do documento?"
)
```

## 🛠️ Tecnologias Utilizadas

### Core
- **CrewAI** (0.150.0): Framework para orquestração de agentes AI
- **Streamlit** (1.47.1): Interface web interativa
- **PyTorch** (2.7.0): Framework de deep learning

### Processamento de PDF
- **PyMuPDF** (1.26.3): Extração rápida e eficiente
- **PyPDF2** (3.0.1): Manipulação de PDFs
- **pdfplumber** (0.11.7): Análise detalhada de layout

### LLMs Locais
- **Ollama**: Modelos como Llama 2, Mistral, CodeLlama
- **Hugging Face Transformers** (4.54.0): DialoGPT e outros modelos
- **CUDA Support**: Aceleração GPU automática

### APIs Comerciais
- **OpenAI**: GPT-3.5, GPT-4
- **Anthropic**: Claude 3
- **Google**: Gemini Pro

## 📁 Estrutura do Projeto

```
pdf_reading/
├── apps/
│   └── streamlit_app.py       <- Interface web principal
├── llm_pdf_reading/
│   ├── __init__.py
│   ├── config.py              <- Configurações centralizadas
│   ├── orchestrator.py        <- Orquestrador principal
│   ├── local_llm.py          <- Gerenciador de LLMs locais
│   ├── pdf_utils.py          <- Utilitários para PDFs
│   └── text_processing.py    <- Processamento de texto
├── scripts/
│   ├── setup_local_llm.py    <- Script de configuração
│   └── test_models.py        <- Testes de modelos
├── data/
│   ├── external/             <- PDFs de terceiros
│   ├── processed/            <- Dados processados
│   └── raw/                  <- PDFs originais
├── models/                   <- Modelos treinados/baixados
├── requirements.txt          <- Dependências do projeto
└── README.md                <- Este arquivo
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# APIs Comerciais (opcional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Configurações Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2:7b

# Configurações gerais
USE_LOCAL_MODELS=true
LOG_LEVEL=INFO
```

### Modelos Suportados

#### Ollama (Gratuito)
- `llama2:7b` - Modelo geral da Meta
- `mistral:7b` - Modelo rápido e eficiente
- `codellama:7b` - Especializado em código
- `neural-chat:7b` - Otimizado para conversas

#### Hugging Face (Gratuito)
- `microsoft/DialoGPT-medium` - Conversação
- `microsoft/DialoGPT-large` - Conversação avançada
- `facebook/blenderbot-400M-distill` - Chatbot compacto

## 📖 Como Usar

### 1. Interface Web

1. **Inicie a aplicação**:
   ```bash
   streamlit run pdf_reading/apps/streamlit_app.py
   ```

2. **Configure o modelo**:
   - Marque "Usar Modelos Locais" para modelos gratuitos
   - Selecione o modelo Ollama desejado (se disponível)
   - Configure fallback para Hugging Face se necessário

3. **Processe um PDF**:
   - Faça upload de um arquivo PDF
   - Clique em "🚀 Processar PDF"
   - Explore os resultados nas abas:
     - 📊 **Análise**: Métricas e resumo
     - 📝 **Conteúdo**: Texto extraído
     - 📋 **Metadados**: Informações do arquivo
     - ❓ **Perguntas**: Sistema de Q&A

4. **Faça perguntas**:
   - Digite uma pergunta sobre o documento
   - Clique em "Responder"
   - Visualize o histórico de perguntas

### 2. Uso Programático

```python
from llm_pdf_reading.orchestrator import PDFReadingOrchestrator

# Configuração para modelos locais
config = {
    'use_ollama': True,
    'ollama_model': 'llama2:7b',
    'use_huggingface': True,
    'hf_model': 'microsoft/DialoGPT-medium'
}

# Inicializar orquestrador
orchestrator = PDFReadingOrchestrator(
    use_local_models=True,
    custom_config=config
)

# Processar PDF
result = orchestrator.process_pdf("documento.pdf")

if result["success"]:
    # Análise básica
    analysis = result["analysis"]
    print(f"Palavras: {analysis['word_count']}")
    print(f"Resumo: {analysis['summary']}")
    
    # Fazer perguntas
    resposta = orchestrator.answer_question(
        result["content"],
        "Quais são os pontos principais?"
    )
    print(f"Resposta: {resposta}")
```

## 🔧 Desenvolvimento

### Executar Testes

```bash
# Teste básico dos modelos
python scripts/test_models.py

# Teste da configuração
python -c "from pdf_reading.llm_pdf_reading.config import *; print('✅ Config OK')"
```

### Estrutura de Desenvolvimento

- `llm_pdf_reading/`: Código principal do projeto
- `apps/`: Aplicações e interfaces
- `scripts/`: Scripts utilitários
- `tests/`: Testes automatizados

## 🐛 Solução de Problemas

### Ollama não conecta
```bash
# Verificar se o Ollama está rodando
curl http://localhost:11434/api/tags

# Iniciar Ollama (se necessário)
ollama serve
```

### Erro de GPU
```bash
# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Forçar CPU se necessário
export CUDA_VISIBLE_DEVICES=""
```

### Dependências faltando
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

## 📈 Performance

- **PDFs pequenos** (< 10 páginas): ~5-15 segundos
- **PDFs médios** (10-50 páginas): ~30-60 segundos  
- **PDFs grandes** (> 50 páginas): ~2-5 minutos

*Performance com GPU pode ser 3-5x mais rápida*

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **uniesecruz** - *Desenvolvimento inicial* - [GitHub](https://github.com/uniesecruz)

## 🙏 Agradecimentos

- [CrewAI](https://crewai.com/) - Framework de orquestração
- [Ollama](https://ollama.ai/) - Modelos locais gratuitos
- [Hugging Face](https://huggingface.co/) - Transformers e modelos
- [Streamlit](https://streamlit.io/) - Interface web

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela!**

