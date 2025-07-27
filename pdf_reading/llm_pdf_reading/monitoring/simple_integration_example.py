#!/usr/bin/env python3
"""
Exemplo simples de integração com código existente
"""

import sys
import time
import random
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importar decoradores de monitoramento
from llm_pdf_reading.monitoring.decorators import (
    monitor_llm_operation,
    monitor_pdf_operation,
    monitor_complete_operation
)

# Iniciar sistema de monitoramento
from llm_pdf_reading.monitoring import model_monitor

def init_monitoring():
    """Inicializa o sistema de monitoramento"""
    if not model_monitor.is_monitoring:
        model_monitor.start_monitoring()
        print("🚀 Sistema de monitoramento iniciado!")
    else:
        print("✅ Sistema de monitoramento já ativo!")

# ====================================================================
# EXEMPLO 1: Função LLM Simples com Monitoramento
# ====================================================================

@monitor_llm_operation(
    model_name="llama2:7b",
    provider="ollama"
)
def generate_text_ollama(prompt: str) -> str:
    """
    Exemplo de função que gera texto com Ollama
    O decorador automaticamente monitora:
    - Tempo de execução
    - Sucesso/falha
    - Métricas LLM
    - Log no MLflow
    """
    print(f"🤖 Gerando texto com Ollama para: {prompt[:50]}...")
    
    # Simular processamento
    processing_time = random.uniform(0.5, 2.0)
    time.sleep(processing_time)
    
    # Simular possível falha (5% de chance)
    if random.random() < 0.05:
        raise Exception("Erro simulado na geração")
    
    response = f"Resposta do Ollama para '{prompt}' (processado em {processing_time:.2f}s)"
    print(f"✅ Texto gerado com sucesso!")
    return response

@monitor_llm_operation(
    model_name="gpt-3.5-turbo",
    provider="openai"
)
def generate_text_openai(prompt: str) -> str:
    """
    Exemplo de função que gera texto com OpenAI
    """
    print(f"🧠 Gerando texto com OpenAI para: {prompt[:50]}...")
    
    # Simular processamento diferente
    processing_time = random.uniform(0.3, 1.5)
    time.sleep(processing_time)
    
    # Simular falha ocasional (3% de chance)
    if random.random() < 0.03:
        raise Exception("Rate limit exceeded")
    
    response = f"Resposta do OpenAI para '{prompt}' (processado em {processing_time:.2f}s)"
    print(f"✅ OpenAI resposta gerada!")
    return response

# ====================================================================
# EXEMPLO 2: Função PDF Simples com Monitoramento
# ====================================================================

@monitor_pdf_operation()
def extract_pdf_text(pdf_path: str) -> str:
    """
    Exemplo de função que extrai texto de PDF
    O decorador monitora automaticamente a operação
    """
    print(f"📄 Extraindo texto de: {pdf_path}")
    
    # Simular extração
    extraction_time = random.uniform(0.2, 1.0)
    time.sleep(extraction_time)
    
    # Simular falha ocasional (2% de chance)
    if random.random() < 0.02:
        raise Exception(f"Erro ao ler PDF: {pdf_path}")
    
    extracted_text = f"""
    Texto extraído do arquivo: {pdf_path}
    
    Este é um documento de exemplo processado pelo sistema.
    O texto foi extraído em {extraction_time:.2f} segundos.
    
    Conteúdo simulado do documento...
    - Seção 1: Introdução
    - Seção 2: Desenvolvimento  
    - Seção 3: Conclusão
    """
    
    print(f"✅ Texto extraído: {len(extracted_text)} caracteres")
    return extracted_text.strip()

# ====================================================================
# EXEMPLO 3: Pipeline Completo com Monitoramento
# ====================================================================

@monitor_complete_operation(operation_type="pdf_qa_complete")
def process_document_qa(pdf_path: str, question: str, model_provider: str = "ollama") -> dict:
    """
    Pipeline completo: PDF → Texto → Resposta
    O decorador monitora toda a operação end-to-end
    """
    print(f"🔄 Iniciando pipeline: {pdf_path} + '{question}' via {model_provider}")
    
    result = {
        "pdf_path": pdf_path,
        "question": question,
        "model_provider": model_provider,
        "start_time": time.time()
    }
    
    try:
        # Passo 1: Extrair texto do PDF
        print("📖 Passo 1: Extraindo texto...")
        extracted_text = extract_pdf_text(pdf_path)
        result["extracted_text"] = extracted_text[:200] + "..." # Resumo
        result["extraction_success"] = True
        
        # Passo 2: Gerar resposta
        print("🤖 Passo 2: Gerando resposta...")
        prompt = f"Baseado no texto: {extracted_text[:500]}...\n\nPergunta: {question}"
        
        if model_provider == "openai":
            answer = generate_text_openai(prompt)
        else:
            answer = generate_text_ollama(prompt)
            
        result["answer"] = answer
        result["qa_success"] = True
        result["success"] = True
        
        # Calcular tempo total
        result["total_time"] = time.time() - result["start_time"]
        
        print(f"🎉 Pipeline concluído com sucesso em {result['total_time']:.2f}s!")
        
    except Exception as e:
        result["error"] = str(e)
        result["success"] = False
        result["total_time"] = time.time() - result["start_time"]
        print(f"❌ Erro no pipeline: {e}")
    
    return result

# ====================================================================
# TESTES E DEMONSTRAÇÃO
# ====================================================================

def test_llm_monitoring():
    """Testa monitoramento de LLM"""
    print("\n" + "="*50)
    print("🧪 TESTE: Monitoramento de LLM")
    print("="*50)
    
    test_prompts = [
        "Qual é a capital do Brasil?",
        "Explique o que é inteligência artificial",
        "Como funciona um algoritmo de machine learning?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Teste {i}: {prompt}")
        
        try:
            # Testar Ollama
            response_ollama = generate_text_ollama(prompt)
            print(f"   Ollama: {len(response_ollama)} caracteres")
            
            # Testar OpenAI (1 em 3 testes)
            if i % 3 == 0:
                response_openai = generate_text_openai(prompt)
                print(f"   OpenAI: {len(response_openai)} caracteres")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def test_pdf_monitoring():
    """Testa monitoramento de PDF"""
    print("\n" + "="*50)
    print("🧪 TESTE: Monitoramento de PDF")
    print("="*50)
    
    test_files = [
        "documento1.pdf",
        "relatorio.pdf", 
        "manual.pdf"
    ]
    
    for pdf_file in test_files:
        print(f"\n📄 Processando: {pdf_file}")
        try:
            text = extract_pdf_text(pdf_file)
            print(f"   ✅ Sucesso: {len(text)} caracteres")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def test_complete_pipeline():
    """Testa pipeline completo"""
    print("\n" + "="*50)
    print("🧪 TESTE: Pipeline Completo")
    print("="*50)
    
    scenarios = [
        {
            "pdf": "documento_tecnico.pdf",
            "question": "Quais são as principais conclusões?",
            "provider": "ollama"
        },
        {
            "pdf": "relatorio_vendas.pdf",
            "question": "Qual foi o resultado do trimestre?",
            "provider": "openai"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎬 Cenário {i}: {scenario['pdf']}")
        try:
            result = process_document_qa(
                scenario["pdf"],
                scenario["question"],
                scenario["provider"]
            )
            
            if result["success"]:
                print(f"   ✅ Sucesso em {result['total_time']:.2f}s")
            else:
                print(f"   ❌ Falhou: {result.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            print(f"   💥 Erro inesperado: {e}")

def show_monitoring_summary():
    """Mostra resumo do monitoramento"""
    print("\n" + "="*50)
    print("📊 RESUMO DO MONITORAMENTO")
    print("="*50)
    
    try:
        # Status geral
        status = model_monitor.get_system_status()
        print(f"📈 Total de requisições: {status['total_requests']}")
        print(f"📊 Disponibilidade: {status['availability']:.1%}")
        print(f"⚡ Tempo médio: {status['avg_response_time']:.2f}s")
        print(f"⏱️ Tempo ativo: {status['uptime_formatted']}")
        
        # Modelos monitorados
        metrics = model_monitor.get_real_time_metrics()
        print(f"\n🤖 Modelos monitorados: {len(metrics['model_states'])}")
        
        for model_name, state in metrics['model_states'].items():
            if state['total_requests'] > 0:
                print(f"   - {model_name}: {state['total_requests']} req, {state['avg_response_time']:.2f}s")
                
    except Exception as e:
        print(f"❌ Erro ao obter status: {e}")

def main():
    """Função principal de demonstração"""
    print("🚀 EXEMPLO DE INTEGRAÇÃO COM CÓDIGO EXISTENTE")
    print("="*60)
    print("Este exemplo mostra como adicionar monitoramento")
    print("ao seu código existente usando apenas decoradores!")
    print("="*60)
    
    # Inicializar monitoramento
    init_monitoring()
    
    try:
        # Executar testes
        test_llm_monitoring()
        test_pdf_monitoring()
        test_complete_pipeline()
        
        # Mostrar resumo
        show_monitoring_summary()
        
        print("\n" + "="*60)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("="*60)
        print("\n📋 Para aplicar ao seu código:")
        print("1. Adicione o decorador:")
        print("   @monitor_llm_operation(model_name='seu_modelo', provider='ollama')")
        print("   def sua_funcao(...):")
        print("       return resultado")
        print("\n2. Inicie o monitoramento:")
        print("   from llm_pdf_reading.monitoring import model_monitor")
        print("   model_monitor.start_monitoring()")
        print("\n3. Visualize os resultados:")
        print("   - Dashboard: streamlit run dashboard.py")
        print("   - MLflow: mlflow ui")
        print("   - Status: model_monitor.get_system_status()")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ Teste de integração executado com sucesso!")
    else:
        print("\n💥 Falha no teste de integração!")
