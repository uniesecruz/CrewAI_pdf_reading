#!/usr/bin/env python3
"""
Script simples para abrir o dashboard do MLflow
"""

import webbrowser
import time
import requests
import sys

def open_mlflow_dashboard():
    """Abre o dashboard do MLflow no navegador"""
    
    # URL do MLflow UI
    mlflow_url = "http://127.0.0.1:5001"
    
    # Verificar se o MLflow está rodando
    try:
        response = requests.get(mlflow_url, timeout=5)
        if response.status_code == 200:
            print("✅ MLflow UI está rodando corretamente!")
            print(f"🌐 Abrindo dashboard em: {mlflow_url}")
            
            # Abrir no navegador
            webbrowser.open(mlflow_url)
            
            print("\n📊 Dashboard do MLflow aberto com sucesso!")
            print("Você pode visualizar:")
            print("- Experimentos de análise de PDFs")
            print("- Métricas de desempenho dos modelos")
            print("- Comparações de temas detectados")
            print("- Histórico de execuções")
            
        else:
            print("❌ MLflow UI não está respondendo corretamente")
            
    except requests.exceptions.RequestException as e:
        print("❌ Erro ao conectar com o MLflow UI:")
        print(f"   {e}")
        print("\n💡 Certifique-se de que o MLflow UI está rodando:")
        print("   mlflow ui --host 127.0.0.1 --port 5001")

if __name__ == "__main__":
    open_mlflow_dashboard()
