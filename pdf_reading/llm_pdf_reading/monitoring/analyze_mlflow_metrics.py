#!/usr/bin/env python3
"""
Script para analisar e visualizar as métricas do MLflow
do teste de análise de PDF Random Forest
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import mlflow
import mlflow.tracking

def analyze_mlflow_metrics():
    """
    Analisa as métricas registradas no MLflow de forma detalhada
    """
    print("📈 ANÁLISE DETALHADA DAS MÉTRICAS MLFLOW")
    print("="*70)
    
    # Configurar MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    
    try:
        # Obter experimento
        experiment = mlflow.get_experiment_by_name("Random_Forest_PDF_Analysis")
        if not experiment:
            print("❌ Experimento não encontrado!")
            return
        
        print(f"🧪 Experimento: {experiment.name}")
        print(f"📁 ID: {experiment.experiment_id}")
        print(f"🗄️ URI: {mlflow.get_tracking_uri()}")
        
        # Buscar todas as execuções
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        if runs.empty:
            print("❌ Nenhuma execução encontrada!")
            return
        
        print(f"\n📊 Total de execuções encontradas: {len(runs)}")
        
        # Analisar a execução mais recente
        latest_run = runs.iloc[0]
        
        print(f"\n🔍 ANÁLISE DA EXECUÇÃO MAIS RECENTE:")
        print(f"   📝 Nome: {latest_run.get('tags.mlflow.runName', 'N/A')}")
        print(f"   ✅ Status: {latest_run['status']}")
        print(f"   🕐 Início: {latest_run['start_time']}")
        print(f"   🏁 Fim: {latest_run.get('end_time', 'N/A')}")
        
        # Separar métricas por categoria
        metrics_columns = [col for col in runs.columns if col.startswith('metrics.')]
        params_columns = [col for col in runs.columns if col.startswith('params.')]
        
        print(f"\n📊 MÉTRICAS REGISTRADAS ({len(metrics_columns)} métricas):")
        
        # Categorizar métricas
        theme_metrics = []
        extraction_metrics = []
        rf_metrics = []
        performance_metrics = []
        success_metrics = []
        
        for col in metrics_columns:
            metric_name = col.replace('metrics.', '')
            value = latest_run[col]
            
            if pd.notna(value):
                if 'theme' in metric_name:
                    theme_metrics.append((metric_name, value))
                elif 'extract' in metric_name or 'pages' in metric_name or 'words' in metric_name or 'characters' in metric_name:
                    extraction_metrics.append((metric_name, value))
                elif 'rf_' in metric_name or 'content_' in metric_name or 'technical_' in metric_name:
                    rf_metrics.append((metric_name, value))
                elif 'time' in metric_name or 'efficiency' in metric_name:
                    performance_metrics.append((metric_name, value))
                elif 'success' in metric_name or 'rate' in metric_name or 'score' in metric_name:
                    success_metrics.append((metric_name, value))
        
        # Exibir métricas por categoria
        if theme_metrics:
            print(f"\n🎯 MÉTRICAS DE ANÁLISE DE TEMA:")
            for metric, value in theme_metrics:
                if 'percentage' in metric or 'confidence' in metric:
                    print(f"   📈 {metric.replace('_', ' ').title()}: {value:.1f}%")
                else:
                    print(f"   📈 {metric.replace('_', ' ').title()}: {value:.2f}")
        
        if extraction_metrics:
            print(f"\n📄 MÉTRICAS DE EXTRAÇÃO DE TEXTO:")
            for metric, value in extraction_metrics:
                if 'percentage' in metric or 'efficiency' in metric:
                    print(f"   📊 {metric.replace('_', ' ').title()}: {value:.1f}%")
                elif 'time' in metric:
                    print(f"   ⏱️ {metric.replace('_', ' ').title()}: {value:.3f}s")
                else:
                    print(f"   📊 {metric.replace('_', ' ').title()}: {value:.0f}")
        
        if rf_metrics:
            print(f"\n🌳 MÉTRICAS DE RANDOM FOREST:")
            for metric, value in rf_metrics:
                if 'percentage' in metric or 'density' in metric or 'depth' in metric:
                    print(f"   🔍 {metric.replace('_', ' ').title()}: {value:.2f}%")
                else:
                    print(f"   🔍 {metric.replace('_', ' ').title()}: {value:.0f}")
        
        if performance_metrics:
            print(f"\n⚡ MÉTRICAS DE PERFORMANCE:")
            for metric, value in performance_metrics:
                print(f"   ⏱️ {metric.replace('_', ' ').title()}: {value:.3f}s")
        
        if success_metrics:
            print(f"\n🏆 MÉTRICAS DE SUCESSO E QUALIDADE:")
            for metric, value in success_metrics:
                if 'rate' in metric or 'percentage' in metric:
                    print(f"   📈 {metric.replace('_', ' ').title()}: {value:.1f}%")
                else:
                    print(f"   🏆 {metric.replace('_', ' ').title()}: {value:.1f}")
        
        # Parâmetros registrados
        print(f"\n📋 PARÂMETROS REGISTRADOS ({len(params_columns)} parâmetros):")
        for col in params_columns:
            param_name = col.replace('params.', '')
            value = latest_run[col]
            if pd.notna(value):
                print(f"   📝 {param_name.replace('_', ' ').title()}: {value}")
        
        # Estatísticas gerais
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        
        # Calcular métricas médias se houver múltiplas execuções
        if len(runs) > 1:
            print(f"   📈 Total de execuções: {len(runs)}")
            
            # Métricas de sucesso médias
            success_cols = [col for col in metrics_columns if 'success' in col]
            for col in success_cols:
                if col in runs.columns:
                    avg_success = runs[col].mean() * 100
                    print(f"   ✅ {col.replace('metrics.', '').replace('_', ' ').title()} médio: {avg_success:.1f}%")
            
            # Tempo médio de processamento
            time_cols = [col for col in metrics_columns if 'time' in col]
            for col in time_cols:
                if col in runs.columns:
                    avg_time = runs[col].mean()
                    print(f"   ⏱️ {col.replace('metrics.', '').replace('_', ' ').title()} médio: {avg_time:.3f}s")
        
        # Insights e recomendações
        print(f"\n💡 INSIGHTS E RECOMENDAÇÕES:")
        
        # Análise de tema
        theme_confidence = latest_run.get('metrics.theme_confidence', 0)
        if theme_confidence < 20:
            print(f"   ⚠️ Confiança do tema baixa ({theme_confidence:.1f}%) - considere melhorar o algoritmo de detecção")
        elif theme_confidence > 80:
            print(f"   ✅ Excelente confiança do tema ({theme_confidence:.1f}%)")
        
        # Análise de extração
        extraction_efficiency = latest_run.get('metrics.extraction_efficiency_percentage', 100)
        if extraction_efficiency < 50:
            print(f"   ⚠️ Eficiência de extração baixa ({extraction_efficiency:.1f}%) - processar mais páginas")
        
        # Análise de conteúdo RF
        content_density = latest_run.get('metrics.content_density', 0)
        if content_density > 5:
            print(f"   ✅ Alta densidade de conteúdo Random Forest ({content_density:.2f}%)")
        elif content_density < 1:
            print(f"   ⚠️ Baixa densidade de conteúdo Random Forest ({content_density:.2f}%)")
        
        print(f"\n🔗 PRÓXIMOS PASSOS:")
        print(f"   🌐 Iniciar MLflow UI: mlflow ui")
        print(f"   📊 Acessar dashboard: http://localhost:5000")
        print(f"   📈 Comparar execuções para identificar padrões")
        print(f"   🔍 Analisar correlações entre métricas")
        print(f"   📋 Exportar dados: mlflow.search_runs()")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

def generate_metrics_summary():
    """
    Gera um resumo das principais métricas para relatório
    """
    print(f"\n" + "="*70)
    print("📋 RESUMO EXECUTIVO DAS MÉTRICAS")
    print("="*70)
    
    try:
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        experiment = mlflow.get_experiment_by_name("Random_Forest_PDF_Analysis")
        
        if experiment:
            runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], max_results=1)
            
            if not runs.empty:
                latest_run = runs.iloc[0]
                
                print(f"🎯 RESUMO DA ANÁLISE:")
                print(f"   📄 Documento: {latest_run.get('params.pdf_file', 'N/A')}")
                print(f"   🎭 Tema esperado: {latest_run.get('params.expected_theme', 'N/A')}")
                print(f"   🤖 Tema detectado: {latest_run.get('params.main_theme', 'N/A')}")
                print(f"   📈 Confiança: {latest_run.get('metrics.theme_confidence', 0):.1f}%")
                print(f"   🎯 Correspondência: {latest_run.get('metrics.theme_match_score', 0):.1f}%")
                
                print(f"\n📊 PERFORMANCE:")
                print(f"   ✅ Taxa de sucesso geral: {latest_run.get('metrics.overall_success_rate', 0):.1f}%")
                print(f"   🏆 Score de qualidade: {latest_run.get('metrics.quality_score', 0):.1f}")
                print(f"   ⏱️ Tempo total: {latest_run.get('metrics.total_processing_time', 0):.2f}s")
                
                print(f"\n🌳 ANÁLISE DE CONTEÚDO:")
                print(f"   📝 Palavras extraídas: {latest_run.get('metrics.extracted_words', 0):.0f}")
                print(f"   🔍 Menções Random Forest: {latest_run.get('metrics.total_rf_mentions', 0):.0f}")
                print(f"   📈 Densidade do conteúdo: {latest_run.get('metrics.content_density', 0):.2f}%")
                print(f"   🎯 Profundidade técnica: {latest_run.get('metrics.technical_depth', 0):.1f}%")
                
                print(f"\n💡 CONCLUSÃO:")
                overall_success = latest_run.get('metrics.overall_success_rate', 0)
                if overall_success == 100:
                    print(f"   🎉 Análise completamente bem-sucedida!")
                elif overall_success >= 66:
                    print(f"   ✅ Análise majoritariamente bem-sucedida")
                else:
                    print(f"   ⚠️ Análise com limitações - revisar configurações")
    
    except Exception as e:
        print(f"❌ Erro no resumo: {e}")

def main():
    """
    Função principal para análise das métricas MLflow
    """
    print("📊 ANALISADOR DE MÉTRICAS MLFLOW - RANDOM FOREST PDF")
    print("="*70)
    
    # Verificar se o banco MLflow existe
    if not os.path.exists("mlflow.db"):
        print("❌ Banco de dados MLflow não encontrado!")
        print("💡 Execute primeiro: python test_random_forest_pdf.py")
        return
    
    # Executar análises
    analyze_mlflow_metrics()
    generate_metrics_summary()
    
    print(f"\n✨ Análise concluída! Use 'mlflow ui' para explorar visualmente.")

if __name__ == "__main__":
    main()
