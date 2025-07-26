"""
Setup automático para LLMs locais gratuitos
Script universal (Windows/Linux/Mac)
"""
import subprocess
import sys
import os
import platform
from pathlib import Path

def print_header():
    """Imprime cabeçalho do setup"""
    print("\n" + "=" * 60)
    print("   🤖 LLM PDF Reading - Setup Modelos Locais")
    print("   🎯 100% Gratuito usando GPU local!")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    print(f"🐍 Python detectado: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ requerido!")
        return False
    
    print("✅ Versão do Python compatível")
    return True

def check_project_structure():
    """Verifica estrutura do projeto"""
    print("🔍 Verificando estrutura do projeto...")
    
    # Navegar para diretório do projeto
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    print(f"📁 Diretório atual: {project_dir}")
    
    required_files = ["requirements.txt", "pyproject.toml"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Arquivo {file} não encontrado!")
            return False
    
    print("✅ Estrutura do projeto verificada")
    return True

def install_dependencies():
    """Instala dependências do projeto"""
    print("\n📦 Instalando dependências Python...")
    
    try:
        # Atualizar pip primeiro
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instalar dependências
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        
        print("✅ Dependências instaladas com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Erro ao instalar dependências!")
        print("\n💡 Possíveis soluções:")
        print("   1. Ative o ambiente virtual")
        print("   2. Verifique se o Python está no PATH")
        print("   3. Execute como administrador")
        print(f"   4. Erro: {e}")
        return False

def detect_gpu():
    """Detecta GPU disponível"""
    print("\n🔍 Verificando GPU...")
    
    gpu_info = {"nvidia": False, "cuda": False}
    
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            gpu_info["nvidia"] = True
            print("✅ GPU NVIDIA detectada!")
    except FileNotFoundError:
        print("⚠️  GPU NVIDIA não detectada")
    
    return gpu_info

def install_pytorch(gpu_info):
    """Instala PyTorch baseado na GPU"""
    print("\n📦 Instalando PyTorch...")
    
    try:
        if gpu_info["nvidia"]:
            print("📥 Instalando PyTorch com CUDA...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "torch", "torchvision", "torchaudio", 
                "--index-url", "https://download.pytorch.org/whl/cu121"
            ], check=True)
        else:
            print("📥 Instalando PyTorch CPU...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "torch", "torchvision", "torchaudio"
            ], check=True)
        
        print("✅ PyTorch instalado com sucesso!")
        return True
        
    except subprocess.CalledProcessError:
        print("⚠️  Erro ao instalar PyTorch, mas continuando...")
        return False

def setup_ollama():
    """Configura Ollama"""
    print("\n🦙 Verificando Ollama...")
    
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama detectado!")
            
            # Tentar baixar modelo
            print("📥 Baixando modelo llama2:7b...")
            try:
                subprocess.run(["ollama", "pull", "llama2:7b"], check=True, timeout=300)
                print("✅ Modelo llama2:7b baixado!")
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print("⚠️  Erro ao baixar modelo, mas Ollama está instalado")
                return True
    except FileNotFoundError:
        pass
    
    print("❌ Ollama não encontrado")
    print("\n💡 Para instalar Ollama:")
    
    system = platform.system().lower()
    if system == "windows":
        print("   1. Baixe: https://ollama.ai/download/windows")
        print("   2. Execute o instalador")
    elif system == "darwin":
        print("   1. Baixe: https://ollama.ai/download/mac")
        print("   2. Ou use: brew install ollama")
    else:
        print("   1. Execute: curl -fsSL https://ollama.ai/install.sh | sh")
    
    return False

def test_system():
    """Testa o sistema"""
    print("\n🧪 Testando sistema...")
    
    try:
        if Path("examples/local_llm_test.py").exists():
            subprocess.run([sys.executable, "examples/local_llm_test.py"], 
                          check=False, timeout=60)
        else:
            print("⚠️  Arquivo de teste não encontrado")
    except subprocess.TimeoutExpired:
        print("⚠️  Teste demorou muito, mas isso é normal")
    except Exception as e:
        print(f"⚠️  Erro no teste: {e}")

def show_next_steps():
    """Mostra próximos passos"""
    print("\n" + "=" * 60)
    print("   🎉 Setup concluído!")
    print("=" * 60)
    print("\n🚀 Próximos passos:")
    print("   1. Configure o arquivo .env se necessário")
    print("   2. Teste: python examples/local_llm_test.py")
    print("   3. Interface web: streamlit run apps/streamlit_app.py")
    print("\n💡 Modelos recomendados para Ollama:")
    print("   - ollama pull llama2:7b      (Modelo geral)")
    print("   - ollama pull mistral:7b     (Rápido e eficiente)")
    print("   - ollama pull codellama:7b   (Para código)")
    print()

def main():
    """Função principal do setup"""
    print_header()
    
    # Verificações iniciais
    if not check_python_version():
        return False
    
    if not check_project_structure():
        return False
    
    # Instalações
    if not install_dependencies():
        print("⚠️  Continuando mesmo com erro nas dependências...")
    
    gpu_info = detect_gpu()
    install_pytorch(gpu_info)
    
    # Configurações
    ollama_ok = setup_ollama()
    
    # Teste
    test_system()
    
    # Finalizar
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            input("Pressione Enter para sair...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Setup cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")
    else:
        input("Pressione Enter para sair...")
