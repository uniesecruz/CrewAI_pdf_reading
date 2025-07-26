"""
Utilitários para processamento de PDFs
"""
import PyPDF2
import fitz  # PyMuPDF
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Classe para processar arquivos PDF"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text_pypdf2(self, pdf_path: Path) -> str:
        """Extrai texto usando PyPDF2"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto com PyPDF2: {e}")
            return ""
    
    def extract_text_pymupdf(self, pdf_path: Path) -> str:
        """Extrai texto usando PyMuPDF (melhor qualidade)"""
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto com PyMuPDF: {e}")
            return ""
    
    def extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extrai metadados do PDF"""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            return metadata
        except Exception as e:
            logger.error(f"Erro ao extrair metadados: {e}")
            return {}
    
    def split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Divide o texto em chunks para processamento"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
        return chunks
