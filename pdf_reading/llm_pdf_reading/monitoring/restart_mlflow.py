#!/usr/bin/env python3
"""
Script para reiniciar o MLflow UI de forma limpa
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def stop_mlflow_processes():
    """
    Para todos os processos MLflow rodando
    """
    print("🛑 Parando processos MLflow existentes...")
    
    try:
        # No Windows, usar taskkill
        if os.name == 'nt':
            # Parar processos MLflow
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'IMAGENAME eq python.exe'], 
                         capture_output=True, text=True)
            time.sleep(2)
        else:
            # Linux/Mac
            subprocess.run(['pkill', '-f', 'mlflow'], capture_output=True)
        
        print("✅ Processos MLflow parados")
        
    except Exception as e:
        print(f"⚠️ Erro ao parar processos: {e}")

def check_port_available(port=5000):
    """
    Verifica se a porta está disponível
    """
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        if f":{port}" in result.stdout:
            print(f"⚠️ Porta {port} ainda em uso")
            return False
        else:
            print(f"✅ Porta {port} disponível")
            return True
    except:
        return True

def start_mlflow_ui():
    """
    Inicia o MLflow UI de forma limpa
    """
    print("🚀 Iniciando MLflow UI...")
    
    # Verificar se estamos no diretório correto
    current_dir = Path.cwd()
    monitoring_dir = current_dir / "llm_pdf_reading" / "monitoring"
    
    # Mudar para o diretório de monitoramento se existir
    if monitoring_dir.exists():
        os.chdir(monitoring_dir)
        print(f"📁 Mudando para: {monitoring_dir}")
    
    # Verificar se o banco MLflow existe
    mlflow_db = Path("mlflow.db")
    if mlflow_db.exists():
        print(f"✅ Banco MLflow encontrado: {mlflow_db}")
    else:
        print("⚠️ Banco MLflow não encontrado - será criado automaticamente")
    
    try:
        # Comando para iniciar MLflow UI
        cmd = [
            'mlflow', 'ui', 
            '--host', '127.0.0.1',  # Usar localhost ao invés de 0.0.0.0
            '--port', '5000',
            '--backend-store-uri', 'sqlite:///mlflow.db'
        ]
        
        print(f"📝 Executando: {' '.join(cmd)}")
        
        # Iniciar o processo
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("⏳ Aguardando MLflow UI iniciar...")
        
        # Aguardar e mostrar saída
        lines_shown = 0
        for line in process.stdout:
            if lines_shown < 10:  # Limitar número de linhas mostradas
                print(f"   {line.strip()}")
                lines_shown += 1
            
            # Verificar se o servidor iniciou
            if "Serving on" in line:
                print("\n✅ MLflow UI iniciado com sucesso!")
                print("🌐 Acesse: http://localhost:5000")
                print("⏹️ Para parar: Ctrl+C ou feche o terminal")
                break
        
        # Aguardar o processo (mantém rodando)
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ Parando MLflow UI...")
            process.terminate()
            process.wait()
            print("✅ MLflow UI parado.")
            
    except FileNotFoundError:
        print("❌ MLflow não encontrado!")
        print("💡 Instale com: pip install mlflow")
        return False
    except Exception as e:
        print(f"❌ Erro ao iniciar MLflow UI: {e}")
        return False
    
    return True

def main():
    """
    Função principal
    """
    print("🔄 REINICIALIZADOR DO MLFLOW UI")
    print("="*50)
    
    # Parar processos existentes
    stop_mlflow_processes()
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Verificar porta
    if not check_port_available(5000):
        print("⚠️ Porta 5000 ainda ocupada, tentando parar...")
        time.sleep(3)
    
    # Iniciar MLflow UI
    start_mlflow_ui()

if __name__ == "__main__":
    main()
