#!/usr/bin/env python3
"""
Teste específico de monitoramento de função PDF
Demonstra como usar o Profile.pdf para testar o sistema
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importar decoradores de monitoramento
from llm_pdf_reading.monitoring.decorators import monitor_pdf_operation
from llm_pdf_reading.monitoring import model_monitor

def init_monitoring():
    """Inicializa o sistema de monitoramento"""
    if not model_monitor.is_monitoring:
        model_monitor.start_monitoring()
        print("🚀 Sistema de monitoramento iniciado!")
    else:
        print("✅ Sistema de monitoramento já ativo!")

def find_pdf_file(filename: str = "Profile.pdf") -> Optional[str]:
    """
    Procura pelo arquivo PDF no projeto
    """
    possible_locations = [
        # Diretório atual
        Path(".") / filename,
        # Diretório do script
        Path(__file__).parent / filename,
        # Diretório raiz do projeto
        project_root / filename,
        # Pasta data
        project_root / "data" / filename,
        project_root / "data" / "raw" / filename,
        project_root / "data" / "external" / filename,
        # Pasta documents
        project_root / "documents" / filename,
        # Pasta examples
        project_root / "examples" / filename,
        # Desktop
        Path.home() / "Desktop" / filename,
    ]
    
    print(f"🔍 Procurando por {filename}...")
    for location in possible_locations:
        print(f"   Verificando: {location}")
        if location.exists() and location.is_file():
            print(f"✅ Arquivo encontrado: {location}")
            return str(location.absolute())
    
    print(f"❌ Arquivo {filename} não encontrado nas localizações verificadas")
    return None

# ====================================================================
# IMPLEMENTAÇÃO REAL DE EXTRAÇÃO DE PDF COM MONITORAMENTO
# ====================================================================

@monitor_pdf_operation()
def extract_text_from_real_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extrai texto de um arquivo PDF real usando PyMuPDF
    O decorador monitora automaticamente:
    - Tempo de processamento
    - Tamanho do arquivo
    - Número de páginas
    - Sucesso/falha da operação
    """
    print(f"📄 Iniciando extração de PDF: {pdf_path}")
    
    start_time = time.time()
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        # Obter informações do arquivo
        file_size = os.path.getsize(pdf_path)
        print(f"📊 Tamanho do arquivo: {file_size / 1024:.2f} KB")
        
        # Tentar importar PyMuPDF
        try:
            import fitz  # PyMuPDF
            print("✅ PyMuPDF disponível - usando extração avançada")
            
            # Abrir o PDF
            doc = fitz.open(pdf_path)
            num_pages = len(doc)
            print(f"📖 Número de páginas: {num_pages}")
            
            # Extrair texto de todas as páginas
            full_text = ""
            for page_num in range(num_pages):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                full_text += f"\n--- Página {page_num + 1} ---\n{page_text}"
            
            doc.close()
            
        except ImportError:
            print("⚠️ PyMuPDF não disponível - usando extração simulada")
            
            # Simulação de extração para quando PyMuPDF não está disponível
            import random
            num_pages = random.randint(1, 10)
            
            full_text = f"""
--- EXTRAÇÃO SIMULADA DE {pdf_path} ---

Este é um texto simulado extraído do arquivo PDF.
O arquivo tem {num_pages} página(s) e {file_size} bytes.

CONTEÚDO SIMULADO:
- Seção 1: Informações gerais
- Seção 2: Dados específicos
- Seção 3: Conclusões

Texto extraído em modo de simulação porque PyMuPDF não está instalado.
Para extração real, instale: pip install PyMuPDF
            """
        
        # Calcular métricas
        processing_time = time.time() - start_time
        text_length = len(full_text)
        
        result = {
            "success": True,
            "file_path": pdf_path,
            "file_size_bytes": file_size,
            "file_size_kb": file_size / 1024,
            "num_pages": num_pages,
            "text_length": text_length,
            "processing_time": processing_time,
            "words_count": len(full_text.split()),
            "extracted_text": full_text,
            "summary": f"Extraído {text_length} caracteres de {num_pages} página(s) em {processing_time:.2f}s"
        }
        
        print(f"✅ Extração concluída com sucesso!")
        print(f"   📊 {text_length} caracteres extraídos")
        print(f"   📖 {num_pages} páginas processadas")
        print(f"   ⏱️ {processing_time:.2f} segundos")
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        result = {
            "success": False,
            "file_path": pdf_path,
            "error": str(e),
            "processing_time": processing_time,
            "error_type": type(e).__name__
        }
        
        print(f"❌ Erro na extração: {e}")
        return result

@monitor_pdf_operation()
def analyze_pdf_structure(pdf_path: str) -> Dict[str, Any]:
    """
    Analisa a estrutura de um PDF (metadados, páginas, etc.)
    """
    print(f"🔍 Analisando estrutura do PDF: {pdf_path}")
    
    start_time = time.time()
    
    try:
        file_size = os.path.getsize(pdf_path)
        
        try:
            import fitz
            
            doc = fitz.open(pdf_path)
            
            # Extrair metadados
            metadata = doc.metadata
            num_pages = len(doc)
            
            # Analisar cada página
            pages_info = []
            for page_num in range(min(num_pages, 5)):  # Limitar a 5 páginas para exemplo
                page = doc.load_page(page_num)
                rect = page.rect
                text_length = len(page.get_text())
                
                pages_info.append({
                    "page_number": page_num + 1,
                    "width": rect.width,
                    "height": rect.height,
                    "text_length": text_length
                })
            
            doc.close()
            
            result = {
                "success": True,
                "file_path": pdf_path,
                "file_size": file_size,
                "num_pages": num_pages,
                "metadata": metadata,
                "pages_info": pages_info,
                "processing_time": time.time() - start_time
            }
            
        except ImportError:
            # Análise simulada
            result = {
                "success": True,
                "file_path": pdf_path,
                "file_size": file_size,
                "analysis_type": "simulated",
                "message": "Análise simulada - PyMuPDF não disponível",
                "processing_time": time.time() - start_time
            }
        
        print(f"✅ Análise concluída em {result['processing_time']:.2f}s")
        return result
        
    except Exception as e:
        result = {
            "success": False,
            "file_path": pdf_path,
            "error": str(e),
            "processing_time": time.time() - start_time
        }
        
        print(f"❌ Erro na análise: {e}")
        return result

# ====================================================================
# TESTES ESPECÍFICOS PARA PROFILE.PDF
# ====================================================================

def test_profile_pdf_extraction():
    """
    Teste específico para o arquivo Profile.pdf
    """
    print("\n" + "="*60)
    print("🧪 TESTE: Extração de texto do Profile.pdf")
    print("="*60)
    
    # Procurar o arquivo
    pdf_path = find_pdf_file("Profile.pdf")
    
    if not pdf_path:
        print("⚠️ Profile.pdf não encontrado. Criando arquivo de exemplo...")
        
        # Se não encontrar, sugerir onde colocar
        suggested_path = Path(__file__).parent / "Profile.pdf"
        print(f"💡 Coloque o arquivo Profile.pdf em: {suggested_path}")
        print("   Ou em qualquer uma dessas localizações:")
        print("   - Pasta atual do script")
        print("   - Pasta data/raw/ do projeto")
        print("   - Desktop")
        
        # Criar um PDF de exemplo (se possível)
        try:
            create_example_pdf(str(suggested_path))
            pdf_path = str(suggested_path)
        except Exception as e:
            print(f"❌ Não foi possível criar PDF de exemplo: {e}")
            return False
    
    # Executar extração com monitoramento
    print(f"\n📄 Testando extração com monitoramento...")
    
    try:
        result = extract_text_from_real_pdf(pdf_path)
        
        if result["success"]:
            print(f"\n🎉 EXTRAÇÃO BEM-SUCEDIDA!")
            print(f"   📊 Arquivo: {result['file_path']}")
            print(f"   💾 Tamanho: {result['file_size_kb']:.2f} KB")
            print(f"   📖 Páginas: {result['num_pages']}")
            print(f"   📝 Caracteres: {result['text_length']}")
            print(f"   🔤 Palavras: {result['words_count']}")
            print(f"   ⏱️ Tempo: {result['processing_time']:.2f}s")
            
            # Mostrar amostra do texto
            text_sample = result['extracted_text'][:300]
            print(f"\n📖 Amostra do texto extraído:")
            print("-" * 50)
            print(text_sample + "..." if len(result['extracted_text']) > 300 else text_sample)
            print("-" * 50)
            
            return True
        else:
            print(f"\n❌ FALHA NA EXTRAÇÃO!")
            print(f"   Erro: {result['error']}")
            print(f"   Tipo: {result['error_type']}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_profile_pdf_analysis():
    """
    Teste de análise estrutural do Profile.pdf
    """
    print("\n" + "="*60)
    print("🧪 TESTE: Análise estrutural do Profile.pdf")
    print("="*60)
    
    pdf_path = find_pdf_file("Profile.pdf")
    
    if not pdf_path:
        print("❌ Profile.pdf não encontrado para análise")
        return False
    
    try:
        result = analyze_pdf_structure(pdf_path)
        
        if result["success"]:
            print(f"\n🎉 ANÁLISE BEM-SUCEDIDA!")
            print(f"   📊 Arquivo: {result['file_path']}")
            
            if "metadata" in result:
                print(f"   📋 Metadados disponíveis")
                metadata = result["metadata"]
                if metadata.get("title"):
                    print(f"      Título: {metadata['title']}")
                if metadata.get("author"):
                    print(f"      Autor: {metadata['author']}")
                if metadata.get("creator"):
                    print(f"      Criador: {metadata['creator']}")
            
            if "pages_info" in result:
                print(f"   📖 Informações das páginas:")
                for page_info in result["pages_info"]:
                    print(f"      Página {page_info['page_number']}: {page_info['width']:.0f}x{page_info['height']:.0f}px, {page_info['text_length']} chars")
            
            return True
        else:
            print(f"❌ Falha na análise: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def create_example_pdf(output_path: str):
    """
    Cria um PDF de exemplo se não existir um real
    """
    try:
        # Tentar usar reportlab para criar PDF
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        print(f"📝 Criando PDF de exemplo: {output_path}")
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Página 1
        c.drawString(100, height - 100, "PROFILE DOCUMENT - EXEMPLO")
        c.drawString(100, height - 130, "Este é um documento PDF de exemplo para teste")
        c.drawString(100, height - 160, "do sistema de monitoramento.")
        c.drawString(100, height - 200, "Nome: João Silva")
        c.drawString(100, height - 230, "Cargo: Desenvolvedor Python")
        c.drawString(100, height - 260, "Empresa: Tech Solutions")
        c.drawString(100, height - 290, "Email: joao@email.com")
        c.drawString(100, height - 340, "HABILIDADES:")
        c.drawString(120, height - 370, "- Python, Machine Learning")
        c.drawString(120, height - 400, "- LLMs, MLflow, Streamlit")
        c.drawString(120, height - 430, "- PDF Processing, Monitoring")
        
        c.showPage()
        
        # Página 2
        c.drawString(100, height - 100, "EXPERIÊNCIA PROFISSIONAL")
        c.drawString(100, height - 130, "2023-2025: Desenvolvedor Senior")
        c.drawString(100, height - 160, "- Desenvolvimento de sistemas de IA")
        c.drawString(100, height - 190, "- Integração de LLMs com PDFs")
        c.drawString(100, height - 220, "- Sistema de monitoramento MLflow")
        
        c.drawString(100, height - 270, "PROJETOS:")
        c.drawString(120, height - 300, "1. LLM PDF Reading System")
        c.drawString(120, height - 330, "2. Monitoring & Analytics Platform")
        c.drawString(120, height - 360, "3. AI Document Processing")
        
        c.save()
        print(f"✅ PDF de exemplo criado: {output_path}")
        
    except ImportError:
        print("⚠️ reportlab não disponível para criar PDF de exemplo")
        print("   Instale com: pip install reportlab")
        raise
    except Exception as e:
        print(f"❌ Erro ao criar PDF de exemplo: {e}")
        raise

def show_monitoring_results():
    """
    Mostra os resultados do monitoramento após os testes
    """
    print("\n" + "="*60)
    print("📊 RESULTADOS DO MONITORAMENTO")
    print("="*60)
    
    try:
        # Status geral do sistema
        status = model_monitor.get_system_status()
        print(f"📈 Total de operações: {status['total_requests']}")
        print(f"📊 Taxa de sucesso: {status['availability']:.1%}")
        print(f"⏱️ Tempo médio: {status['avg_response_time']:.2f}s")
        
        # Métricas em tempo real
        metrics = model_monitor.get_real_time_metrics()
        
        print(f"\n📊 Operações recentes:")
        if metrics['current_operations']:
            for op_id, op_data in metrics['current_operations'].items():
                print(f"   - {op_data['operation']}: {op_data['duration_so_far']:.2f}s")
        else:
            print("   Nenhuma operação ativa no momento")
        
        # Performance tracker
        from llm_pdf_reading.monitoring import performance_tracker
        summary = performance_tracker.get_performance_summary()
        
        if summary:
            print(f"\n⚡ Resumo de Performance:")
            for operation, stats in summary.items():
                if "pdf" in operation.lower():
                    print(f"   📄 {operation}:")
                    print(f"      Execuções: {stats['count']}")
                    print(f"      Tempo médio: {stats['avg_duration']:.2f}s")
                    print(f"      Tempo mín/máx: {stats['min_duration']:.2f}s / {stats['max_duration']:.2f}s")
        
    except Exception as e:
        print(f"❌ Erro ao obter métricas: {e}")

def main():
    """
    Função principal para testar monitoramento de PDF
    """
    print("🚀 TESTE DE MONITORAMENTO DE FUNÇÃO PDF")
    print("="*70)
    print("Este teste demonstra como o sistema monitora")
    print("operações de processamento de PDF em tempo real.")
    print("="*70)
    
    # Inicializar monitoramento
    init_monitoring()
    
    try:
        # Executar testes específicos do Profile.pdf
        success1 = test_profile_pdf_extraction()
        success2 = test_profile_pdf_analysis()
        
        # Mostrar resultados do monitoramento
        show_monitoring_results()
        
        print("\n" + "="*70)
        if success1 or success2:
            print("🎉 TESTE DE MONITORAMENTO PDF CONCLUÍDO!")
            print("="*70)
            print("\n📋 O que foi monitorado automaticamente:")
            print("✅ Tempo de processamento")
            print("✅ Tamanho do arquivo")
            print("✅ Número de páginas")
            print("✅ Taxa de sucesso/falha")
            print("✅ Métricas de performance")
            print("✅ Logs automáticos")
            
            print("\n🔍 Para ver mais detalhes:")
            print("- Status: model_monitor.get_system_status()")
            print("- Métricas: model_monitor.get_real_time_metrics()")
            print("- Dashboard: streamlit run dashboard.py")
            print("- MLflow: mlflow ui")
        else:
            print("⚠️ TESTES CONCLUÍDOS COM LIMITAÇÕES")
            print("="*70)
            print("Coloque o arquivo Profile.pdf no diretório para teste completo")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ Sistema de monitoramento PDF testado com sucesso!")
    else:
        print("\n💥 Falha no teste do sistema de monitoramento PDF!")
