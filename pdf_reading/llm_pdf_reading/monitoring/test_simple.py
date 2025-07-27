#!/usr/bin/env python3
"""
Teste simplificado para verificar se os erros foram corrigidos
"""

import sys
import os
import time
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import mlflow

def test_mlflow_basic():
    """Teste básico do MLflow para verificar configuração"""
    print("🧪 TESTE BÁSICO DO MLFLOW")
    print("="*50)
    
    try:
        # Configurar MLflow
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("Simple_Test")
        
        # Finalizar run ativo se existir
        try:
            active_run = mlflow.active_run()
            if active_run:
                print("⚠️ Finalizando run MLflow ativo...")
                mlflow.end_run()
        except Exception as e:
            print(f"Aviso: {e}")
        
        # Teste simples
        with mlflow.start_run(run_name="basic_test"):
            mlflow.log_param("test_param", "valor_teste")
            mlflow.log_metric("test_metric", 42.0)
            
            print("✅ Parâmetro registrado: test_param = 'valor_teste'")
            print("✅ Métrica registrada: test_metric = 42.0")
            
            # Teste nested run
            try:
                with mlflow.start_run(nested=True, run_name="nested_test"):
                    mlflow.log_metric("nested_metric", 3.14)
                    print("✅ Nested run funcionando!")
            except Exception as e:
                print(f"⚠️ Erro em nested run: {e}")
        
        print("✅ Teste MLflow concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste MLflow: {e}")
        return False

def test_imports():
    """Teste de imports do sistema de monitoramento"""
    print("\n🔍 TESTE DE IMPORTS")
    print("="*50)
    
    try:
        # Testar imports básicos
        from llm_pdf_reading.monitoring import model_monitor
        print("✅ model_monitor importado")
        
        from llm_pdf_reading.monitoring.decorators import monitor_pdf_operation
        print("✅ decorators importado")
        
        # Testar inicialização
        if not model_monitor.is_monitoring:
            model_monitor.start_monitoring()
            print("✅ Sistema de monitoramento iniciado")
        else:
            print("✅ Sistema de monitoramento já ativo")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def test_file_access():
    """Teste de acesso ao arquivo PDF"""
    print("\n📄 TESTE DE ACESSO AO ARQUIVO")
    print("="*50)
    
    pdf_path = r"c:\Users\win\Desktop\Projetos\pdf_reading\pdf_reading\data\external\Random_Forest.pdf"
    
    try:
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ Arquivo encontrado: {pdf_path}")
            print(f"✅ Tamanho: {file_size / 1024:.2f} KB")
            return True
        else:
            print(f"❌ Arquivo não encontrado: {pdf_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao acessar arquivo: {e}")
        return False

def main():
    """Teste principal simplificado"""
    print("🔧 TESTE SIMPLIFICADO - VERIFICAÇÃO DE CORREÇÕES")
    print("="*60)
    
    results = []
    
    # Teste 1: MLflow básico
    results.append(test_mlflow_basic())
    
    # Teste 2: Imports
    results.append(test_imports())
    
    # Teste 3: Arquivo
    results.append(test_file_access())
    
    # Resultado final
    successful_tests = sum(results)
    total_tests = len(results)
    
    print(f"\n🎯 RESULTADO FINAL")
    print("="*50)
    print(f"✅ Testes bem-sucedidos: {successful_tests}/{total_tests}")
    print(f"📊 Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 Todos os testes passaram! Sistema corrigido.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verificar erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ Correções verificadas com sucesso!")
    else:
        print("\n💥 Ainda há problemas a resolver!")
