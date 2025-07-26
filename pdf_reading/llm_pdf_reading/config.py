"""
Configurações do projeto LLM PDF Reading
Suporte para modelos locais gratuitos e APIs comerciais
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Diretórios do projeto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
CONFIG_DIR = PROJECT_ROOT / "config"

# ========================================
# CONFIGURAÇÕES DE MODELOS
# ========================================

# Escolha do tipo de modelo (local ou API)
USE_LOCAL_MODELS = os.getenv("USE_LOCAL_MODELS", "True").lower() == "true"

# Configurações para APIs comerciais
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ========================================
# CONFIGURAÇÕES DE MODELOS LOCAIS (GRATUITOS)
# ========================================

# Ollama Configuration
OLLAMA_CONFIG = {
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "default_model": os.getenv("OLLAMA_DEFAULT_MODEL", "llama2:7b"),
    "timeout": 120,
    "available_models": [
        "llama2:7b",      # Modelo geral, bom para textos
        "mistral:7b",     # Rápido e eficiente
        "codellama:7b",   # Especializado em código
        "neural-chat:7b", # Conversacional
        "dolphin-mistral:7b", # Instruct-tuned
    ]
}

# Hugging Face Configuration  
HUGGINGFACE_CONFIG = {
    "model_name": os.getenv("HF_MODEL_NAME", "microsoft/DialoGPT-medium"),
    "cache_dir": os.getenv("HF_CACHE_DIR", str(MODELS_DIR / "huggingface")),
    "device": os.getenv("DEVICE", "auto"),  # auto, cpu, cuda, mps
    "use_gpu": os.getenv("USE_GPU", "True").lower() == "true",
    "available_models": {
        "conversational": [
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-large",
            "facebook/blenderbot-400M-distill"
        ],
        "instruction": [
            "microsoft/CodeGPT-small-py",
            "Salesforce/codegen-350M-mono"
        ],
        "embedding": [
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2"
        ]
    }
}

# Configurações de inferência local
LOCAL_INFERENCE_CONFIG = {
    "max_tokens": int(os.getenv("MAX_TOKENS", "2048")),
    "temperature": float(os.getenv("TEMPERATURE", "0.7")),
    "top_p": float(os.getenv("TOP_P", "0.9")),
    "do_sample": True,
    "pad_token_id": 50256,  # GPT-2 pad token
    "use_cache": True,
    "device_map": "auto" if os.getenv("USE_GPU", "True").lower() == "true" else "cpu"
}

# ========================================
# CONFIGURAÇÕES DO CREWAI
# ========================================

CREW_AI_CONFIG = {
    "max_rpm": 10,
    "max_execution_time": 300,
    "verbose": True,
    "use_local_models": USE_LOCAL_MODELS
}

# ========================================
# CONFIGURAÇÕES DE PDF
# ========================================

PDF_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_pages": 100,
    "extract_images": False,
    "extract_tables": True
}

# ========================================
# CONFIGURAÇÕES DE EMBEDDING
# ========================================

EMBEDDING_CONFIG = {
    "model": "sentence-transformers/all-MiniLM-L6-v2" if USE_LOCAL_MODELS else "text-embedding-ada-002",
    "dimension": 384 if USE_LOCAL_MODELS else 1536,
    "batch_size": 32,
    "use_local": USE_LOCAL_MODELS
}

# ========================================
# UTILITÁRIOS
# ========================================

def get_available_models():
    """Retorna lista de modelos disponíveis baseado na configuração"""
    if USE_LOCAL_MODELS:
        return {
            "ollama": OLLAMA_CONFIG["available_models"],
            "huggingface": HUGGINGFACE_CONFIG["available_models"]
        }
    else:
        return {
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "anthropic": ["claude-3-sonnet", "claude-3-haiku"],
            "google": ["gemini-pro", "gemini-pro-vision"]
        }

def get_model_config(model_type="auto"):
    """Retorna configuração do modelo baseado no tipo"""
    if USE_LOCAL_MODELS:
        if model_type == "ollama" or model_type == "auto":
            return OLLAMA_CONFIG
        elif model_type == "huggingface":
            return HUGGINGFACE_CONFIG
    
    return {
        "openai_api_key": OPENAI_API_KEY,
        "anthropic_api_key": ANTHROPIC_API_KEY,
        "google_api_key": GOOGLE_API_KEY
    }

# Debug info
if __name__ == "__main__":
    print(f"🔧 Configuração LLM PDF Reading")
    print(f"📍 Diretório do projeto: {PROJECT_ROOT}")
    print(f"🤖 Usando modelos locais: {USE_LOCAL_MODELS}")
    print(f"💾 Modelos disponíveis: {get_available_models()}")
