"""
Script para configurar o ambiente de desenvolvimento
Inclui suporte para LLMs gratuitas rodando na GPU
"""
import subprocess
import sys
import os
import platform
from pathlib import Path
import json

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

def detect_gpu():
    """Detecta se há GPU disponível para uso"""
    gpu_info = {
        "has_nvidia": False,
        "has_amd": False,
        "cuda_available": False,
        "torch_available": False
    }
    
    try:
        # Verificar NVIDIA GPU
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            gpu_info["has_nvidia"] = True
            print("🎮 GPU NVIDIA detectada!")
    except FileNotFoundError:
        pass
    
    try:
        # Verificar PyTorch e CUDA
        import torch
        gpu_info["torch_available"] = True
        gpu_info["cuda_available"] = torch.cuda.is_available()
        if gpu_info["cuda_available"]:
            print(f"🚀 CUDA disponível! GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("💻 CUDA não disponível, usando CPU")
    except ImportError:
        print("⚠️  PyTorch não instalado")
    
    return gpu_info

def install_gpu_dependencies(gpu_info):
    """Instala dependências específicas para GPU"""
    if not gpu_info["torch_available"]:
        print("📦 Instalando PyTorch...")
        try:
            if gpu_info["has_nvidia"]:
                # PyTorch com CUDA
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu121"
                ])
            else:
                # PyTorch CPU
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio"
                ])
            print("✅ PyTorch instalado!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar PyTorch: {e}")
            return False
    
    # Instalar dependências para modelos locais
    local_deps = [
        "transformers>=4.35.0",
        "accelerate>=0.21.0", 
        "bitsandbytes>=0.41.0",
        "scipy>=1.11.0",
        "safetensors>=0.4.0"
    ]
    
    print("📦 Instalando dependências para modelos locais...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + local_deps)
        print("✅ Dependências para GPU instaladas!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências GPU: {e}")
        return False
    
    return True

def setup_ollama():
    """Configura Ollama para modelos locais"""
    print("🦙 Configurando Ollama...")
    
    system = platform.system().lower()
    
    if system == "windows":
        print("💡 Para instalar Ollama no Windows:")
        print("   1. Baixe de: https://ollama.ai/download/windows")
        print("   2. Execute o instalador")
        print("   3. Reinicie o terminal")
        print("   4. Execute: ollama pull llama2")
    elif system == "linux":
        print("💡 Para instalar Ollama no Linux:")
        print("   Execute: curl -fsSL https://ollama.ai/install.sh | sh")
    elif system == "darwin":
        print("💡 Para instalar Ollama no macOS:")
        print("   1. Baixe de: https://ollama.ai/download/mac")
        print("   2. Ou use Homebrew: brew install ollama")
    
    # Verificar se Ollama está instalado
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama detectado!")
            
            # Sugerir modelos recomendados
            recommended_models = [
                "llama2:7b",
                "mistral:7b", 
                "codellama:7b",
                "neural-chat:7b"
            ]
            
            print("🔧 Modelos recomendados para instalar:")
            for model in recommended_models:
                print(f"   ollama pull {model}")
            
            return True
    except FileNotFoundError:
        pass
    
    return False

def check_env_file():
    """Verifica se o arquivo .env existe e tem as configurações necessárias"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return False
    
    # Ler conteúdo do .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Chaves de API (opcionais se usar modelos locais)
    api_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
    missing_api_keys = []
    
    for key in api_keys:
        if f"{key}=your_" in content:
            missing_api_keys.append(key)
    
    # Verificar configurações de modelos locais
    local_configs = ["USE_LOCAL_MODELS", "OLLAMA_BASE_URL", "HF_MODEL_NAME"]
    has_local_config = any(config in content for config in local_configs)
    
    if missing_api_keys and not has_local_config:
        print("⚠️  Configure pelo menos uma opção:")
        print("   OPÇÃO 1 - APIs comerciais:")
        for key in missing_api_keys:
            print(f"     - {key}")
        print("   OPÇÃO 2 - Modelos locais gratuitos:")
        print("     - USE_LOCAL_MODELS=True")
        print("     - OLLAMA_BASE_URL=http://localhost:11434")
        print("     - HF_MODEL_NAME=microsoft/DialoGPT-medium")
        return False
    
    print("✅ Arquivo .env configurado!")
    return True

def create_local_model_config():
    """Cria configuração para modelos locais"""
    config = {
        "local_models": {
            "ollama": {
                "base_url": "http://localhost:11434",
                "models": [
                    {"name": "llama2:7b", "description": "Llama 2 7B - Modelo geral"},
                    {"name": "mistral:7b", "description": "Mistral 7B - Rápido e eficiente"},
                    {"name": "codellama:7b", "description": "Code Llama 7B - Para código"},
                    {"name": "neural-chat:7b", "description": "Neural Chat 7B - Conversacional"}
                ]
            },
            "huggingface": {
                "models": [
                    {"name": "microsoft/DialoGPT-medium", "type": "conversational"},
                    {"name": "distilbert-base-uncased", "type": "embedding"},
                    {"name": "sentence-transformers/all-MiniLM-L6-v2", "type": "embedding"}
                ]
            },
            "local_inference": {
                "device": "auto",  # auto, cpu, cuda
                "max_length": 2048,
                "temperature": 0.7,
                "do_sample": True
            }
        }
    }
    
    config_path = Path("config/local_models.json")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuração de modelos locais criada em: {config_path}")
    return config_path

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
    print("🎯 Com suporte para LLMs gratuitas na GPU!")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not Path("pyproject.toml").exists():
        print("❌ Execute este script no diretório raiz do projeto!")
        return
    
    # Detectar GPU
    print("🔍 Detectando hardware...")
    gpu_info = detect_gpu()
    
    # Criar diretórios
    create_data_directories()
    
    # Instalar dependências básicas
    if not install_requirements():
        return
    
    # Instalar dependências para GPU se disponível
    if gpu_info["has_nvidia"] or gpu_info["torch_available"]:
        install_gpu_dependencies(gpu_info)
    
    # Configurar Ollama
    ollama_available = setup_ollama()
    
    # Criar configuração de modelos locais
    create_local_model_config()
    
    # Verificar configurações
    env_ok = check_env_file()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA CONFIGURAÇÃO:")
    print(f"   🎮 GPU NVIDIA: {'✅' if gpu_info['has_nvidia'] else '❌'}")
    print(f"   🔥 CUDA: {'✅' if gpu_info['cuda_available'] else '❌'}")
    print(f"   🦙 Ollama: {'✅' if ollama_available else '❌'}")
    print(f"   🔧 Configuração: {'✅' if env_ok else '⚠️'}")
    
    print("\n� OPÇÕES DE USO:")
    print("   1. 🆓 MODELOS LOCAIS (Gratuito):")
    print("      - Ollama: llama2, mistral, codellama")
    print("      - Hugging Face: DialoGPT, DistilBERT")
    print("   2. ☁️  APIS COMERCIAIS:")
    print("      - OpenAI GPT-4, Anthropic Claude, Google Gemini")
    
    print("\n� COMANDOS PARA TESTAR:")
    if ollama_available:
        print("   🦙 Ollama: ollama run llama2")
    print("   🧪 Teste básico: python examples/basic_usage.py")
    print("   🌐 Interface web: streamlit run apps/streamlit_app.py")
    
    if not env_ok:
        print("\n⚠️  Configure o .env para começar a usar!")

if __name__ == "__main__":
    main()
