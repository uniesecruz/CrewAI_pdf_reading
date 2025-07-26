"""
Classe principal para orquestração do processamento de PDFs
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from .pdf_utils import PDFProcessor
from .crew_agents import PDFAnalysisAgents, PDFAnalysisTasks

logger = logging.getLogger(__name__)

class PDFReadingOrchestrator:
    """Orquestrador principal para leitura e análise de PDFs"""
    
    def __init__(self, llm=None):
        self.pdf_processor = PDFProcessor()
        self.agents = PDFAnalysisAgents(llm)
        self.tasks = PDFAnalysisTasks()
        
        # Criar agentes
        self.pdf_reader = self.agents.create_pdf_reader_agent()
        self.content_analyzer = self.agents.create_content_analyzer_agent()
        self.qa_agent = self.agents.create_qa_agent()
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Processa um arquivo PDF completo"""
        try:
            pdf_path = Path(pdf_path)
            
            # Verificar se o arquivo existe
            if not pdf_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
            # Extrair texto
            logger.info(f"Extraindo texto de: {pdf_path}")
            text_content = self.pdf_processor.extract_text_pymupdf(pdf_path)
            
            if not text_content.strip():
                raise ValueError("Não foi possível extrair texto do PDF")
            
            # Extrair metadados
            metadata = self.pdf_processor.extract_metadata(pdf_path)
            
            # Dividir em chunks
            chunks = self.pdf_processor.split_into_chunks(text_content)
            
            # Processar com CrewAI (simulado por enquanto)
            analysis_result = self._analyze_content(text_content)
            
            return {
                "file_path": str(pdf_path),
                "metadata": metadata,
                "content": text_content,
                "chunks": chunks,
                "analysis": analysis_result,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF: {e}")
            return {
                "file_path": str(pdf_path) if 'pdf_path' in locals() else "unknown",
                "error": str(e),
                "success": False
            }
    
    def answer_question(self, pdf_content: str, question: str) -> str:
        """Responde uma pergunta sobre o conteúdo do PDF"""
        try:
            # Por enquanto, implementação simples
            # Em produção, usaria CrewAI para processar
            return f"Baseado no conteúdo do PDF, para a pergunta '{question}': [Resposta seria gerada pelo LLM]"
        except Exception as e:
            logger.error(f"Erro ao responder pergunta: {e}")
            return f"Erro ao processar pergunta: {e}"
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Análise interna do conteúdo (placeholder)"""
        # Esta função seria expandida para usar CrewAI
        word_count = len(content.split())
        char_count = len(content)
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "estimated_reading_time": word_count // 200,  # 200 palavras por minuto
            "summary": "Resumo seria gerado pelo LLM...",
            "key_topics": ["Tópico 1", "Tópico 2", "Tópico 3"]
        }
    
    def batch_process(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """Processa múltiplos PDFs"""
        results = []
        for pdf_path in pdf_paths:
            result = self.process_pdf(pdf_path)
            results.append(result)
        return results
