# Setup LLM PDF Reading - Modelos Locais Gratuitos
# PowerShell Script

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "   🤖 LLM PDF Reading - Setup Modelos Locais" -ForegroundColor Green
Write-Host "   🎯 100% Gratuito usando GPU local!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Navegar para o diretório do projeto
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

Write-Host "🔍 Verificando estrutura do projeto..." -ForegroundColor Yellow
Write-Host "📁 Diretório atual: $PWD" -ForegroundColor Cyan

if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Arquivo requirements.txt não encontrado!" -ForegroundColor Red
    Write-Host "💡 Execute este script do diretório scripts/ do projeto" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

if (-not (Test-Path "pyproject.toml")) {
    Write-Host "❌ Arquivo pyproject.toml não encontrado!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "✅ Projeto encontrado: $PWD" -ForegroundColor Green
Write-Host ""

# Verificar Python
Write-Host "🐍 Verificando versão do Python..." -ForegroundColor Yellow
try {
    $PythonVersion = python --version 2>&1
    Write-Host "✅ Python detectado: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado no PATH!" -ForegroundColor Red
    Write-Host "💡 Instale Python ou ative o ambiente virtual" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar ambiente virtual
if (Test-Path ".venv") {
    Write-Host "🔧 Ambiente virtual encontrado" -ForegroundColor Green
    Write-Host "💡 Certifique-se de que está ativado: .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  Ambiente virtual não encontrado" -ForegroundColor Yellow
    Write-Host "💡 Recomendado criar um: python -m venv .venv" -ForegroundColor Yellow
}

Write-Host ""

# Instalar dependências
Write-Host "📦 Instalando dependências Python..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Erro na instalação"
    }
    Write-Host "✅ Dependências instaladas com sucesso!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ Erro ao instalar dependências!" -ForegroundColor Red
    Write-Host "💡 Possíveis soluções:" -ForegroundColor Yellow
    Write-Host "   1. Ative o ambiente virtual: .venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "   2. Atualize pip: python -m pip install --upgrade pip" -ForegroundColor Cyan
    Write-Host "   3. Verifique a versão do Python: python --version" -ForegroundColor Cyan
    Write-Host "   4. Tente instalar manualmente: pip install torch transformers" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Pressione Enter para continuar mesmo assim"
}

Write-Host ""

# Verificar GPU NVIDIA
Write-Host "🔍 Verificando GPU NVIDIA..." -ForegroundColor Yellow
try {
    nvidia-smi | Out-Null
    Write-Host "✅ GPU NVIDIA detectada!" -ForegroundColor Green
    Write-Host "📦 Instalando PyTorch com CUDA..." -ForegroundColor Yellow
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
} catch {
    Write-Host "⚠️  GPU NVIDIA não detectada, usando CPU" -ForegroundColor Yellow
    Write-Host "📦 Instalando PyTorch CPU..." -ForegroundColor Yellow
    pip install torch torchvision torchaudio
}

Write-Host ""

# Configurar Ollama
Write-Host "🦙 Configurando Ollama..." -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANTE: Para usar Ollama (recomendado):" -ForegroundColor Cyan
Write-Host "1. Baixe de: https://ollama.ai/download/windows" -ForegroundColor White
Write-Host "2. Execute o instalador" -ForegroundColor White
Write-Host "3. Reinicie este script" -ForegroundColor White
Write-Host ""

try {
    ollama --version | Out-Null
    Write-Host "✅ Ollama detectado!" -ForegroundColor Green
    Write-Host "📥 Baixando modelo llama2:7b..." -ForegroundColor Yellow
    ollama pull llama2:7b
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Modelo llama2:7b baixado!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Erro ao baixar modelo, mas Ollama está instalado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Ollama não encontrado" -ForegroundColor Red
    Write-Host "💡 Instale Ollama para usar modelos locais otimizados" -ForegroundColor Yellow
}

Write-Host ""

# Testar sistema
Write-Host "🧪 Executando teste do sistema..." -ForegroundColor Yellow
try {
    python examples/local_llm_test.py
} catch {
    Write-Host "⚠️  Erro ao executar teste, mas isso é normal se as dependências ainda não estão completas" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "   🎉 Setup concluído!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Configure o arquivo .env se necessário" -ForegroundColor White
Write-Host "   2. Teste: python examples/local_llm_test.py" -ForegroundColor White
Write-Host "   3. Interface web: streamlit run apps/streamlit_app.py" -ForegroundColor White
Write-Host ""
Write-Host "💡 Modelos recomendados para Ollama:" -ForegroundColor Yellow
Write-Host "   - ollama pull llama2:7b      (Modelo geral)" -ForegroundColor White
Write-Host "   - ollama pull mistral:7b     (Rápido e eficiente)" -ForegroundColor White
Write-Host "   - ollama pull codellama:7b   (Para código)" -ForegroundColor White
Write-Host ""

Read-Host "Pressione Enter para sair"
