#!/usr/bin/env python3
"""
Script para iniciar o sistema de monitoramento
Execute este script no início da sua aplicação
"""

import sys
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from llm_pdf_reading.monitoring import model_monitor, experiment_manager

def start_monitoring():
    """Inicia o sistema de monitoramento"""
    print("🚀 Iniciando sistema de monitoramento...")
    
    # Configurar alertas
    def on_high_response_time(model_name: str, response_time: float):
        print(f"⚠️ ALERTA: {model_name} - Tempo alto: {response_time:.2f}s")
    
    def on_model_error(model_name: str, error: str):
        print(f"❌ ERRO: {model_name} - {error}")
    
    # Registrar callbacks
    model_monitor.add_alert_callback("high_response_time", on_high_response_time)
    model_monitor.add_alert_callback("model_error", on_model_error)
    
    # Iniciar monitoramento
    model_monitor.start_monitoring()
    print("✅ Monitoramento de modelos iniciado")
    
    # Iniciar sessão MLflow (se disponível)
    if experiment_manager.mlflow_available:
        run_id = experiment_manager.start_run(
            run_name="monitoring_session",
            tags={
                "project": "llm_pdf_reading",
                "environment": "development",
                "auto_started": "true"
            }
        )
        print(f"📊 Sessão MLflow iniciada: {run_id}")
    
    print("🎯 Sistema de monitoramento pronto!")
    return True

if __name__ == "__main__":
    start_monitoring()
