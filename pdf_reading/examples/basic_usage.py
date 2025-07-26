"""
Exemplo de uso básico do sistema LLM PDF Reading
"""
from pathlib import Path
import sys

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent.parent))

from llm_pdf_reading.orchestrator import PDFReadingOrchestrator

def main():
    # Exemplo de uso básico
    print("🤖 LLM PDF Reading - Exemplo de Uso")
    print("=" * 50)
    
    # Inicializar o orquestrador
    orchestrator = PDFReadingOrchestrator()
    
    # Caminho para um PDF de exemplo (você precisa substituir pelo seu arquivo)
    pdf_path = "data/raw/exemplo.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        print("💡 Coloque um arquivo PDF em 'data/raw/exemplo.pdf' para testar")
        return
    
    try:
        print(f"📄 Processando: {pdf_path}")
        
        # Processar o PDF
        result = orchestrator.process_pdf(pdf_path)
        
        if result["success"]:
            print("✅ PDF processado com sucesso!")
            print(f"📊 Estatísticas:")
            print(f"   - Palavras: {result['analysis']['word_count']}")
            print(f"   - Caracteres: {result['analysis']['character_count']}")
            print(f"   - Chunks: {len(result['chunks'])}")
            print(f"   - Tempo estimado de leitura: {result['analysis']['estimated_reading_time']} min")
            
            print(f"\n📝 Primeiros 500 caracteres do conteúdo:")
            print(result["content"][:500] + "...")
            
            # Exemplo de pergunta
            question = "Qual é o tema principal do documento?"
            print(f"\n❓ Pergunta: {question}")
            answer = orchestrator.answer_question(result["content"], question)
            print(f"💡 Resposta: {answer}")
            
        else:
            print(f"❌ Erro: {result['error']}")
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
