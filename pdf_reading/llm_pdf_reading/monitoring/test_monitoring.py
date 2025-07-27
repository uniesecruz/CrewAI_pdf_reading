#!/usr/bin/env python3
"""
Teste básico do sistema de monitoramento
"""

import sys
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_monitoring():
    """Testa o sistema de monitoramento básico"""
    print("🔍 Testando sistema de monitoramento...")
    
    try:
        # Importar módulos
        from llm_pdf_reading.monitoring import (
            model_monitor,
            performance_tracker,
            experiment_manager,
            metrics_collector
        )
        print("✅ Módulos importados com sucesso")
        
        # Testar coleta de métricas
        system_metrics = metrics_collector.collect_system_metrics()
        print(f"✅ Métricas coletadas - CPU: {system_metrics.cpu_usage:.1f}%")
        
        # Testar performance tracker
        with performance_tracker.track_operation("test_operation"):
            import time
            time.sleep(0.1)
        print("✅ Performance tracker funcionando")
        
        # Testar registro de modelo
        model_monitor.record_request(
            success=True,
            response_time=1.5,
            model_name="test_model"
        )
        print("✅ Registro de modelo funcionando")
        
        # Verificar status
        status = model_monitor.get_system_status()
        print(f"✅ Status do sistema obtido - Disponibilidade: {status['availability']:.1%}")
        
        # Testar MLflow (se disponível)
        if experiment_manager.mlflow_available:
            print("✅ MLflow disponível")
        else:
            print("⚠️ MLflow não disponível")
        
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_decorators():
    """Testa os decoradores de monitoramento"""
    print("\n🔍 Testando decoradores...")
    
    try:
        from llm_pdf_reading.monitoring.decorators import monitor_llm_operation
        
        @monitor_llm_operation(
            model_name="llama2:7b",
            provider="ollama"
        )
        def test_llm_function(prompt: str):
            """Função de teste para LLM"""
            import time
            time.sleep(0.2)  # Simular processamento
            return f"Resposta para: {prompt}"
        
        # Testar a função decorada
        result = test_llm_function("Como você está?")
        print(f"✅ Decorator LLM funcionando - Resultado: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos decoradores: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTES DO SISTEMA DE MONITORAMENTO")
    print("="*60)
    
    # Executar testes
    basic_test = test_monitoring()
    decorator_test = test_decorators()
    
    print("\n" + "="*60)
    if basic_test and decorator_test:
        print("🎉 SISTEMA DE MONITORAMENTO FUNCIONANDO PERFEITAMENTE!")
        print("\n📋 Próximos passos:")
        print("1. 🚀 Para usar no seu código: python start_monitoring.py")
        print("2. 📱 Para abrir dashboard: streamlit run dashboard.py")
        print("3. 📊 Para MLflow UI: mlflow ui")
        print("4. 🔗 Aplicar decoradores nos seus códigos existentes")
    else:
        print("💥 ALGUNS TESTES FALHARAM - Verifique os erros acima")
    
    return basic_test and decorator_test

if __name__ == "__main__":
    main()
