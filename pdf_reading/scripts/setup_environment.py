"""
Script para configurar o ambiente de desenvolvimento
"""
import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False
    return True

def check_env_file():
    """Verifica se o arquivo .env existe e tem as configurações necessárias"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return False
    
    # Ler conteúdo do .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if f"{key}=your_" in content:
            missing_keys.append(key)
    
    if missing_keys:
        print("⚠️  Configure as seguintes chaves de API no arquivo .env:")
        for key in missing_keys:
            print(f"   - {key}")
        return False
    
    print("✅ Arquivo .env configurado!")
    return True

def create_data_directories():
    """Cria diretórios de dados necessários"""
    dirs = [
        "data/raw",
        "data/processed", 
        "data/interim",
        "data/external",
        "models",
        "reports/figures"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Diretórios de dados criados!")

def main():
    """Função principal de setup"""
    print("🚀 Configurando ambiente LLM PDF Reading")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("pyproject.toml").exists():
        print("❌ Execute este script no diretório raiz do projeto!")
        return
    
    # Criar diretórios
    create_data_directories()
    
    # Instalar dependências
    if not install_requirements():
        return
    
    # Verificar configurações
    env_ok = check_env_file()
    
    print("\n" + "=" * 50)
    if env_ok:
        print("🎉 Setup completo! Você pode começar a usar o sistema.")
        print("💡 Para testar: python examples/basic_usage.py")
        print("🌐 Para interface web: python -m streamlit run apps/streamlit_app.py")
    else:
        print("⚠️  Setup parcialmente completo. Configure as API keys no .env")

if __name__ == "__main__":
    main()
