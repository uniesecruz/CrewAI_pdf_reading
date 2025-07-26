"""
Testes para o processador de PDFs
"""
import pytest
from pathlib import Path
import tempfile
import sys

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent.parent))

from llm_pdf_reading.pdf_utils import PDFProcessor

class TestPDFProcessor:
    """Testes para a classe PDFProcessor"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.processor = PDFProcessor()
    
    def test_processor_initialization(self):
        """Testa se o processador é inicializado corretamente"""
        assert self.processor is not None
        assert '.pdf' in self.processor.supported_formats
    
    def test_split_into_chunks(self):
        """Testa a divisão de texto em chunks"""
        text = "Este é um texto de exemplo para testar a funcionalidade de divisão em chunks. " * 20
        chunks = self.processor.split_into_chunks(text, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        assert len(chunks[0]) <= 100
    
    def test_split_into_chunks_empty_text(self):
        """Testa divisão com texto vazio"""
        chunks = self.processor.split_into_chunks("", chunk_size=100, overlap=20)
        assert len(chunks) == 1
        assert chunks[0] == ""
    
    def test_split_into_chunks_short_text(self):
        """Testa divisão com texto curto"""
        text = "Texto curto"
        chunks = self.processor.split_into_chunks(text, chunk_size=100, overlap=20)
        assert len(chunks) == 1
        assert chunks[0] == text
    
    # Nota: Testes com PDFs reais requerem arquivos de exemplo
    # Estes podem ser adicionados quando houver arquivos de teste disponíveis
