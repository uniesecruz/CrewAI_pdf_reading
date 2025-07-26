"""
Exemplo de uso com LLMs locais gratuitos
Demonstra como usar Ollama e Hugging Face Transformers
"""
from pathlib import Path
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent.parent))

def test_local_llm():
    """Testa LLMs locais disponíveis"""
    print("🤖 Testando LLMs Locais Gratuitos")
    print("=" * 50)
    
    try:
        from llm_pdf_reading.local_llm import create_local_llm_manager
        
        # Criar manager
        manager = create_local_llm_manager()
        
        # Verificar disponibilidade
        if not manager.is_available():
            print("❌ Nenhum LLM local disponível!")
            print("\n💡 Para usar LLMs gratuitos:")
            print("   1. Instale Ollama: https://ollama.ai/download")
            print("   2. Execute: ollama pull llama2:7b")
            print("   3. Ou instale transformers: pip install transformers torch")
            return False
        
        # Mostrar informações
        info = manager.get_info()
        print(f"✅ LLM Local Disponível!")
        print(f"   Provedor: {info['provider']}")
        if 'models' in info:
            print(f"   Modelos: {info['models']}")
        if 'model' in info:
            print(f"   Modelo: {info['model']}")
        if 'device' in info:
            print(f"   Device: {info['device']}")
        
        # Teste de geração
        print(f"\n🧪 Testando geração de texto...")
        test_prompts = [
            "Explique brevemente o que é inteligência artificial:",
            "Resuma em uma frase: A leitura de PDFs é importante porque",
            "Complete: Machine learning é"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            try:
                print(f"\n{i}. Prompt: {prompt}")
                response = manager.generate(prompt, max_length=100, temperature=0.7)
                print(f"   Resposta: {response[:200]}...")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Dependências não instaladas: {e}")
        print("💡 Execute: pip install transformers torch ollama")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_pdf_with_local_llm():
    """Testa processamento de PDF com LLM local"""
    print("\n📄 Testando PDF com LLM Local")
    print("=" * 50)
    
    try:
        from llm_pdf_reading.orchestrator import PDFReadingOrchestrator
        
        # Criar orquestrador com modelos locais
        orchestrator = PDFReadingOrchestrator(use_local_models=True)
        
        # Verificar se LLM está disponível
        llm_info = orchestrator.get_llm_info()
        print(f"🤖 LLM Info: {llm_info}")
        
        # Caminho para PDF de exemplo
        pdf_path = "data/raw/exemplo.pdf"
        
        if not Path(pdf_path).exists():
            print(f"❌ Arquivo não encontrado: {pdf_path}")
            print("💡 Coloque um arquivo PDF em 'data/raw/exemplo.pdf' para testar")
            
            # Criar texto de exemplo para demonstração
            exemplo_texto = """
            Este é um documento de exemplo sobre inteligência artificial.
            A IA está revolucionando várias áreas da tecnologia e sociedade.
            Machine learning e deep learning são subcampos importantes da IA.
            Aplicações incluem reconhecimento de voz, visão computacional e processamento de linguagem natural.
            O futuro da IA promete ainda mais avanços e integração na vida cotidiana.
            """
            
            print(f"\n🧪 Usando texto de exemplo para demonstração...")
            
            # Testar análise de conteúdo
            analysis = orchestrator._analyze_content_with_llm(exemplo_texto)
            print(f"\n📊 Análise do conteúdo:")
            for key, value in analysis.items():
                print(f"   {key}: {value}")
            
            # Testar resposta a pergunta
            pergunta = "Quais são os subcampos da inteligência artificial?"
            resposta = orchestrator.answer_question(exemplo_texto, pergunta)
            print(f"\n❓ Pergunta: {pergunta}")
            print(f"💡 Resposta: {resposta}")
            
            return True
        
        # Processar PDF real
        print(f"📄 Processando: {pdf_path}")
        result = orchestrator.process_pdf(pdf_path)
        
        if result["success"]:
            print("✅ PDF processado com sucesso!")
            print(f"📊 Estatísticas:")
            analysis = result["analysis"]
            print(f"   - Palavras: {analysis['word_count']}")
            print(f"   - Tipo de análise: {analysis['analysis_type']}")
            print(f"   - LLM usado: {result.get('llm_used', 'N/A')}")
            
            if 'llm_summary' in analysis:
                print(f"   - Resumo LLM: {analysis['llm_summary'][:200]}...")
            
            # Testar pergunta
            pergunta = "Qual é o tema principal do documento?"
            resposta = orchestrator.answer_question(result["content"], pergunta)
            print(f"\n❓ Pergunta: {pergunta}")
            print(f"💡 Resposta: {resposta[:300]}...")
        else:
            print(f"❌ Erro: {result['error']}")
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def show_setup_guide():
    """Mostra guia de configuração para LLMs locais"""
    print("\n📚 Guia de Configuração - LLMs Locais Gratuitos")
    print("=" * 60)
    
    print("🦙 OPÇÃO 1: Ollama (Recomendado)")
    print("   1. Baixe: https://ollama.ai/download")
    print("   2. Instale o executável")
    print("   3. Abra terminal e execute:")
    print("      ollama pull llama2:7b")
    print("      ollama pull mistral:7b")
    print("   4. Teste: ollama run llama2")
    
    print("\n🤗 OPÇÃO 2: Hugging Face Transformers")
    print("   1. Instale dependências:")
    print("      pip install torch transformers accelerate")
    print("   2. Para GPU (NVIDIA):")
    print("      pip install torch --index-url https://download.pytorch.org/whl/cu121")
    print("   3. Configure no .env:")
    print("      HF_MODEL_NAME=microsoft/DialoGPT-medium")
    
    print("\n⚡ DICAS DE PERFORMANCE:")
    print("   - GPU NVIDIA: Use modelos 7B (llama2:7b, mistral:7b)")
    print("   - CPU: Use modelos menores (DialoGPT-medium)")
    print("   - RAM: Recomendado 8GB+ para modelos 7B")
    print("   - Disco: Reserve 5-10GB para modelos")
    
    print("\n🔧 CONFIGURAÇÃO NO .env:")
    print("   USE_LOCAL_MODELS=True")
    print("   OLLAMA_BASE_URL=http://localhost:11434")
    print("   OLLAMA_DEFAULT_MODEL=llama2:7b")
    print("   USE_GPU=True")

def main():
    """Função principal"""
    print("🚀 LLM PDF Reading - Teste de Modelos Locais")
    print("🎯 100% Gratuito usando GPU local!")
    print("=" * 60)
    
    # Testar LLMs locais
    llm_available = test_local_llm()
    
    if llm_available:
        # Testar com PDF
        test_pdf_with_local_llm()
    else:
        # Mostrar guia de configuração
        show_setup_guide()
    
    print("\n" + "=" * 60)
    print("🎉 Teste concluído!")
    print("💡 Para usar na interface web: streamlit run apps/streamlit_app.py")

if __name__ == "__main__":
    main()
