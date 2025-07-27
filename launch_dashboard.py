#!/usr/bin/env python3
"""
Script para inicializar o dashboard de monitoramento
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def launch_dashboard():
    """
    Inicia o dashboard de monitoramento
    """
    print("🚀 INICIANDO DASHBOARD DE MONITORAMENTO")
    print("="*50)
    
    # Verificar se o arquivo dashboard.py existe
    dashboard_file = Path("dashboard.py")
    if not dashboard_file.exists():
        # Procurar na pasta de monitoramento
        monitoring_path = Path("llm_pdf_reading/monitoring/dashboard.py")
        if monitoring_path.exists():
            dashboard_file = monitoring_path
        else:
            print("❌ Arquivo dashboard.py não encontrado!")
            print("💡 Certifique-se de que o dashboard foi criado.")
            return False
    
    print(f"📊 Dashboard encontrado: {dashboard_file}")
    
    try:
        # Iniciar o dashboard com Streamlit
        print("🌐 Iniciando Streamlit...")
        
        # Comando para iniciar o streamlit
        cmd = ["streamlit", "run", str(dashboard_file), "--server.port", "8501"]
        
        print(f"📝 Executando: {' '.join(cmd)}")
        
        # Iniciar o processo
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar um pouco para o servidor iniciar
        time.sleep(3)
        
        # Verificar se o processo está rodando
        if process.poll() is None:
            print("✅ Dashboard iniciado com sucesso!")
            print("🌐 Acesse: http://localhost:8501")
            print("⏹️ Para parar: Ctrl+C")
            
            # Aguardar o processo terminar
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n⏹️ Parando dashboard...")
                process.terminate()
                process.wait()
                print("✅ Dashboard parado.")
        else:
            # Processo falhou
            stdout, stderr = process.communicate()
            print("❌ Falha ao iniciar dashboard!")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Streamlit não encontrado!")
        print("💡 Instale com: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")
        return False
    
    return True

def check_dependencies():
    """
    Verifica se as dependências estão instaladas
    """
    print("🔍 Verificando dependências...")
    
    try:
        import streamlit
        print("✅ Streamlit instalado")
    except ImportError:
        print("❌ Streamlit não instalado")
        print("💡 Execute: pip install streamlit")
        return False
    
    return True

def main():
    """
    Função principal
    """
    print("📊 LAUNCHER DO DASHBOARD DE MONITORAMENTO")
    print("="*60)
    
    # Verificar dependências
    if not check_dependencies():
        return
    
    # Iniciar dashboard
    success = launch_dashboard()
    
    if success:
        print("\n✅ Dashboard encerrado com sucesso!")
    else:
        print("\n❌ Falha ao iniciar dashboard!")

if __name__ == "__main__":
    main()
