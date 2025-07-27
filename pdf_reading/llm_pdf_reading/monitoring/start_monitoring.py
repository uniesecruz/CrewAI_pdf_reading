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
    def on_alert(alert: dict):
        alert_type = alert.get('type', 'unknown')
        message = alert.get('message', 'Alerta desconhecido')
        severity = alert.get('severity', 'info')
        
        if severity == 'critical':
            print(f"🚨 CRÍTICO: {message}")
        elif severity == 'warning':
            print(f"⚠️ ALERTA: {message}")
        else:
            print(f"ℹ️ INFO: {message}")
    
    # Registrar callback de alerta
    model_monitor.register_alert_callback(on_alert)
    
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
