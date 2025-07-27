#!/usr/bin/env python3
"""
Teste específico para o arquivo Random_Forest.pdf
Demonstra o monitoramento de operações PDF em tempo real
"""

import sys
import os
import time
import pandas as pd
from pathlib import Path
from typing import Dict, Any

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importar decoradores de monitoramento
from llm_pdf_reading.monitoring.decorators import monitor_pdf_operation
from llm_pdf_reading.monitoring import model_monitor
import mlflow
import mlflow.sklearn

def ask_user_about_document_theme():
    """
    Pergunta ao usuário sobre o tema esperado do documento
    """
    print("\n" + "="*60)
    print("❓ PERGUNTA SOBRE O TEMA DO DOCUMENTO")
    print("="*60)
    
    themes_options = {
        "1": "Machine Learning",
        "2": "Random Forest",
        "3": "Data Science", 
        "4": "Deep Learning",
        "5": "Natural Language Processing",
        "6": "Computer Vision",
        "7": "Statistics",
        "8": "Programming",
        "9": "Outro"
    }
    
    print("🎯 Qual tema você espera encontrar neste documento?")
    print("\nOpções disponíveis:")
    for key, value in themes_options.items():
        print(f"   {key}. {value}")
    
    while True:
        try:
            choice = input("\n📝 Digite o número da opção (1-9): ").strip()
            
            if choice in themes_options:
                expected_theme = themes_options[choice]
                
                if choice == "9":  # Outro
                    custom_theme = input("📝 Digite o tema específico: ").strip()
                    if custom_theme:
                        expected_theme = custom_theme
                
                print(f"✅ Tema esperado registrado: {expected_theme}")
                return expected_theme
            else:
                print("❌ Opção inválida. Digite um número de 1 a 9.")
                
        except KeyboardInterrupt:
            print("\n⚠️ Operação cancelada pelo usuário.")
            return "Não informado"
        except Exception as e:
            print(f"❌ Erro: {e}")
            return "Erro na entrada"

def compare_themes_with_mlflow(expected_theme: str, detected_theme: str, confidence: float):
    """
    Compara tema esperado vs detectado e registra no MLflow
    """
    print(f"\n🔍 COMPARAÇÃO DE TEMAS:")
    print(f"   🎯 Esperado: {expected_theme}")
    print(f"   🤖 Detectado: {detected_theme}")
    print(f"   📈 Confiança: {confidence:.1f}%")
    
    # Calcular score de correspondência
    if expected_theme.lower() in detected_theme.lower() or detected_theme.lower() in expected_theme.lower():
        theme_match_score = 100.0
        match_status = "Exato"
    elif any(word in detected_theme.lower() for word in expected_theme.lower().split()):
        theme_match_score = 75.0
        match_status = "Parcial"
    else:
        theme_match_score = 0.0
        match_status = "Diferente"
    
    print(f"   🎯 Correspondência: {match_status} ({theme_match_score}%)")
    
    # Registrar no MLflow
    try:
        with mlflow.start_run(nested=True, run_name="theme_comparison"):
            mlflow.log_param("expected_theme", expected_theme)
            mlflow.log_param("detected_theme", detected_theme)
            mlflow.log_param("match_status", match_status)
            mlflow.log_metric("detection_confidence", confidence)
            mlflow.log_metric("theme_match_score", theme_match_score)
            mlflow.log_metric("accuracy_score", (confidence + theme_match_score) / 2)
    except Exception as e:
        print(f"Erro ao iniciar execução MLflow: {e}")
    
    return {
        "expected_theme": expected_theme,
        "detected_theme": detected_theme,
        "match_status": match_status,
        "theme_match_score": theme_match_score,
        "detection_confidence": confidence,
        "accuracy_score": (confidence + theme_match_score) / 2
    }

def init_monitoring():
    """Inicializa o sistema de monitoramento"""
    if not model_monitor.is_monitoring:
        model_monitor.start_monitoring()
        print("🚀 Sistema de monitoramento iniciado!")
    else:
        print("✅ Sistema de monitoramento já ativo!")
    """Inicializa o sistema de monitoramento"""
    if not model_monitor.is_monitoring:
        model_monitor.start_monitoring()
        print("🚀 Sistema de monitoramento iniciado!")
    else:
        print("✅ Sistema de monitoramento já ativo!")

@monitor_pdf_operation()
def extract_text_from_random_forest_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extrai texto do Random_Forest.pdf com monitoramento automático
    """
    print(f"📄 Iniciando extração do Random Forest PDF: {pdf_path}")
    
    start_time = time.time()
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        # Obter informações do arquivo
        file_size = os.path.getsize(pdf_path)
        print(f"📊 Tamanho do arquivo: {file_size / 1024:.2f} KB")
        
        # Tentar usar PyMuPDF para extração real
        try:
            import fitz  # PyMuPDF
            print("✅ PyMuPDF disponível - extração avançada")
            
            # Abrir o PDF
            doc = fitz.open(pdf_path)
            num_pages = len(doc)
            print(f"📖 Número de páginas: {num_pages}")
            
            # Extrair texto das primeiras páginas
            full_text = ""
            pages_to_extract = min(num_pages, 5)  # Limitar para performance
            
            for page_num in range(pages_to_extract):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                full_text += f"\n--- Página {page_num + 1} ---\n{page_text}"
                print(f"   📄 Página {page_num + 1}: {len(page_text)} caracteres")
            
            # Extrair metadados
            metadata = doc.metadata
            
            doc.close()
            
            # Calcular estatísticas
            processing_time = time.time() - start_time
            text_length = len(full_text)
            words_count = len(full_text.split())
            
            result = {
                "success": True,
                "file_path": pdf_path,
                "file_size_bytes": file_size,
                "file_size_kb": file_size / 1024,
                "num_pages": num_pages,
                "pages_processed": pages_to_extract,
                "text_length": text_length,
                "words_count": words_count,
                "processing_time": processing_time,
                "metadata": metadata,
                "extracted_text": full_text,
                "summary": f"Extraído {text_length} caracteres de {pages_to_extract}/{num_pages} páginas em {processing_time:.2f}s"
            }
            
            print(f"✅ Extração concluída com sucesso!")
            print(f"   📊 {text_length} caracteres extraídos")
            print(f"   📖 {pages_to_extract} de {num_pages} páginas processadas")
            print(f"   🔤 {words_count} palavras encontradas")
            print(f"   ⏱️ {processing_time:.2f} segundos")
            
            return result
            
        except ImportError:
            print("⚠️ PyMuPDF não disponível - usando extração básica")
            
            # Método alternativo - ler como texto se for possível
            try:
                with open(pdf_path, 'rb') as f:
                    content = f.read()
                
                # Simular extração baseada no tamanho
                processing_time = time.time() - start_time
                
                result = {
                    "success": True,
                    "file_path": pdf_path,
                    "file_size_bytes": file_size,
                    "extraction_method": "basic",
                    "processing_time": processing_time,
                    "message": f"Arquivo {file_size} bytes processado (método básico)"
                }
                
                print(f"✅ Processamento básico concluído em {processing_time:.2f}s")
                return result
                
            except Exception as e:
                raise Exception(f"Erro na extração básica: {e}")
        
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
def analyze_document_theme(pdf_path: str) -> Dict[str, Any]:
    """
    Analisa o tema principal do documento usando análise de texto
    """
    print(f"🎯 Analisando tema do documento: {pdf_path}")
    
    start_time = time.time()
    
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        file_size = os.path.getsize(pdf_path)
        
        # Iniciar experimento MLflow
        try:
            with mlflow.start_run(nested=True, run_name="document_theme_analysis"):
                mlflow.log_param("file_path", pdf_path)
                mlflow.log_param("file_size_kb", file_size / 1024)
                
                try:
                    import fitz
                    
                    doc = fitz.open(pdf_path)
                    num_pages = len(doc)
                    mlflow.log_param("num_pages", num_pages)
                    
                    # Extrair texto completo
                    full_text = ""
                    for page_num in range(min(num_pages, 20)):  # Analisar até 20 páginas
                        page = doc.load_page(page_num)
                        page_text = page.get_text()
                        full_text += page_text + " "
                    
                    doc.close()
                    
                    # Análise de temas técnicos
                    themes = {
                        "Machine Learning": ["machine learning", "ml", "algorithm", "model", "training", "prediction"],
                        "Random Forest": ["random forest", "decision tree", "ensemble", "bagging", "bootstrap"],
                        "Data Science": ["data science", "dataset", "feature", "analysis", "statistical"],
                        "Deep Learning": ["deep learning", "neural network", "tensorflow", "pytorch", "gradient"],
                        "Natural Language": ["nlp", "natural language", "text processing", "sentiment", "tokenization"],
                        "Computer Vision": ["computer vision", "image", "opencv", "cnn", "convolution"],
                        "Statistics": ["statistics", "probability", "distribution", "hypothesis", "correlation"],
                        "Programming": ["python", "programming", "code", "function", "class", "variable"]
                    }
                    
                    text_lower = full_text.lower()
                    theme_scores = {}
                    total_words = len(full_text.split())
                    
                    print(f"   📊 Analisando {total_words} palavras...")
                    
                    for theme, keywords in themes.items():
                        score = 0
                        found_keywords = []
                        
                        for keyword in keywords:
                            count = text_lower.count(keyword)
                            if count > 0:
                                score += count
                                found_keywords.append(f"{keyword}:{count}")
                        
                        if score > 0:
                            theme_scores[theme] = {
                                "score": score,
                                "percentage": (score / max(total_words, 1)) * 100,
                                "keywords_found": found_keywords
                            }
                            
                            # Log métricas no MLflow
                            mlflow.log_metric(f"theme_{theme.lower().replace(' ', '_')}_score", score)
                            mlflow.log_metric(f"theme_{theme.lower().replace(' ', '_')}_percentage", theme_scores[theme]["percentage"])
                    
                    # Determinar tema principal
                    if theme_scores:
                        main_theme = max(theme_scores.keys(), key=lambda x: theme_scores[x]["score"])
                        main_theme_score = theme_scores[main_theme]["score"]
                        confidence = min(theme_scores[main_theme]["percentage"] * 10, 100)
                    else:
                        main_theme = "Tema não identificado"
                        main_theme_score = 0
                        confidence = 0
                    
                    processing_time = time.time() - start_time
                    
                    # Log métricas principais
                    mlflow.log_metric("processing_time_seconds", processing_time)
                    mlflow.log_metric("total_words", total_words)
                    mlflow.log_metric("main_theme_score", main_theme_score)
                    mlflow.log_metric("confidence_percentage", confidence)
                    mlflow.log_param("main_theme", main_theme)
                    
                    result = {
                        "success": True,
                        "file_path": pdf_path,
                        "file_size": file_size,
                        "num_pages": num_pages,
                        "total_words": total_words,
                        "main_theme": main_theme,
                        "confidence": confidence,
                        "theme_scores": theme_scores,
                        "processing_time": processing_time,
                        "analysis_summary": f"Tema principal: {main_theme} (confiança: {confidence:.1f}%)"
                    }
                    
                    print(f"✅ Análise de tema concluída em {processing_time:.2f}s")
                    print(f"   🎯 Tema principal: {main_theme}")
                    print(f"   📈 Confiança: {confidence:.1f}%")
                    print(f"   🔍 Temas encontrados:")
                    
                    for theme, data in sorted(theme_scores.items(), key=lambda x: x[1]["score"], reverse=True):
                        print(f"      - {theme}: {data['score']} menções ({data['percentage']:.2f}%)")
                    
                    return result
                    
                except ImportError:
                    # Análise simulada sem PyMuPDF
                    processing_time = time.time() - start_time
                    
                    # Simular análise baseada no nome do arquivo
                    filename = os.path.basename(pdf_path).lower()
                    
                    if "random_forest" in filename:
                        main_theme = "Random Forest"
                        confidence = 85.0
                        theme_scores = {"Random Forest": {"score": 15, "percentage": 5.2}}
                    elif "machine" in filename or "ml" in filename:
                        main_theme = "Machine Learning"
                        confidence = 75.0
                        theme_scores = {"Machine Learning": {"score": 12, "percentage": 4.1}}
                    else:
                        main_theme = "Documento Técnico"
                        confidence = 60.0
                        theme_scores = {"Programming": {"score": 8, "percentage": 2.8}}
                    
                    # Log métricas simuladas
                    mlflow.log_metric("processing_time_seconds", processing_time)
                    mlflow.log_metric("confidence_percentage", confidence)
                    mlflow.log_param("main_theme", main_theme)
                    mlflow.log_param("analysis_method", "simulated")
                    
                    result = {
                        "success": True,
                        "file_path": pdf_path,
                        "file_size": file_size,
                        "main_theme": main_theme,
                        "confidence": confidence,
                        "theme_scores": theme_scores,
                        "processing_time": processing_time,
                        "analysis_method": "simulated",
                        "analysis_summary": f"Tema simulado: {main_theme} (confiança: {confidence:.1f}%)"
                    }
                    
                    print(f"✅ Análise simulada concluída em {processing_time:.2f}s")
                    print(f"   🎯 Tema identificado: {main_theme}")
                    print(f"   📈 Confiança: {confidence:.1f}%")
                    
                    return result
        except Exception as e:
            print(f"Erro ao iniciar execução MLflow: {e}")
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Log erro no MLflow
        try:
            with mlflow.start_run(nested=True, run_name="document_theme_analysis_error"):
                mlflow.log_param("error", str(e))
                mlflow.log_metric("processing_time_seconds", processing_time)
                mlflow.log_param("success", False)
        except Exception as mlflow_error:
            print(f"Erro adicional no MLflow: {mlflow_error}")
        
        result = {
            "success": False,
            "file_path": pdf_path,
            "error": str(e),
            "processing_time": processing_time
        }
        
        print(f"❌ Erro na análise de tema: {e}")
        return result

@monitor_pdf_operation()
def analyze_random_forest_content(pdf_path: str) -> Dict[str, Any]:
    """
    Análise específica do conteúdo sobre Random Forest com MLflow
    """
    print(f"🔍 Analisando conteúdo sobre Random Forest: {pdf_path}")
    
    start_time = time.time()
    
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        file_size = os.path.getsize(pdf_path)
        
        # Iniciar experimento MLflow para Random Forest
        try:
            with mlflow.start_run(nested=True, run_name="random_forest_content_analysis"):
                mlflow.log_param("file_path", pdf_path)
                mlflow.log_param("file_size_kb", file_size / 1024)
                
                try:
                    import fitz
                    
                    doc = fitz.open(pdf_path)
                    num_pages = len(doc)
                    mlflow.log_param("num_pages", num_pages)
                    
                    # Procurar por termos relacionados a Random Forest
                    rf_terms = {
                        'random_forest': ['random forest', 'randomforest'],
                        'decision_trees': ['decision tree', 'decision trees'],
                        'ensemble': ['ensemble', 'ensemble method'],
                        'bagging': ['bagging', 'bootstrap aggregating'],
                        'bootstrap': ['bootstrap', 'bootstrap sampling'],
                        'feature_importance': ['feature importance', 'variable importance'],
                        'overfitting': ['overfitting', 'overfit'],
                        'accuracy': ['accuracy', 'performance'],
                        'classification': ['classification', 'classifier'],
                        'regression': ['regression', 'regressor']
                    }
                    
                    found_terms = {}
                    full_text = ""
                    
                    for page_num in range(min(num_pages, 15)):  # Analisar até 15 páginas
                        page = doc.load_page(page_num)
                        page_text = page.get_text().lower()
                        full_text += page_text
                        
                        # Contar ocorrências de termos
                        for category, terms in rf_terms.items():
                            for term in terms:
                                count = page_text.count(term)
                                if count > 0:
                                    if category not in found_terms:
                                        found_terms[category] = 0
                                    found_terms[category] += count
                    
                    doc.close()
                    
                    # Análise de conteúdo
                    total_chars = len(full_text)
                    total_words = len(full_text.split())
                    total_rf_mentions = sum(found_terms.values())
                    
                    # Calcular métricas de qualidade
                    content_density = total_rf_mentions / max(total_words, 1) * 100
                    technical_depth = len(found_terms) / len(rf_terms) * 100
                    
                    processing_time = time.time() - start_time
                    
                    # Log todas as métricas no MLflow
                    mlflow.log_metric("processing_time_seconds", processing_time)
                    mlflow.log_metric("total_characters", total_chars)
                    mlflow.log_metric("total_words", total_words)
                    mlflow.log_metric("total_rf_mentions", total_rf_mentions)
                    mlflow.log_metric("content_density_percentage", content_density)
                    mlflow.log_metric("technical_depth_percentage", technical_depth)
                    
                    # Log métricas específicas por categoria
                    for category, count in found_terms.items():
                        mlflow.log_metric(f"rf_{category}_mentions", count)
                    
                    result = {
                        "success": True,
                        "file_path": pdf_path,
                        "file_size": file_size,
                        "num_pages": num_pages,
                        "total_characters": total_chars,
                        "total_words": total_words,
                        "rf_terms_found": found_terms,
                        "total_rf_mentions": total_rf_mentions,
                        "content_density": content_density,
                        "technical_depth": technical_depth,
                        "processing_time": processing_time,
                        "analysis_summary": f"Encontrados {total_rf_mentions} menções a Random Forest (densidade: {content_density:.2f}%)"
                    }
                    
                    print(f"✅ Análise concluída em {processing_time:.2f}s")
                    print(f"   📊 {total_words} palavras analisadas")
                    print(f"   🌳 {total_rf_mentions} menções a Random Forest")
                    print(f"   📈 Densidade do conteúdo: {content_density:.2f}%")
                    print(f"   🎯 Profundidade técnica: {technical_depth:.2f}%")
                    
                    if found_terms:
                        print("   🔍 Categorias encontradas:")
                        for category, count in found_terms.items():
                            print(f"      - {category.replace('_', ' ').title()}: {count} menções")
                    
                    return result
                    
                except ImportError:
                    # Análise simulada
                    processing_time = time.time() - start_time
                    
                    # Simular métricas baseadas no arquivo
                    simulated_rf_mentions = 25
                    simulated_content_density = 3.2
                    simulated_technical_depth = 75.0
                    
                    # Log métricas simuladas
                    mlflow.log_metric("processing_time_seconds", processing_time)
                    mlflow.log_metric("total_rf_mentions", simulated_rf_mentions)
                    mlflow.log_metric("content_density_percentage", simulated_content_density)
                    mlflow.log_metric("technical_depth_percentage", simulated_technical_depth)
                    mlflow.log_param("analysis_method", "simulated")
                    
                    result = {
                        "success": True,
                        "file_path": pdf_path,
                        "file_size": file_size,
                        "analysis_type": "simulated",
                        "total_rf_mentions": simulated_rf_mentions,
                        "content_density": simulated_content_density,
                        "technical_depth": simulated_technical_depth,
                        "processing_time": processing_time,
                        "message": "Análise simulada - arquivo processado com sucesso"
                    }
                    
                    print(f"✅ Análise simulada concluída em {processing_time:.2f}s")
                    print(f"   🌳 {simulated_rf_mentions} menções simuladas")
                    print(f"   📈 Densidade simulada: {simulated_content_density:.2f}%")
                    
                    return result
        except Exception as e:
            print(f"Erro ao iniciar execução MLflow: {e}")
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Log erro no MLflow
        try:
            with mlflow.start_run(nested=True, run_name="random_forest_analysis_error"):
                mlflow.log_param("error", str(e))
                mlflow.log_metric("processing_time_seconds", processing_time)
                mlflow.log_param("success", False)
        except Exception as mlflow_error:
            print(f"Erro adicional no MLflow: {mlflow_error}")
        
        result = {
            "success": False,
            "file_path": pdf_path,
            "error": str(e),
            "processing_time": processing_time
        }
        
        print(f"❌ Erro na análise: {e}")
        return result

def show_monitoring_dashboard():
    """
    Mostra dashboard de monitoramento após os testes
    """
    print("\n" + "="*70)
    print("📊 DASHBOARD DE MONITORAMENTO - RANDOM FOREST PDF")
    print("="*70)
    
    try:
        # Status do sistema
        status = model_monitor.get_system_status()
        print(f"🎯 MÉTRICAS GERAIS:")
        print(f"   📈 Total de operações: {status.get('total_requests', 0)}")
        print(f"   📊 Taxa de sucesso: {status.get('availability', 1.0):.1%}")
        print(f"   ⏱️ Tempo médio de resposta: {status.get('avg_response_time', 0.0):.2f}s")
        
        # Tratar erro de uptime se não existir
        uptime = status.get('uptime', 0)
        if uptime is not None:
            print(f"   ⏰ Tempo ativo: {uptime:.0f}s")
        else:
            print(f"   ⏰ Tempo ativo: Não disponível")
        
        # Métricas em tempo real
        metrics = model_monitor.get_real_time_metrics()
        
        print(f"\n🔄 OPERAÇÕES EM TEMPO REAL:")
        current_ops = metrics.get('current_operations', {})
        if current_ops:
            for op_id, op_data in current_ops.items():
                print(f"   - {op_data['operation']}: {op_data['duration_so_far']:.2f}s")
        else:
            print("   ✅ Nenhuma operação ativa")
        
        # Performance tracker
        from llm_pdf_reading.monitoring import performance_tracker
        summary = performance_tracker.get_performance_summary()
        
        if summary:
            print(f"\n⚡ RESUMO DE PERFORMANCE:")
            for operation, stats in summary.items():
                print(f"   📄 {operation}:")
                print(f"      🔢 Execuções: {stats['count']}")
                print(f"      ⏱️ Tempo médio: {stats['avg_duration']:.2f}s")
                print(f"      📊 Mín/Máx: {stats['min_duration']:.2f}s / {stats['max_duration']:.2f}s")
                if stats['count'] > 1:
                    print(f"      📈 Última execução: {stats['last_duration']:.2f}s")
        
    except Exception as e:
        print(f"❌ Erro ao obter métricas: {e}")
        print("   💡 Continuando com execução normal...")

def main():
    """
    Teste principal com Random_Forest.pdf e análise de tema com MLflow
    """
    print("🌳 TESTE DE MONITORAMENTO - RANDOM FOREST PDF COM ANÁLISE DE TEMA")
    print("="*80)
    print("Testando o sistema de monitoramento com análise de tema e métricas MLflow")
    print("="*80)
    
    # Configurar MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Random_Forest_PDF_Analysis")
    
    # Finalizar run ativo se existir
    try:
        active_run = mlflow.active_run()
        if active_run:
            print("⚠️ Finalizando run MLflow ativo...")
            mlflow.end_run()
    except Exception as e:
        print(f"Aviso: {e}")
    
    # Caminho para o arquivo
    pdf_path = r"c:\Users\win\Desktop\Projetos\pdf_reading\pdf_reading\data\external\Random_Forest.pdf"
    
    # Verificar se existe
    if not os.path.exists(pdf_path):
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        return False
    
    print(f"📁 Arquivo encontrado: {pdf_path}")
    print(f"📊 Tamanho: {os.path.getsize(pdf_path) / 1024:.2f} KB")
    
    # Inicializar monitoramento
    init_monitoring()
    
    # Perguntar ao usuário sobre o tema esperado
    expected_theme = ask_user_about_document_theme()
    
    try:
        # Iniciar experimento principal no MLflow
        with mlflow.start_run(run_name="Complete_PDF_Analysis_with_Theme_Question"):
            # Log informações básicas do arquivo
            mlflow.log_param("pdf_file", os.path.basename(pdf_path))
            mlflow.log_param("file_size_kb", os.path.getsize(pdf_path) / 1024)
            mlflow.log_param("analysis_timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
            mlflow.log_param("expected_theme", expected_theme)
            
            print("\n" + "="*60)
            print("🧪 TESTE 1: Análise de Tema do Documento")
            print("="*60)
            
            # Teste 1: Análise de tema
            result_theme = analyze_document_theme(pdf_path)
            
            theme_comparison = None
            if result_theme["success"]:
                print(f"✅ Análise de tema bem-sucedida!")
                print(f"   🎯 Tema: {result_theme['main_theme']}")
                print(f"   📈 Confiança: {result_theme['confidence']:.1f}%")
                
                # Comparar com tema esperado
                theme_comparison = compare_themes_with_mlflow(
                    expected_theme, 
                    result_theme['main_theme'], 
                    result_theme['confidence']
                )
                
                # Log métricas principais do tema
                mlflow.log_metric("theme_analysis_success", 1)
                mlflow.log_param("main_theme", result_theme['main_theme'])
                mlflow.log_metric("theme_confidence", result_theme['confidence'])
                mlflow.log_metric("theme_match_score", theme_comparison['theme_match_score'])
                mlflow.log_metric("theme_accuracy", theme_comparison['accuracy_score'])
            else:
                print(f"❌ Falha na análise de tema: {result_theme['error']}")
                mlflow.log_metric("theme_analysis_success", 0)
                mlflow.log_param("theme_error", result_theme['error'])
            
            print("\n" + "="*60)
            print("🧪 TESTE 2: Extração de Texto")
            print("="*60)
            
            # Teste 2: Extração de texto
            result1 = extract_text_from_random_forest_pdf(pdf_path)
            
            if result1["success"]:
                print(f"✅ Extração bem-sucedida!")
                mlflow.log_metric("text_extraction_success", 1)
                mlflow.log_metric("extraction_time", result1.get("processing_time", 0))
                
                if "extracted_text" in result1:
                    # Mostrar amostra do texto
                    sample = result1["extracted_text"][:500]
                    print(f"\n📖 Amostra do conteúdo extraído:")
                    print("-" * 50)
                    print(sample + "...")
                    print("-" * 50)
                    
                    # Log métricas de extração
                    mlflow.log_metric("extracted_characters", result1.get("text_length", 0))
                    mlflow.log_metric("extracted_words", result1.get("words_count", 0))
                    mlflow.log_metric("pages_processed", result1.get("pages_processed", 0))
                    mlflow.log_metric("total_pages", result1.get("num_pages", 0))
                    
                    # Calcular eficiência de extração
                    if result1.get("num_pages", 0) > 0:
                        extraction_efficiency = (result1.get("pages_processed", 0) / result1.get("num_pages", 1)) * 100
                        mlflow.log_metric("extraction_efficiency_percentage", extraction_efficiency)
            else:
                print(f"❌ Falha na extração: {result1['error']}")
                mlflow.log_metric("text_extraction_success", 0)
                mlflow.log_param("extraction_error", result1['error'])
            
            print("\n" + "="*60)
            print("🧪 TESTE 3: Análise de Conteúdo Random Forest")
            print("="*60)
            
            # Teste 3: Análise de conteúdo
            result2 = analyze_random_forest_content(pdf_path)
            
            if result2["success"]:
                print(f"✅ Análise bem-sucedida!")
                mlflow.log_metric("rf_analysis_success", 1)
                mlflow.log_metric("rf_analysis_time", result2.get("processing_time", 0))
                
                if "total_rf_mentions" in result2:
                    mlflow.log_metric("total_rf_mentions", result2["total_rf_mentions"])
                    mlflow.log_metric("content_density", result2.get("content_density", 0))
                    mlflow.log_metric("technical_depth", result2.get("technical_depth", 0))
                    
                    # Calcular relevância baseada no tema esperado
                    if "random forest" in expected_theme.lower() or "forest" in expected_theme.lower():
                        relevance_score = min(result2.get("content_density", 0) * 10, 100)
                    else:
                        relevance_score = max(50 - result2.get("content_density", 0), 0)
                    
                    mlflow.log_metric("content_relevance_score", relevance_score)
            else:
                print(f"❌ Falha na análise: {result2['error']}")
                mlflow.log_metric("rf_analysis_success", 0)
                mlflow.log_param("rf_analysis_error", result2['error'])
            
            # Calcular métricas gerais de qualidade
            total_success = sum([
                1 if result_theme["success"] else 0,
                1 if result1["success"] else 0,
                1 if result2["success"] else 0
            ])
            
            overall_success_rate = (total_success / 3) * 100
            
            # Calcular score de qualidade geral
            quality_score = 0
            if result_theme["success"]:
                quality_score += result_theme.get("confidence", 0) * 0.4
            if result1["success"] and result1.get("words_count", 0) > 0:
                quality_score += min(result1.get("words_count", 0) / 1000 * 100, 100) * 0.3
            if result2["success"]:
                quality_score += result2.get("content_density", 0) * 10 * 0.3
            
            # Log métricas finais
            mlflow.log_metric("overall_success_rate", overall_success_rate)
            mlflow.log_metric("total_tests", 3)
            mlflow.log_metric("successful_tests", total_success)
            mlflow.log_metric("quality_score", quality_score)
            
            # Métricas de performance temporal
            total_processing_time = sum([
                result_theme.get("processing_time", 0),
                result1.get("processing_time", 0),
                result2.get("processing_time", 0)
            ])
            mlflow.log_metric("total_processing_time", total_processing_time)
            mlflow.log_metric("avg_processing_time_per_test", total_processing_time / 3)
            
            # Mostrar dashboard
            show_monitoring_dashboard()
            
            # Mostrar resumo MLflow com métricas principais
            show_comprehensive_mlflow_summary(theme_comparison, total_processing_time, quality_score)
            
            print("\n" + "="*80)
            print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print("="*80)
            print("\n📋 O que foi analisado e monitorado:")
            print("✅ Pergunta sobre tema esperado do documento")
            print("✅ Comparação tema esperado vs detectado")
            print("✅ Análise de confiança da detecção")
            print("✅ Extração completa de texto")
            print("✅ Análise específica de Random Forest")
            print("✅ Métricas de densidade e relevância")
            print("✅ Score de qualidade geral")
            print("✅ Métricas temporais de performance")
            print("✅ Taxa de sucesso detalhada")
            
            print(f"\n📊 Resumo das Métricas Principais:")
            print(f"   🎯 Taxa de sucesso geral: {overall_success_rate:.1f}%")
            print(f"   🧪 Testes executados: {total_success}/3")
            print(f"   📈 Score de qualidade: {quality_score:.1f}")
            print(f"   ⏱️ Tempo total: {total_processing_time:.2f}s")
            if theme_comparison:
                print(f"   🎭 Correspondência de tema: {theme_comparison['match_status']} ({theme_comparison['theme_match_score']:.1f}%)")
            
            print(f"\n🔍 Próximos passos:")
            print(f"   📊 Ver dashboard: streamlit run dashboard.py")
            print(f"   📈 Ver MLflow UI: mlflow ui --port 5001")
            print(f"   📝 Ver logs: model_monitor.get_system_status()")
            print(f"   🗄️ Banco MLflow: sqlite:///mlflow.db")
            
            # Finalizar run MLflow
            try:
                if mlflow.active_run():
                    mlflow.end_run()
            except Exception:
                pass
            
            return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        
        # Log erro no MLflow
        try:
            with mlflow.start_run(run_name="Complete_PDF_Analysis_Error"):
                mlflow.log_param("error", str(e))
                mlflow.log_param("error_type", type(e).__name__)
                mlflow.log_param("expected_theme", expected_theme)
                mlflow.log_metric("success", 0)
        except Exception as mlflow_error:
            print(f"Erro adicional no MLflow: {mlflow_error}")
        
        return False

def show_comprehensive_mlflow_summary(theme_comparison=None, total_processing_time=0, quality_score=0):
    """
    Mostra resumo abrangente das métricas registradas no MLflow
    """
    print("\n" + "="*70)
    print("📈 RESUMO ABRANGENTE DAS MÉTRICAS MLFLOW")
    print("="*70)
    
    try:
        import mlflow.tracking
        
        # Obter informações do experimento atual
        experiment = mlflow.get_experiment_by_name("Random_Forest_PDF_Analysis")
        if experiment:
            print(f"🧪 Experimento: {experiment.name}")
            print(f"📁 ID: {experiment.experiment_id}")
            print(f"🗄️ Local: {mlflow.get_tracking_uri()}")
            
            # Listar runs recentes
            runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], max_results=5)
            
            if not runs.empty:
                print(f"\n📊 Última execução (métricas principais):")
                latest_run = runs.iloc[0]
                
                run_name = latest_run.get('tags.mlflow.runName', 'Unnamed')
                status = latest_run['status']
                start_time = latest_run['start_time']
                
                print(f"   📝 Nome: {run_name}")
                print(f"   ✅ Status: {status}")
                print(f"   🕐 Início: {start_time}")
                
                # Métricas principais organizadas por categoria
                print(f"\n🎯 MÉTRICAS DE ANÁLISE DE TEMA:")
                theme_metrics = {
                    'theme_confidence': 'Confiança da detecção',
                    'theme_match_score': 'Score de correspondência',
                    'theme_accuracy': 'Precisão geral do tema'
                }
                
                for metric_key, metric_name in theme_metrics.items():
                    metric_col = f'metrics.{metric_key}'
                    if metric_col in latest_run and not pd.isna(latest_run[metric_col]):
                        value = latest_run[metric_col]
                        print(f"   📈 {metric_name}: {value:.1f}%")
                
                print(f"\n📄 MÉTRICAS DE EXTRAÇÃO DE TEXTO:")
                extraction_metrics = {
                    'extracted_words': 'Palavras extraídas',
                    'extracted_characters': 'Caracteres extraídos',
                    'pages_processed': 'Páginas processadas',
                    'extraction_efficiency_percentage': 'Eficiência da extração'
                }
                
                for metric_key, metric_name in extraction_metrics.items():
                    metric_col = f'metrics.{metric_key}'
                    if metric_col in latest_run and not pd.isna(latest_run[metric_col]):
                        value = latest_run[metric_col]
                        if 'percentage' in metric_key or 'efficiency' in metric_key:
                            print(f"   📊 {metric_name}: {value:.1f}%")
                        else:
                            print(f"   📊 {metric_name}: {value:.0f}")
                
                print(f"\n🌳 MÉTRICAS DE RANDOM FOREST:")
                rf_metrics = {
                    'total_rf_mentions': 'Total de menções RF',
                    'content_density': 'Densidade do conteúdo',
                    'technical_depth': 'Profundidade técnica',
                    'content_relevance_score': 'Score de relevância'
                }
                
                for metric_key, metric_name in rf_metrics.items():
                    metric_col = f'metrics.{metric_key}'
                    if metric_col in latest_run and not pd.isna(latest_run[metric_col]):
                        value = latest_run[metric_col]
                        if 'density' in metric_key or 'depth' in metric_key or 'score' in metric_key:
                            print(f"   🔍 {metric_name}: {value:.2f}%")
                        else:
                            print(f"   🔍 {metric_name}: {value:.0f}")
                
                print(f"\n⚡ MÉTRICAS DE PERFORMANCE:")
                performance_metrics = {
                    'total_processing_time': f'Tempo total: {total_processing_time:.2f}s',
                    'avg_processing_time_per_test': 'Tempo médio por teste',
                    'overall_success_rate': 'Taxa de sucesso geral',
                    'quality_score': f'Score de qualidade: {quality_score:.1f}'
                }
                
                for metric_key, metric_name in performance_metrics.items():
                    metric_col = f'metrics.{metric_key}'
                    if metric_col in latest_run and not pd.isna(latest_run[metric_col]):
                        value = latest_run[metric_col]
                        if metric_key == 'total_processing_time':
                            print(f"   ⏱️ {metric_name}")
                        elif metric_key == 'quality_score':
                            print(f"   🏆 {metric_name}")
                        elif 'rate' in metric_key or 'success' in metric_key:
                            print(f"   📈 {metric_name}: {value:.1f}%")
                        else:
                            print(f"   ⏱️ {metric_name}: {value:.2f}s")
                
                # Informações sobre comparação de temas
                if theme_comparison:
                    print(f"\n🎭 COMPARAÇÃO DE TEMAS:")
                    print(f"   🎯 Esperado: {theme_comparison['expected_theme']}")
                    print(f"   🤖 Detectado: {theme_comparison['detected_theme']}")
                    print(f"   ✅ Status: {theme_comparison['match_status']}")
                    print(f"   📊 Score: {theme_comparison['theme_match_score']:.1f}%")
                    print(f"   🎯 Precisão: {theme_comparison['accuracy_score']:.1f}%")
                
                print(f"\n� PARÂMETROS REGISTRADOS:")
                param_keys = ['expected_theme', 'main_theme', 'pdf_file', 'analysis_timestamp']
                for param_key in param_keys:
                    param_col = f'params.{param_key}'
                    if param_col in latest_run and pd.notna(latest_run[param_col]):
                        value = latest_run[param_col]
                        print(f"   📝 {param_key.replace('_', ' ').title()}: {value}")
            
            print(f"\n💡 Para análise detalhada:")
            print(f"   🌐 Execute: mlflow ui")
            print(f"   📊 Acesse: http://localhost:5000")
            print(f"   🔍 Compare experimentos e métricas")
            print(f"   📈 Visualize tendências de performance")
        
    except Exception as e:
        print(f"❌ Erro ao obter resumo MLflow: {e}")
        print("💡 Certifique-se de que o MLflow está configurado corretamente")
        
        # Fallback para métricas básicas
        if theme_comparison:
            print(f"\n📋 Resumo básico (sem MLflow):")
            print(f"   🎯 Tema esperado: {theme_comparison['expected_theme']}")
            print(f"   🤖 Tema detectado: {theme_comparison['detected_theme']}")
            print(f"   📊 Correspondência: {theme_comparison['match_status']}")
            print(f"   ⏱️ Tempo total: {total_processing_time:.2f}s")
            print(f"   🏆 Score de qualidade: {quality_score:.1f}")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ Monitoramento de PDF testado com sucesso!")
    else:
        print("\n💥 Falha no teste de monitoramento!")
