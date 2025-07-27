#!/usr/bin/env python3
"""
Exemplo completo de integração do sistema de monitoramento
com código existente de LLM PDF Reading

Este arquivo demonstra como aplicar os decoradores de monitoramento
aos seus códigos existentes sem modificar a lógica principal.
"""

import sys
import time
import random
from pathlib import Path
from typing import Dict, Any, Optional

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importar decoradores de monitoramento
from llm_pdf_reading.monitoring.decorators import (
    monitor_llm_operation,
    monitor_pdf_operation,
    monitor_qa_operation,
    monitor_complete_operation
)

# Iniciar sistema de monitoramento
from llm_pdf_reading.monitoring import model_monitor
if not model_monitor.is_monitoring:
    model_monitor.start_monitoring()
    print("🚀 Sistema de monitoramento iniciado!")

# ====================================================================
# EXEMPLO 1: Simulação de LocalLLMManager com monitoramento
# ====================================================================

class LocalLLMManagerMonitored:
    """Exemplo de LocalLLMManager com monitoramento integrado"""
    
    def __init__(self):
        self.available_models = [
            "llama2:7b",
            "llama2:13b", 
            "mistral:7b",
            "codellama:7b",
            "gemma:7b"
        ]
        print("🤖 LocalLLMManager iniciado com modelos:", self.available_models)
    
    @monitor_llm_operation(
        model_name="llama2:7b",
        provider="ollama"
    )
    def generate_with_ollama(self, prompt: str, model_name: str = "llama2:7b") -> str:
        """
        Simula geração de texto com Ollama
        O decorator automaticamente monitora:
        - Tempo de execução
        - Sucesso/falha
        - Métricas LLM
        - Log no MLflow
        """
        print(f"📝 Gerando resposta com {model_name}...")
        
        # Simular processamento (seu código existente aqui)
        processing_time = random.uniform(0.5, 3.0)  # Simular variação
        time.sleep(processing_time)
        
        # Simular possível falha (5% de chance)
        if random.random() < 0.05:
            raise Exception(f"Erro simulado no modelo {model_name}")
        
        # Retornar resposta simulada
        response = f"""
        Baseado no prompt: "{prompt}"
        
        Esta é uma resposta simulada do modelo {model_name} via Ollama.
        A resposta foi processada em {processing_time:.2f} segundos.
        
        Conteúdo da resposta gerada pelo modelo...
        """
        
        print(f"✅ Resposta gerada com sucesso!")
        return response.strip()
    
    @monitor_llm_operation(
        model_name="microsoft/DialoGPT-medium",
        provider="huggingface"
    )
    def generate_with_huggingface(self, prompt: str, model_name: str = "microsoft/DialoGPT-medium") -> str:
        """
        Simula geração de texto com Hugging Face
        Também automaticamente monitorado
        """
        print(f"🤗 Gerando resposta com HuggingFace {model_name}...")
        
        # Simular processamento diferente
        processing_time = random.uniform(1.0, 4.0)
        time.sleep(processing_time)
        
        # Simular falha ocasional
        if random.random() < 0.1:
            raise Exception(f"Erro de conectividade com HuggingFace")
        
        response = f"Resposta do HuggingFace {model_name}: {prompt}"
        print(f"✅ HuggingFace resposta gerada!")
        return response

# ====================================================================
# EXEMPLO 2: Simulação de PDFOrchestrator com monitoramento
# ====================================================================

class PDFOrchestratorMonitored:
    """Exemplo de PDFOrchestrator com monitoramento integrado"""
    
    def __init__(self, llm_manager: LocalLLMManagerMonitored):
        self.llm_manager = llm_manager
        print("📄 PDFOrchestrator iniciado!")
    
    @monitor_pdf_operation()
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Simula extração de texto do PDF
        Monitora automaticamente:
        - Tempo de processamento
        - Tamanho do arquivo
        - Número de páginas
        - Método de extração
        """
        print(f"📖 Extraindo texto de: {pdf_path}")
        
        # Simular extração (seu código PyMuPDF aqui)
        extraction_time = random.uniform(0.3, 2.0)
        time.sleep(extraction_time)
        
        # Simular falha ocasional
        if random.random() < 0.02:
            raise Exception(f"Erro ao ler arquivo PDF: {pdf_path}")
        
        # Texto simulado extraído
        extracted_text = f"""
        TEXTO EXTRAÍDO DO PDF: {pdf_path}
        
        Capítulo 1: Introdução
        Este é um documento de exemplo que foi processado pelo sistema de 
        leitura de PDFs com monitoramento integrado.
        
        Capítulo 2: Desenvolvimento  
        O sistema utiliza PyMuPDF para extração de texto e modelos LLM
        para análise e resposta a perguntas.
        
        Capítulo 3: Conclusão
        A integração do monitoramento permite acompanhar a performance
        em tempo real sem modificar o código principal.
        
        Total de páginas processadas: 10
        Tempo de extração: {extraction_time:.2f}s
        """
        
        print(f"✅ Texto extraído: {len(extracted_text)} caracteres")
        return extracted_text.strip()
    
    @monitor_qa_operation()
    def answer_question(self, question: str, context: str, model_name: str = "llama2:7b") -> str:
        """
        Simula resposta a pergunta com contexto
        Monitora automaticamente:
        - Qualidade da resposta
        - Tempo de processamento
        - Métricas de Q&A
        """
        print(f"❓ Respondendo pergunta: {question[:50]}...")
        
        # Usar LLM monitorado
        prompt = f"""
        Contexto: {context[:500]}...
        
        Pergunta: {question}
        
        Por favor, responda baseado no contexto fornecido.
        """
        
        # Chamar LLM (que já está monitorado)
        if "huggingface" in model_name.lower():
            answer = self.llm_manager.generate_with_huggingface(prompt, model_name)
        else:
            answer = self.llm_manager.generate_with_ollama(prompt, model_name)
        
        print(f"✅ Pergunta respondida!")
        return answer
    
    @monitor_complete_operation(
        operation_type="pdf_qa_pipeline"
    )
    def process_pdf_and_answer(self, pdf_path: str, question: str, model_name: str = "llama2:7b") -> Dict[str, Any]:
        """
        Pipeline completo: PDF → Texto → Resposta
        Monitora a operação completa end-to-end
        """
        print(f"🔄 Iniciando pipeline completo...")
        
        result = {
            "pdf_path": pdf_path,
            "question": question, 
            "model_name": model_name,
            "timestamp": time.time()
        }
        
        try:
            # Passo 1: Extrair texto
            print("📄 Passo 1: Extraindo texto do PDF...")
            extracted_text = self.extract_text_from_pdf(pdf_path)
            result["extracted_text"] = extracted_text
            result["extraction_success"] = True
            
            # Passo 2: Responder pergunta
            print("🤖 Passo 2: Gerando resposta...")
            answer = self.answer_question(question, extracted_text, model_name)
            result["answer"] = answer
            result["qa_success"] = True
            
            # Métricas finais
            result["total_time"] = time.time() - result["timestamp"]
            result["success"] = True
            
            print(f"🎉 Pipeline concluído com sucesso em {result['total_time']:.2f}s!")
            
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
            result["total_time"] = time.time() - result["timestamp"]
            print(f"❌ Erro no pipeline: {e}")
        
        return result

# ====================================================================
# EXEMPLO 3: Simulação de Streamlit App monitorado
# ====================================================================

@monitor_complete_operation(operation_type="streamlit_session")
def simulate_streamlit_interaction(pdf_file: str, user_question: str, selected_model: str) -> Dict[str, Any]:
    """
    Simula uma interação completa do usuário no Streamlit
    """
    print(f"🖥️ Simulando sessão Streamlit...")
    print(f"   📁 Arquivo: {pdf_file}")
    print(f"   ❓ Pergunta: {user_question}")
    print(f"   🤖 Modelo: {selected_model}")
    
    # Inicializar componentes
    llm_manager = LocalLLMManagerMonitored()
    orchestrator = PDFOrchestratorMonitored(llm_manager)
    
    # Processar com monitoramento completo
    result = orchestrator.process_pdf_and_answer(
        pdf_path=pdf_file,
        question=user_question,
        model_name=selected_model
    )
    
    return result

# ====================================================================
# EXEMPLO 4: Testes e Demonstração
# ====================================================================

def test_llm_monitoring():
    """Testa monitoramento de LLM isoladamente"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Monitoramento de LLM")
    print("="*60)
    
    llm = LocalLLMManagerMonitored()
    
    # Testar múltiplos modelos
    test_cases = [
        ("llama2:7b", "ollama", "Qual é a capital do Brasil?"),
        ("llama2:13b", "ollama", "Explique machine learning de forma simples"),
        ("microsoft/DialoGPT-medium", "huggingface", "Como funciona um transformer?")
    ]
    
    for model, provider, prompt in test_cases:
        try:
            print(f"\n🔍 Testando {model} via {provider}")
            
            if provider == "ollama":
                response = llm.generate_with_ollama(prompt, model)
            else:
                response = llm.generate_with_huggingface(prompt, model)
                
            print(f"📝 Resposta obtida: {len(response)} caracteres")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

def test_pdf_monitoring():
    """Testa monitoramento de PDF isoladamente"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Monitoramento de PDF")
    print("="*60)
    
    llm = LocalLLMManagerMonitored()
    orchestrator = PDFOrchestratorMonitored(llm)
    
    # Testar diferentes PDFs
    test_pdfs = [
        "manual_usuario.pdf",
        "relatorio_anual.pdf", 
        "artigo_cientifico.pdf"
    ]
    
    for pdf_file in test_pdfs:
        try:
            print(f"\n📄 Processando: {pdf_file}")
            text = orchestrator.extract_text_from_pdf(pdf_file)
            print(f"✅ Texto extraído: {len(text)} caracteres")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

def test_qa_monitoring():
    """Testa monitoramento de Q&A"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: Monitoramento de Q&A")
    print("="*60)
    
    llm = LocalLLMManagerMonitored()
    orchestrator = PDFOrchestratorMonitored(llm)
    
    # Contexto simulado
    context = """
    O sistema de monitoramento LLM PDF Reading foi desenvolvido para
    fornecer observabilidade completa sobre operações de processamento
    de documentos e geração de respostas. Ele inclui métricas de
    performance, rastreamento de experimentos com MLflow, e alertas
    em tempo real.
    """
    
    # Perguntas de teste
    questions = [
        "O que é o sistema de monitoramento?",
        "Quais funcionalidades estão incluídas?",
        "Como funciona o MLflow?",
    ]
    
    for question in questions:
        try:
            print(f"\n❓ Pergunta: {question}")
            answer = orchestrator.answer_question(question, context)
            print(f"✅ Resposta gerada")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

def test_complete_pipeline():
    """Testa pipeline completo"""
    print("\n" + "="*60)
    print("🧪 TESTE 4: Pipeline Completo")
    print("="*60)
    
    # Cenários de teste
    scenarios = [
        {
            "pdf": "documento_tecnico.pdf",
            "question": "Quais são as principais conclusões do documento?",
            "model": "llama2:7b"
        },
        {
            "pdf": "manual_instrucoes.pdf", 
            "question": "Como configurar o sistema?",
            "model": "mistral:7b"
        },
        {
            "pdf": "relatorio_financeiro.pdf",
            "question": "Qual foi o resultado do trimestre?",
            "model": "microsoft/DialoGPT-medium"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎬 Cenário {i}:")
        try:
            result = simulate_streamlit_interaction(
                scenario["pdf"],
                scenario["question"], 
                scenario["model"]
            )
            
            if result["success"]:
                print(f"✅ Pipeline executado com sucesso em {result['total_time']:.2f}s")
            else:
                print(f"❌ Pipeline falhou: {result.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

def show_monitoring_status():
    """Mostra status atual do monitoramento"""
    print("\n" + "="*60)
    print("📊 STATUS DO MONITORAMENTO")
    print("="*60)
    
    from llm_pdf_reading.monitoring import model_monitor
    
    # Status geral
    status = model_monitor.get_system_status()
    print(f"🟢 Monitoramento ativo: {status['monitoring_active']}")
    print(f"⏱️ Tempo ativo: {status['uptime_formatted']}")
    print(f"📊 Disponibilidade: {status['availability']:.1%}")
    print(f"⚡ Tempo médio: {status['avg_response_time']:.2f}s")
    print(f"📈 Total de requisições: {status['total_requests']}")
    
    # Métricas em tempo real
    metrics = model_monitor.get_real_time_metrics()
    print(f"\n🤖 Modelos monitorados: {len(metrics['model_states'])}")
    
    for model_name, state in metrics['model_states'].items():
        print(f"   - {model_name}: {state['total_requests']} req, {state['avg_response_time']:.2f}s avg")

def main():
    """Função principal de demonstração"""
    print("🚀 DEMONSTRAÇÃO DE INTEGRAÇÃO COM CÓDIGO EXISTENTE")
    print("="*70)
    print("Este exemplo mostra como integrar o monitoramento aos seus")
    print("códigos existentes usando decoradores.")
    print("="*70)
    
    try:
        # Executar testes sequenciais
        test_llm_monitoring()
        test_pdf_monitoring() 
        test_qa_monitoring()
        test_complete_pipeline()
        
        # Mostrar status final
        show_monitoring_status()
        
        print("\n" + "="*70)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print("\n📋 Como aplicar ao seu código:")
        print("1. Importe os decoradores:")
        print("   from llm_pdf_reading.monitoring.decorators import monitor_llm_operation")
        print("\n2. Aplique aos seus métodos:")
        print("   @monitor_llm_operation(model_name='seu_modelo', provider='ollama')")
        print("   def sua_funcao_existente(...):")
        print("       # Código inalterado")
        print("       return resultado")
        print("\n3. Inicie o monitoramento:")
        print("   from llm_pdf_reading.monitoring import model_monitor")
        print("   model_monitor.start_monitoring()")
        print("\n4. Veja os resultados:")
        print("   - Dashboard: streamlit run dashboard.py")
        print("   - MLflow: mlflow ui")
        print("   - Status: model_monitor.get_system_status()")
        
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
