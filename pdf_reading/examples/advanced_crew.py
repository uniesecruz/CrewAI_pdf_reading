"""
Exemplo avançado com CrewAI completo
"""
from pathlib import Path
import sys

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent.parent))

def advanced_crew_example():
    """
    Exemplo mostrando como usar CrewAI de forma mais avançada
    Este exemplo requer que as dependências estejam instaladas
    """
    try:
        from crewai import Crew
        from llm_pdf_reading.crew_agents import PDFAnalysisAgents, PDFAnalysisTasks
        from llm_pdf_reading.pdf_utils import PDFProcessor
        
        print("🚀 Exemplo Avançado com CrewAI")
        print("=" * 50)
        
        # Inicializar componentes
        pdf_processor = PDFProcessor()
        agents = PDFAnalysisAgents()
        
        # Criar agentes
        pdf_reader = agents.create_pdf_reader_agent()
        content_analyzer = agents.create_content_analyzer_agent()
        qa_agent = agents.create_qa_agent()
        
        # Exemplo de PDF (substitua pelo seu arquivo)
        pdf_path = Path("data/raw/exemplo.pdf")
        
        if not pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {pdf_path}")
            return
        
        # Extrair conteúdo
        content = pdf_processor.extract_text_pymupdf(pdf_path)
        
        # Criar tarefas
        extraction_task = PDFAnalysisTasks.create_extraction_task(content, pdf_reader)
        analysis_task = PDFAnalysisTasks.create_analysis_task(content, content_analyzer)
        
        # Criar crew
        crew = Crew(
            agents=[pdf_reader, content_analyzer],
            tasks=[extraction_task, analysis_task],
            verbose=True
        )
        
        # Executar
        print("🔄 Executando análise com CrewAI...")
        result = crew.kickoff()
        
        print("✅ Análise concluída!")
        print(f"📋 Resultado: {result}")
        
    except ImportError as e:
        print(f"❌ Dependências não instaladas: {e}")
        print("💡 Execute: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    advanced_crew_example()
