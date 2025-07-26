@echo off
echo Iniciando aplicacao Streamlit...
echo.
echo Certifique-se de que o ambiente virtual esta ativo e as dependencias instaladas
echo.
pause

cd /d "%~dp0.."
streamlit run apps/streamlit_app.py
