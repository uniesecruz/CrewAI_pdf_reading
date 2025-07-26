#!/usr/bin/env python3
"""
Teste para verificar se as correções do LLM funcionam
"""
import sys
from pathlib import Path

# Adicionar o módulo ao path
sys.path.append(str(Path(__file__).parent / "pdf_reading"))

def test_local_llm():
    """Testa o gerenciador de LLM local"""
    try:
        from llm_pdf_reading.local_llm import LocalLLMManager
        
        # Configuração de teste
        config = {
            'use_ollama': True,
            'use_huggingface': True,
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama2:7b',
            'hf_model': 'microsoft/DialoGPT-medium',
            'device': 'auto'
        }
        
        print("🔧 Testando LocalLLMManager...")
        manager = LocalLLMManager(config)
        
        print(f"✅ Manager criado: {manager.current_provider}")
        print(f"📊 Disponível: {manager.is_available()}")
        
        if manager.is_available():
            print("🧪 Testando geração com max_length...")
            try:
                response = manager.generate(
                    "Teste simples",
                    max_length=50,
                    temperature=0.5
                )
                print(f"✅ Sucesso: {response[:100]}...")
            except Exception as e:
                print(f"❌ Erro na geração: {e}")
        else:
            print("⚠️ Nenhum LLM disponível para teste")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_llm()
