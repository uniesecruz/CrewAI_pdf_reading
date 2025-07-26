@echo off
title Setup LLM PDF Reading - Modelos Locais Gratuitos
color 0A

echo.
echo ================================================
echo   🤖 LLM PDF Reading - Setup Modelos Locais
echo   🎯 100%% Gratuito usando GPU local!
echo ================================================
echo.

echo 📦 Instalando dependencias Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ✅ Dependencias instaladas com sucesso!
echo.

echo 🔍 Verificando GPU NVIDIA...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ GPU NVIDIA detectada!
    echo 📦 Instalando PyTorch com CUDA...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
) else (
    echo ⚠️  GPU NVIDIA nao detectada, usando CPU
    echo 📦 Instalando PyTorch CPU...
    pip install torch torchvision torchaudio
)

echo.
echo 🦙 Configurando Ollama...
echo.
echo IMPORTANTE: Para usar Ollama (recomendado):
echo 1. Baixe de: https://ollama.ai/download/windows
echo 2. Execute o instalador
echo 3. Reinicie este script
echo.

where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama detectado!
    echo 📥 Baixando modelo llama2:7b...
    ollama pull llama2:7b
    if %errorlevel% equ 0 (
        echo ✅ Modelo llama2:7b baixado!
    ) else (
        echo ⚠️  Erro ao baixar modelo, mas Ollama esta instalado
    )
) else (
    echo ❌ Ollama nao encontrado
    echo 💡 Instale Ollama para usar modelos locais otimizados
)

echo.
echo 🧪 Executando teste do sistema...
python examples/local_llm_test.py

echo.
echo ================================================
echo   🎉 Setup concluido!
echo ================================================
echo.
echo 🚀 Proximos passos:
echo   1. Configure o arquivo .env se necessario
echo   2. Teste: python examples/local_llm_test.py
echo   3. Interface web: streamlit run apps/streamlit_app.py
echo.
echo 💡 Modelos recomendados para Ollama:
echo   - ollama pull llama2:7b      (Modelo geral)
echo   - ollama pull mistral:7b     (Rapido e eficiente)
echo   - ollama pull codellama:7b   (Para codigo)
echo.

pause
