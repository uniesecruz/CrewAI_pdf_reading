"""
Classe principal para orquestração do processamento de PDFs
Suporte para LLMs locais gratuitos e APIs comerciais
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from .pdf_utils import PDFProcessor
from .config import USE_LOCAL_MODELS, get_model_config

logger = logging.getLogger(__name__)

class PDFReadingOrchestrator:
    """Orquestrador principal para leitura e análise de PDFs"""
    
    def __init__(self, llm=None, use_local_models: Optional[bool] = None, custom_config: Optional[Dict] = None):
        self.pdf_processor = PDFProcessor()
        self.use_local_models = use_local_models if use_local_models is not None else USE_LOCAL_MODELS
        self.llm_manager = None
        self.custom_config = custom_config
        
        # Inicializar LLM
        self._initialize_llm(llm)
    
    def _initialize_llm(self, llm=None):
        """Inicializa o gerenciador de LLM"""
        if llm:
            self.llm_manager = llm
            return
        
        if self.use_local_models:
            try:
                # Se há configuração personalizada, usar LocalLLMManager diretamente
                if self.custom_config:
                    from .local_llm import LocalLLMManager
                    self.llm_manager = LocalLLMManager(self.custom_config)
                else:
                    from .local_llm import create_local_llm_manager
                    self.llm_manager = create_local_llm_manager()
                
                if self.llm_manager and self.llm_manager.is_available():
                    logger.info(f"🤖 LLM local inicializado: {self.llm_manager.current_provider}")
                else:
                    logger.warning("⚠️  LLM local não disponível, usando modo simplificado")
                    self.llm_manager = None
            except Exception as e:
                logger.error(f"Erro ao inicializar LLM local: {e}")
                self.llm_manager = None
        else:
            logger.info("💰 Modo API comercial selecionado")
            # Aqui seria inicializado cliente para APIs comerciais
            self.llm_manager = None
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Processa um arquivo PDF completo"""
        try:
            pdf_path = Path(pdf_path)
            
            # Verificar se o arquivo existe
            if not pdf_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
            # Extrair texto
            logger.info(f"📄 Extraindo texto de: {pdf_path}")
            text_content = self.pdf_processor.extract_text_pymupdf(pdf_path)
            
            if not text_content.strip():
                raise ValueError("Não foi possível extrair texto do PDF")
            
            # Extrair metadados
            metadata = self.pdf_processor.extract_metadata(pdf_path)
            
            # Dividir em chunks
            chunks = self.pdf_processor.split_into_chunks(text_content)
            
            # Analisar conteúdo com LLM (se disponível)
            analysis_result = self._analyze_content_with_llm(text_content)
            
            return {
                "file_path": str(pdf_path),
                "metadata": metadata,
                "content": text_content,
                "chunks": chunks,
                "analysis": analysis_result,
                "llm_used": self.llm_manager.current_provider if self.llm_manager else "none",
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
        """Responde uma pergunta sobre o conteúdo do PDF usando LLM"""
        try:
            if self.llm_manager and self.llm_manager.is_available():
                # Criar prompt estruturado
                prompt = f"""
Baseado no seguinte conteúdo de documento, responda a pergunta de forma precisa e concisa.

DOCUMENTO:
{pdf_content[:2000]}...

PERGUNTA: {question}

RESPOSTA:"""
                
                # Gerar resposta com LLM local
                response = self.llm_manager.generate(
                    prompt,
                    max_length=500,
                    temperature=0.3  # Mais determinístico para QA
                )
                
                return response.strip()
            else:
                # Fallback simples quando LLM não está disponível
                return self._simple_qa_fallback(pdf_content, question)
                
        except Exception as e:
            logger.error(f"Erro ao responder pergunta: {e}")
            return f"Erro ao processar pergunta: {e}"
    
    def _analyze_content_with_llm(self, content: str) -> Dict[str, Any]:
        """Análise de conteúdo usando LLM (se disponível)"""
        base_analysis = self._basic_analysis(content)
        
        if self.llm_manager and self.llm_manager.is_available():
            try:
                # Prompt para análise do conteúdo
                prompt = f"""
Analise o seguinte texto e forneça:
1. Resumo principal (máximo 100 palavras)
2. 3-5 tópicos principais
3. Tipo de documento (relatório, artigo, manual, etc.)

TEXTO:
{content[:1500]}...

ANÁLISE:"""
                
                llm_analysis = self.llm_manager.generate(
                    prompt,
                    max_length=300,
                    temperature=0.5
                )
                
                base_analysis["llm_summary"] = llm_analysis
                base_analysis["analysis_type"] = "llm_enhanced"
                
            except Exception as e:
                logger.error(f"Erro na análise LLM: {e}")
                base_analysis["analysis_type"] = "basic_only"
        
        return base_analysis
    
    def _basic_analysis(self, content: str) -> Dict[str, Any]:
        """Análise básica sem LLM"""
        words = content.split()
        word_count = len(words)
        char_count = len(content)
        
        # Análise simples de tópicos (palavras mais frequentes)
        word_freq = {}
        for word in words:
            word = word.lower().strip('.,!?;:"()[]{}')
            if len(word) > 3:  # Ignorar palavras muito curtas
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top 5 palavras mais frequentes como tópicos
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        key_topics = [word for word, freq in top_words]
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "estimated_reading_time": word_count // 200,  # 200 palavras por minuto
            "summary": f"Documento com {word_count} palavras sobre {', '.join(key_topics[:3])}",
            "key_topics": key_topics,
            "analysis_type": "basic"
        }
    
    def _simple_qa_fallback(self, content: str, question: str) -> str:
        """Fallback simples para QA quando LLM não está disponível"""
        # Busca simples por palavras-chave da pergunta no conteúdo
        question_words = question.lower().split()
        content_lower = content.lower()
        
        # Encontrar sentenças que contêm palavras da pergunta
        sentences = content.split('.')
        relevant_sentences = []
        
        for sentence in sentences[:50]:  # Limitar busca
            sentence_lower = sentence.lower()
            matches = sum(1 for word in question_words if word in sentence_lower)
            if matches >= 2:  # Pelo menos 2 palavras da pergunta
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            return f"Baseado no documento: {' '.join(relevant_sentences[:2])}"
        else:
            return "Não foi possível encontrar informação específica sobre essa pergunta no documento."
    
    def get_llm_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o LLM em uso"""
        if self.llm_manager:
            return self.llm_manager.get_info()
        else:
            return {
                "provider": "none",
                "available": False,
                "reason": "LLM local não inicializado"
            }
    
    def batch_process(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """Processa múltiplos PDFs"""
        results = []
        for pdf_path in pdf_paths:
            result = self.process_pdf(pdf_path)
            results.append(result)
        return results
