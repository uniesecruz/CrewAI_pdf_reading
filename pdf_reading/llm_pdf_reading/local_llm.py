"""
Gerenciador de LLMs locais gratuitos
Suporte para Ollama, Hugging Face Transformers e outros modelos open-source
"""
import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class OllamaManager:
    """Gerenciador para modelos Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa cliente Ollama"""
        try:
            import ollama
            self.client = ollama.Client(host=self.base_url)
            logger.info(f"🦙 Cliente Ollama inicializado: {self.base_url}")
        except ImportError:
            logger.warning("⚠️  Ollama não instalado. Execute: pip install ollama")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Ollama: {e}")
    
    def is_available(self) -> bool:
        """Verifica se Ollama está disponível"""
        if not self.client:
            return False
        try:
            # Testar conexão com timeout
            models = self.client.list()
            return True
        except Exception as e:
            logger.debug(f"Ollama não disponível: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis no Ollama"""
        if not self.client:
            return []
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            logger.error(f"Erro ao listar modelos Ollama: {e}")
            return []
    
    def generate(self, prompt: str, model: str = "llama2:7b", **kwargs) -> str:
        """Gera texto usando Ollama"""
        if not self.client:
            raise RuntimeError("Cliente Ollama não disponível")
        
        try:
            # Para Ollama, usar apenas parâmetros básicos
            ollama_options = {}
            
            # Mapear parâmetros para formato Ollama
            if 'temperature' in kwargs:
                ollama_options['temperature'] = kwargs['temperature']
            if 'max_length' in kwargs or 'num_predict' in kwargs:
                ollama_options['num_predict'] = kwargs.get('num_predict', kwargs.get('max_length', 100))
            if 'top_p' in kwargs:
                ollama_options['top_p'] = kwargs['top_p']
            if 'top_k' in kwargs:
                ollama_options['top_k'] = kwargs['top_k']
            
            response = self.client.generate(
                model=model,
                prompt=prompt,
                stream=False,
                options=ollama_options  # Ollama espera options como dict separado
            )
            return response['response']
        except Exception as e:
            logger.error(f"Erro na geração Ollama: {e}")
            raise

class HuggingFaceManager:
    """Gerenciador para modelos Hugging Face Transformers"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", device: str = "auto"):
        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa modelo Hugging Face"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Determinar device
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            logger.info(f"🤗 Carregando modelo {self.model_name} no {self.device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            # Configurar pad_token se não existir
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info(f"✅ Modelo {self.model_name} carregado com sucesso!")
            
        except ImportError:
            logger.warning("⚠️  Transformers não instalado. Execute: pip install transformers torch")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo HF: {e}")
    
    def is_available(self) -> bool:
        """Verifica se o modelo está disponível"""
        return self.model is not None and self.tokenizer is not None
    
    def generate(self, prompt: str, max_length: int = 1024, **kwargs) -> str:
        """Gera texto usando modelo Hugging Face"""
        if not self.is_available():
            raise RuntimeError("Modelo Hugging Face não disponível")
        
        try:
            import torch
            
            # Tokenizar entrada
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = inputs.to("cuda")
            
            # Gerar
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=kwargs.get('temperature', 0.7),
                    do_sample=kwargs.get('do_sample', True),
                    pad_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decodificar resposta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remover prompt da resposta
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Erro na geração HF: {e}")
            raise

class LocalLLMManager:
    """Gerenciador principal para LLMs locais"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ollama = None
        self.huggingface = None
        self.current_provider = None
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Inicializa provedores disponíveis"""
        # Tentar Ollama primeiro
        if self.config.get('use_ollama', True):
            self.ollama = OllamaManager(self.config.get('ollama_url', 'http://localhost:11434'))
            if self.ollama.is_available():
                self.current_provider = 'ollama'
                logger.info("🦙 Usando Ollama como provedor principal")
                return
        
        # Fallback para Hugging Face
        if self.config.get('use_huggingface', True):
            model_name = self.config.get('hf_model', 'microsoft/DialoGPT-medium')
            device = self.config.get('device', 'auto')
            self.huggingface = HuggingFaceManager(model_name, device)
            if self.huggingface.is_available():
                self.current_provider = 'huggingface'
                logger.info("🤗 Usando Hugging Face como provedor principal")
                return
        
        logger.warning("⚠️  Nenhum provedor local disponível!")
    
    def is_available(self) -> bool:
        """Verifica se algum provedor está disponível"""
        return self.current_provider is not None
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Gera texto usando o provedor disponível"""
        if not self.is_available():
            raise RuntimeError("Nenhum provedor LLM local disponível")
        
        if self.current_provider == 'ollama':
            model = kwargs.get('model', self.config.get('ollama_model', 'llama2:7b'))
            # Ollama agora pode lidar com max_length convertendo para num_predict
            return self.ollama.generate(prompt, model=model, **kwargs)
        
        elif self.current_provider == 'huggingface':
            return self.huggingface.generate(prompt, **kwargs)
        
        else:
            raise RuntimeError(f"Provedor não suportado: {self.current_provider}")
    
    def get_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o provedor atual"""
        info = {
            "provider": self.current_provider,
            "available": self.is_available()
        }
        
        if self.current_provider == 'ollama' and self.ollama:
            info["models"] = self.ollama.list_models()
            info["base_url"] = self.ollama.base_url
        
        elif self.current_provider == 'huggingface' and self.huggingface:
            info["model"] = self.huggingface.model_name
            info["device"] = self.huggingface.device
        
        return info

# Função de conveniência para criar manager
def create_local_llm_manager(config: Optional[Dict[str, Any]] = None) -> LocalLLMManager:
    """Cria um gerenciador de LLM local com configuração padrão"""
    if config is None:
        from .config import OLLAMA_CONFIG, HUGGINGFACE_CONFIG, LOCAL_INFERENCE_CONFIG
        
        config = {
            'use_ollama': True,
            'use_huggingface': True,
            'ollama_url': OLLAMA_CONFIG['base_url'],
            'ollama_model': OLLAMA_CONFIG['default_model'],
            'hf_model': HUGGINGFACE_CONFIG['model_name'],
            'device': HUGGINGFACE_CONFIG['device'],
            **LOCAL_INFERENCE_CONFIG
        }
    
    return LocalLLMManager(config)

# Teste rápido
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = create_local_llm_manager()
    
    if manager.is_available():
        print(f"✅ LLM local disponível: {manager.current_provider}")
        print(f"📊 Info: {manager.get_info()}")
        
        try:
            response = manager.generate("Olá, como você está?", max_length=100)
            print(f"🤖 Resposta: {response}")
        except Exception as e:
            print(f"❌ Erro na geração: {e}")
    else:
        print("❌ Nenhum LLM local disponível")
