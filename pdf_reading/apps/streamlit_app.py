"""
Aplicação Streamlit para interface web do sistema de leitura de PDFs
"""
import streamlit as st
import tempfile
import os
from pathlib import Path
import sys

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent.parent))

from llm_pdf_reading.orchestrator import PDFReadingOrchestrator

def main():
    st.title("🤖 LLM PDF Reading - Análise Inteligente de PDFs")
    st.markdown("Faça upload de um PDF e deixe nossa IA analisar o conteúdo para você!")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Seleção do modelo LLM
        llm_provider = st.selectbox(
            "Provedor de LLM",
            ["OpenAI", "Anthropic", "Google"]
        )
        
        # Configurações de chunk
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
                    # Inicializar orquestrador
                    orchestrator = PDFReadingOrchestrator()
                    
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
                            question = st.text_input(
                                "Digite sua pergunta:",
                                placeholder="Ex: Qual é o tema principal do documento?"
                            )
                            
                            if st.button("Responder") and question:
                                with st.spinner("Gerando resposta..."):
                                    answer = orchestrator.answer_question(result["content"], question)
                                    st.write("**Resposta:**")
                                    st.write(answer)
                    
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
        st.markdown("### ℹ️ Sobre")
        st.markdown("""
        Esta aplicação usa CrewAI e LLMs para analisar 
        documentos PDF de forma inteligente.
        """)

if __name__ == "__main__":
    main()
