# 🤖 Guia Completo - LLMs Gratuitas na GPU

## 🎯 Objetivo

Este guia configura o sistema para usar **LLMs 100% gratuitas** rodando na sua GPU local, eliminando custos de APIs comerciais.

## 🚀 Setup Rápido (Windows)

```bash
# Método 1: Script automático
scripts/setup_local_llm.bat

# Método 2: Manual
python scripts/setup_environment.py
```

## 🦙 Opção 1: Ollama (Recomendado)

### Instalação:
1. **Baixe:** https://ollama.ai/download/windows
2. **Execute** o instalador
3. **Reinicie** o terminal

### Modelos Recomendados:
```bash
# Modelo geral (4GB RAM)
ollama pull llama2:7b

# Rápido e eficiente (4GB RAM)  
ollama pull mistral:7b

# Especializado em código (4GB RAM)
ollama pull codellama:7b

# Conversacional (4GB RAM)
ollama pull neural-chat:7b
```

### Teste:
```bash
ollama run llama2
>>> Olá! Como você está?
```

## 🤗 Opção 2: Hugging Face Transformers

### Instalação:
```bash
# CPU
pip install torch transformers accelerate

# GPU NVIDIA (recomendado)
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate bitsandbytes
```

### Modelos Recomendados:
- **microsoft/DialoGPT-medium** - Conversacional (400MB)
- **microsoft/DialoGPT-large** - Melhor qualidade (1.3GB)
- **distilbert-base-uncased** - Embeddings rápidos (250MB)

## ⚙️ Configuração (.env)

```env
# ========================================
# MODELOS LOCAIS GRATUITOS (Recomendado)
# ========================================

USE_LOCAL_MODELS=True

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2:7b

# Hugging Face
HF_MODEL_NAME=microsoft/DialoGPT-medium
HF_CACHE_DIR=./models/huggingface

# GPU
USE_GPU=True
DEVICE=auto  # auto, cpu, cuda

# Performance
MAX_TOKENS=2048
TEMPERATURE=0.7
```

## 🎮 Requisitos de Hardware

### GPU NVIDIA (Recomendado):
- **VRAM:** 6GB+ para modelos 7B
- **RAM:** 8GB+ sistema
- **Disco:** 10GB+ livre

### CPU (Alternativa):
- **RAM:** 16GB+ recomendado
- **CPU:** 4+ cores
- **Disco:** 5GB+ livre

## 🧪 Teste do Sistema

```bash
# Teste completo
python examples/local_llm_test.py

# Teste básico
python examples/basic_usage.py

# Interface web
streamlit run apps/streamlit_app.py
```

## 📊 Comparação de Modelos

| Modelo | Tamanho | VRAM | Qualidade | Velocidade |
|--------|---------|------|-----------|------------|
| llama2:7b | 4GB | 6GB | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| mistral:7b | 4GB | 6GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| DialoGPT-medium | 400MB | 2GB | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| codellama:7b | 4GB | 6GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🔧 Solução de Problemas

### Erro: "CUDA out of memory"
```bash
# Usar modelo menor
ollama pull mistral:7b

# Ou configurar CPU
export DEVICE=cpu
```

### Erro: "Ollama não encontrado"
```bash
# Verificar instalação
ollama --version

# Verificar serviço
ollama serve
```

### Erro: "Import torch could not be resolved"
```bash
# Reinstalar PyTorch
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

## 💡 Dicas de Performance

### Para GPU:
- Use modelos 7B para melhor qualidade
- Configure `device=cuda` no .env
- Monitore VRAM com `nvidia-smi`

### Para CPU:
- Use modelos menores (DialoGPT-medium)
- Configure `device=cpu` no .env
- Aumente RAM se possível

### Para ambos:
- Feche outros programas pesados
- Use SSD para cache de modelos
- Configure `temperature=0.3` para respostas mais precisas

## 🌟 Vantagens dos Modelos Locais

✅ **100% Gratuito** - Sem custos de API  
✅ **Privacidade** - Dados ficam no seu computador  
✅ **Sem limite de tokens** - Use quanto quiser  
✅ **Offline** - Funciona sem internet  
✅ **Customizável** - Ajuste parâmetros livremente  
✅ **Sem rate limits** - Sem limitações de uso  

## 🚀 Próximos Passos

1. **Configure** usando o script automático
2. **Teste** com `python examples/local_llm_test.py`
3. **Use** a interface web com `streamlit run apps/streamlit_app.py`
4. **Experimente** diferentes modelos e parâmetros
5. **Customize** para suas necessidades específicas

---

**🎉 Parabéns!** Agora você tem um sistema completo de LLMs gratuitas rodando na sua GPU!
