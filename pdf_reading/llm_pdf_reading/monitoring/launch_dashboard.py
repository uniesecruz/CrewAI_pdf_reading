#!/usr/bin/env python3
"""
Script para lançar o dashboard de monitoramento
"""

import sys
import subprocess
from pathlib import Path

def launch_dashboard():
    """Lança o dashboard Streamlit"""
    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit não instalado")
        print("📦 Instale com: pip install streamlit plotly pandas")
        return False
    
    dashboard_path = Path(__file__).parent / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard não encontrado: {dashboard_path}")
        return False
    
    print("🚀 Lançando dashboard...")
    print("📱 O dashboard abrirá no seu navegador")
    print("🔗 URL: http://localhost:8501")
    print("⏹️ Pressione Ctrl+C para parar")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("
✅ Dashboard encerrado")
    except Exception as e:
        print(f"❌ Erro ao lançar dashboard: {e}")
        return False
    
    return True

if __name__ == "__main__":
    launch_dashboard()
