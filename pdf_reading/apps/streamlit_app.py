"""
Aplicação Streamlit para interface web do sistema de leitura de PDFs
Com suporte para configuração de modelos Ollama e LLMs locais
"""
import streamlit as st
import tempfile
import os
from pathlib import Path
import sys
import requests
import logging

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent.parent))

from llm_pdf_reading.orchestrator import PDFReadingOrchestrator
from llm_pdf_reading.config import OLLAMA_CONFIG, USE_LOCAL_MODELS

def check_ollama_status():
    """Verifica se Ollama está rodando e quais modelos estão disponíveis"""
    try:
        response = requests.get(f"{OLLAMA_CONFIG['base_url']}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            return {
                'available': True,
                'models': available_models
            }
        return {
            'available': False,
            'models': []
        }
    except Exception:
        return {
            'available': False,
            'models': []
        }

def get_model_config_from_ui():
    """Retorna configuração do modelo baseado na seleção da UI"""
    return {
        'use_ollama': st.session_state.get('use_ollama', True),
        'ollama_model': st.session_state.get('selected_ollama_model', 'llama2:7b'),
        'use_huggingface': st.session_state.get('use_huggingface', True),
        'hf_model': st.session_state.get('hf_model', 'microsoft/DialoGPT-medium'),
        'device': st.session_state.get('device', 'auto')
    }

def main():
    st.title("🤖 LLM PDF Reading - Análise Inteligente de PDFs")
    st.markdown("Faça upload de um PDF e deixe nossa IA analisar o conteúdo para você!")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Seleção do tipo de modelo
        st.subheader("🤖 Configuração de LLM")
        
        use_local_models = st.checkbox(
            "Usar Modelos Locais (Gratuito)", 
            value=USE_LOCAL_MODELS,
            help="Use modelos locais (Ollama/Hugging Face) em vez de APIs comerciais"
        )
        
        if use_local_models:
            # Verificar status do Ollama
            ollama_status = check_ollama_status()
            ollama_running = ollama_status['available']
            available_ollama_models = ollama_status['models']
            
            if ollama_running and available_ollama_models:
                st.success(f"✅ Ollama conectado ({len(available_ollama_models)} modelos)")
                
                # Seleção do modelo Ollama
                selected_ollama_model = st.selectbox(
                    "🦙 Modelo Ollama",
                    available_ollama_models,
                    index=0 if available_ollama_models else None,
                    help="Escolha o modelo Ollama para usar"
                )
                st.session_state['selected_ollama_model'] = selected_ollama_model
                st.session_state['use_ollama'] = True
                st.session_state['llm_provider'] = "ollama"
                
                # Mostrar informações do modelo selecionado
                with st.expander("ℹ️ Informações do Modelo"):
                    if 'llama2' in selected_ollama_model:
                        st.write("**Llama 2** - Modelo geral da Meta, bom para conversas e análise de texto")
                    elif 'mistral' in selected_ollama_model:
                        st.write("**Mistral** - Modelo rápido e eficiente para tarefas gerais")
                    elif 'codellama' in selected_ollama_model:
                        st.write("**Code Llama** - Especializado em código e programação")
                    elif 'neural-chat' in selected_ollama_model:
                        st.write("**Neural Chat** - Otimizado para conversas")
                    else:
                        st.write(f"**{selected_ollama_model}** - Modelo personalizado")
                
            else:
                st.warning("⚠️ Ollama não detectado")
                st.markdown("""
                **Para usar Ollama:**
                1. Baixe: [ollama.ai](https://ollama.ai/download)
                2. Instale e execute
                3. Baixe modelos: `ollama pull llama2:7b`
                """)
                
                # Fallback para Hugging Face
                st.session_state['use_ollama'] = False
                st.session_state['use_huggingface'] = True
                st.session_state['llm_provider'] = "huggingface"
            
            # Configuração Hugging Face (sempre disponível como fallback)
            with st.expander("🤗 Configuração Hugging Face"):
                hf_models = [
                    "microsoft/DialoGPT-medium",
                    "microsoft/DialoGPT-large", 
                    "facebook/blenderbot-400M-distill"
                ]
                
                selected_hf_model = st.selectbox(
                    "Modelo Hugging Face",
                    hf_models,
                    index=0,
                    help="Modelo usado se Ollama não estiver disponível"
                )
                st.session_state['hf_model'] = selected_hf_model
                st.session_state['llm_provider'] = "huggingface"
                
                device = st.selectbox(
                    "Device",
                    ["auto", "cpu", "cuda"],
                    index=0,
                    help="auto = detecta automaticamente"
                )
                st.session_state['device'] = device
        
        else:
            # APIs comerciais
            st.subheader("☁️ APIs Comerciais")
            llm_provider = st.selectbox(
                "Provedor de LLM",
                ["OpenAI", "Anthropic", "Google"],
                help="Requer chaves de API configuradas no .env"
            )
            
            if llm_provider == "OpenAI":
                model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            elif llm_provider == "Anthropic":
                model_options = ["claude-3-sonnet", "claude-3-haiku"]
            else:  # Google
                model_options = ["gemini-pro", "gemini-pro-vision"]
            
            selected_commercial_model = st.selectbox(
                "Modelo",
                model_options,
                help=f"Modelos disponíveis do {llm_provider}"
            )
        
        st.markdown("---")
        
        # Configurações de processamento
        st.subheader("📄 Processamento")
        chunk_size = st.slider("Tamanho do Chunk", 500, 2000, 1000)
        chunk_overlap = st.slider("Sobreposição", 100, 500, 200)
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Escolha um arquivo PDF",
        type="pdf",
        help="Faça upload de um arquivo PDF para análise"
    )
    
    if uploaded_file is not None:
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Mostrar informações do arquivo
            st.info(f"📄 Arquivo: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Botão para processar
            if st.button("🚀 Processar PDF", type="primary"):
                with st.spinner("Processando PDF... Isso pode levar alguns momentos."):
                    # Configurar modelo baseado na seleção da UI
                    # Obter configuração do modelo selecionado
                    model_config = get_model_config_from_ui() if use_local_models else None
                    
                    # Inicializar orquestrador com configuração personalizada
                    orchestrator = PDFReadingOrchestrator(
                        use_local_models=use_local_models,
                        custom_config=model_config
                    )
                    
                    # Processar PDF
                    result = orchestrator.process_pdf(tmp_file_path)
                    
                    if result["success"]:
                        # Mostrar resultados
                        st.success("✅ PDF processado com sucesso!")
                        
                        # Tabs para diferentes visualizações
                        tab1, tab2, tab3, tab4 = st.tabs(["📊 Análise", "📝 Conteúdo", "📋 Metadados", "❓ Perguntas"])
                        
                        with tab1:
                            st.subheader("Análise do Documento")
                            analysis = result["analysis"]
                            
                            # Mostrar informações do modelo usado
                            llm_used = result.get("llm_used", "none")
                            if llm_used != "none":
                                st.success(f"🤖 Análise feita com: {llm_used}")
                            else:
                                st.info("📊 Análise básica (sem LLM)")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Palavras", analysis["word_count"])
                            with col2:
                                st.metric("Caracteres", analysis["character_count"])
                            with col3:
                                st.metric("Tempo de Leitura (min)", analysis["estimated_reading_time"])
                            
                            st.write("**Tópicos Principais:**")
                            for topic in analysis["key_topics"]:
                                st.write(f"• {topic}")
                            
                            st.write("**Resumo:**")
                            st.write(analysis["summary"])
                            
                            # Mostrar resumo do LLM se disponível
                            if "llm_summary" in analysis:
                                st.write("**Resumo do LLM:**")
                                st.write(analysis["llm_summary"])
                        
                        with tab2:
                            st.subheader("Conteúdo Extraído")
                            st.text_area(
                                "Texto do PDF",
                                result["content"],
                                height=400,
                                disabled=True
                            )
                            
                            st.write(f"**Total de chunks criados:** {len(result['chunks'])}")
                        
                        with tab3:
                            st.subheader("Metadados do Arquivo")
                            metadata = result["metadata"]
                            if metadata:
                                for key, value in metadata.items():
                                    st.write(f"**{key}:** {value}")
                            else:
                                st.write("Nenhum metadado encontrado.")
                        
                        with tab4:
                            st.subheader("Faça Perguntas sobre o Documento")
                            
                            # Mostrar status do modelo selecionado
                            if st.session_state.get('llm_provider') == "ollama":
                                st.info(f"🤖 Usando modelo Ollama: {st.session_state.get('selected_ollama_model', 'Não selecionado')}")
                            elif st.session_state.get('llm_provider') == "huggingface":
                                st.info(f"🤗 Usando modelo Hugging Face: {st.session_state.get('hf_model', 'DialoGPT-medium')}")
                            else:
                                st.warning("⚠️ Nenhum LLM configurado - usando análise básica")
                            
                            question = st.text_input(
                                "Digite sua pergunta:",
                                placeholder="Ex: Qual é o tema principal do documento?"
                            )
                            
                            if st.button("Responder") and question:
                                with st.spinner("Gerando resposta..."):
                                    try:
                                        # Usar a configuração do modelo selecionado
                                        model_config = get_model_config_from_ui()
                                        orchestrator_qa = PDFReadingOrchestrator(custom_config=model_config)
                                        
                                        answer = orchestrator_qa.answer_question(result["content"], question)
                                        
                                        # Salvar no histórico
                                        if 'questions_history' not in st.session_state:
                                            st.session_state.questions_history = []
                                        
                                        st.session_state.questions_history.append({
                                            'question': question,
                                            'answer': answer,
                                            'model': st.session_state.get('llm_provider', 'basic')
                                        })
                                        
                                        st.write("**Pergunta:**", question)
                                        st.write("**Resposta:**", answer)
                                        
                                    except Exception as e:
                                        st.error(f"Erro ao processar pergunta: {str(e)}")
                                        st.info("Tentando com análise básica...")
                                        answer = f"Desculpe, não foi possível processar sua pergunta com o LLM. Conteúdo relacionado encontrado: {result['content'][:500]}..."
                                        st.write("**Resposta (básica):**", answer)
                            
                            # Histórico de perguntas
                            if st.session_state.get('questions_history'):
                                st.markdown("---")
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.subheader("📜 Histórico de Perguntas")
                                with col2:
                                    if st.button("🗑️ Limpar", help="Limpar histórico de perguntas"):
                                        st.session_state.questions_history = []
                                        st.rerun()
                                
                                for i, qa in enumerate(reversed(st.session_state.questions_history[-5:])):  # Mostrar últimas 5
                                    with st.expander(f"❓ {qa['question'][:60]}..." if len(qa['question']) > 60 else qa['question']):
                                        st.write("**Pergunta:**", qa['question'])
                                        st.write("**Resposta:**", qa['answer'])
                                        st.caption(f"Modelo usado: {qa.get('model', 'desconhecido')}")
                    
                    else:
                        st.error(f"❌ Erro ao processar PDF: {result['error']}")
        
        finally:
            # Limpar arquivo temporário
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    # Informações na sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📚 Como usar")
        st.markdown("""
        1. Faça upload de um PDF
        2. Ajuste as configurações se necessário
        3. Clique em 'Processar PDF'
        4. Explore os resultados nas diferentes abas
        5. Faça perguntas sobre o conteúdo
        """)
        
        st.markdown("---")
        st.markdown("### 🤖 Status dos Modelos")
        
        if st.session_state.get('llm_provider') == "ollama":
            # Verificar status do Ollama
            ollama_status = check_ollama_status()
            if ollama_status['available']:
                st.success("✅ Ollama disponível")
                if ollama_status['models']:
                    st.write("**Modelos instalados:**")
                    for model in ollama_status['models'][:3]:  # Mostrar primeiros 3
                        st.write(f"• {model}")
                else:
                    st.warning("⚠️ Nenhum modelo instalado")
                    st.info("Execute: `ollama pull llama2:7b`")
            else:
                st.error("❌ Ollama não disponível")
                st.info("Inicie o Ollama primeiro")
        
        elif st.session_state.get('llm_provider') == "huggingface":
            st.success("✅ Hugging Face disponível")
            st.write(f"**Modelo:** {st.session_state.get('hf_model', 'DialoGPT-medium')}")
        
        else:
            st.info("ℹ️ Usando análise básica")
        
        st.markdown("---")
        st.markdown("### ℹ️ Sobre")
        st.markdown("""
        Esta aplicação usa CrewAI e LLMs para analisar 
        documentos PDF de forma inteligente.
        """)

if __name__ == "__main__":
    main()
