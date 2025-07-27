#!/usr/bin/env python3
"""
Script para criar um arquivo Profile.pdf de exemplo para testes
"""

def create_simple_pdf():
    """
    Cria um PDF simples usando apenas bibliotecas padrão
    """
    content = """Profile Document - Exemplo

Nome: João da Silva
Cargo: Desenvolvedor Python Sênior
Empresa: TechCorp Solutions
Email: joao.silva@example.com
Telefone: (11) 99999-9999

RESUMO PROFISSIONAL:
Desenvolvedor Python experiente com 5+ anos de experiência em:
- Desenvolvimento de aplicações web
- Machine Learning e IA
- Processamento de documentos PDF
- Integração de LLMs
- Sistemas de monitoramento e analytics

EXPERIÊNCIA:
2023 - Atual: TechCorp Solutions
- Desenvolvimento de sistema de processamento de PDFs
- Integração de modelos LLM para análise de documentos
- Implementação de monitoramento com MLflow
- Criação de dashboards em Streamlit

2020-2023: DataTech Ltda
- Desenvolvimento de pipelines de ML
- Análise e processamento de dados
- Automação de processos

HABILIDADES TÉCNICAS:
- Python, PyTorch, TensorFlow
- Streamlit, FastAPI, Flask
- MLflow, Weights & Biases
- Docker, Kubernetes
- Git, CI/CD

EDUCAÇÃO:
- Bacharelado em Ciência da Computação - USP (2019)
- Certificação em Machine Learning - Coursera (2020)
- Especialização em LLMs - Stanford Online (2023)

PROJETOS DESTACADOS:
1. LLM PDF Reading System
   - Sistema completo de processamento de PDFs
   - Integração com modelos Ollama e OpenAI
   - Interface Streamlit responsiva

2. Monitoring & Analytics Platform
   - Sistema de monitoramento em tempo real
   - Integração com MLflow para tracking
   - Dashboards interativos

3. AI Document Processing
   - Pipeline automatizado de análise
   - Extração inteligente de informações
   - APIs REST para integração

IDIOMAS:
- Português (nativo)
- Inglês (fluente)
- Espanhol (intermediário)

CONTATO:
LinkedIn: linkedin.com/in/joaosilva
GitHub: github.com/joaosilva
Portfolio: joaosilva.dev
"""
    
    # Criar arquivo texto primeiro (para caso PyMuPDF não esteja disponível)
    text_path = "Profile_text.txt"
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo de texto criado: {text_path}")
    
    # Tentar criar PDF real
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        
        pdf_path = "Profile.pdf"
        
        # Criar PDF com formatação
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Dividir conteúdo em parágrafos
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                if para.strip().isupper() or ':' in para:
                    # Títulos
                    p = Paragraph(para.strip(), styles['Heading2'])
                else:
                    # Texto normal
                    p = Paragraph(para.strip(), styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 12))
        
        doc.build(story)
        print(f"✅ PDF criado com sucesso: {pdf_path}")
        return pdf_path
        
    except ImportError:
        print("⚠️ reportlab não disponível. Tentando método alternativo...")
        
        # Método alternativo usando FPDF se disponível
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Profile Document - Exemplo', ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font('Arial', '', 12)
            
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    if line.strip().isupper() or ':' in line:
                        pdf.set_font('Arial', 'B', 12)
                    else:
                        pdf.set_font('Arial', '', 10)
                    
                    # Quebrar linha se muito longa
                    if len(line) > 80:
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            if len(current_line + word) < 80:
                                current_line += word + " "
                            else:
                                pdf.cell(0, 6, current_line.strip(), ln=True)
                                current_line = word + " "
                        if current_line.strip():
                            pdf.cell(0, 6, current_line.strip(), ln=True)
                    else:
                        pdf.cell(0, 6, line, ln=True)
                else:
                    pdf.ln(3)
            
            pdf_path = "Profile.pdf"
            pdf.output(pdf_path)
            print(f"✅ PDF criado com FPDF: {pdf_path}")
            return pdf_path
            
        except ImportError:
            print("⚠️ FPDF também não disponível. Criando PDF básico...")
            
            # Método básico - criar um "PDF" simples (na verdade texto)
            pdf_path = "Profile.pdf"
            with open(pdf_path, 'w', encoding='utf-8') as f:
                f.write("%PDF-1.4\n")
                f.write("1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
                f.write("2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n")
                f.write("3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\n")
                f.write("xref\n0 4\n0000000000 65535 f \n")
                f.write("0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \n")
                f.write("trailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n181\n%%EOF\n")
                f.write(f"\n\n--- CONTENT FOR TESTING ---\n{content}")
            
            print(f"✅ Arquivo PDF básico criado: {pdf_path}")
            return pdf_path

if __name__ == "__main__":
    pdf_file = create_simple_pdf()
    print(f"\n🎉 Arquivo Profile.pdf está pronto para testes!")
    print(f"📁 Localização: {pdf_file}")
    print(f"🧪 Execute: python test_pdf_monitoring.py")
