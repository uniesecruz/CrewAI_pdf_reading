"""
LLM PDF Reading - Sistema de leitura e análise de PDFs usando LLMs e CrewAI
"""

from .config import *
from .pdf_utils import PDFProcessor
from .orchestrator import PDFReadingOrchestrator

__version__ = "0.0.1"
__author__ = "sergio_alves_da_cruz"

# Exportar classes principais
__all__ = [
    "PDFProcessor",
    "PDFReadingOrchestrator",
]