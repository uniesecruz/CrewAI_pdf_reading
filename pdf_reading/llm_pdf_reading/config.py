"""
Configurações do projeto LLM PDF Reading
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

# Configurações de API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configurações do CrewAI
CREW_AI_CONFIG = {
    "max_rpm": 10,
    "max_execution_time": 300,
    "verbose": True
}

# Configurações de PDF
PDF_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_pages": 100
}

# Configurações de Embedding
EMBEDDING_CONFIG = {
    "model": "text-embedding-ada-002",
    "dimension": 1536
}
