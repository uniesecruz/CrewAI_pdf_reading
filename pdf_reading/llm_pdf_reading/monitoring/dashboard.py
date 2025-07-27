"""
Interface web para monitoramento e dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from llm_pdf_reading.monitoring import (
    model_monitor,
    performance_tracker,
    experiment_manager,
    metrics_collector
)

def create_monitoring_dashboard():
    """Cria dashboard de monitoramento no Streamlit"""
    
    st.set_page_config(
        page_title="🔍 LLM PDF Reading - Monitoramento",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 Dashboard de Monitoramento")
    st.markdown("Monitoramento em tempo real de modelos LLM e processamento de PDFs")
    
    # Sidebar para controles
    with st.sidebar:
        st.header("⚙️ Controles")
        
        # Controle de monitoramento
        if st.button("▶️ Iniciar Monitoramento" if not model_monitor.is_monitoring else "⏹️ Parar Monitoramento"):
            if not model_monitor.is_monitoring:
                model_monitor.start_monitoring()
                st.success("Monitoramento iniciado")
            else:
                model_monitor.stop_monitoring()
                st.success("Monitoramento parado")
            st.rerun()
        
        st.markdown("---")
        
        # Configurações de refresh
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)
        refresh_interval = st.slider("Intervalo (segundos)", 1, 30, 5)
        
        if auto_refresh:
            st.empty()  # Placeholder para auto-refresh
        
        if st.button("🔄 Atualizar Agora"):
            st.rerun()
        
        st.markdown("---")
        
        # Ações
        if st.button("📊 Exportar Dados"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_monitor.export_monitoring_data(f"monitoring_data_{timestamp}.json")
            st.success("Dados exportados!")
        
        if st.button("🗑️ Limpar Estatísticas"):
            model_monitor.reset_stats()
            performance_tracker.clear_history()
            st.success("Estatísticas limpas!")
    
    # Layout principal com tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral",
        "🤖 Modelos",
        "⚡ Performance",
        "📈 MLflow",
        "🔧 Sistema"
    ])
    
    with tab1:
        show_overview_tab()
    
    with tab2:
        show_models_tab()
    
    with tab3:
        show_performance_tab()
    
    with tab4:
        show_mlflow_tab()
    
    with tab5:
        show_system_tab()

def show_overview_tab():
    """Tab de visão geral"""
    st.subheader("📊 Visão Geral do Sistema")
    
    # Status geral
    system_status = model_monitor.get_system_status()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🚀 Status",
            "🟢 Ativo" if system_status['monitoring_active'] else "🔴 Inativo",
            delta=None
        )
    
    with col2:
        st.metric(
            "⏱️ Uptime",
            system_status['uptime_formatted'],
            delta=None
        )
    
    with col3:
        st.metric(
            "📊 Disponibilidade",
            f"{system_status['availability']:.1%}",
            delta=f"Alvo: 95%" if system_status['availability'] < 0.95 else "✅ Meta atingida"
        )
    
    with col4:
        st.metric(
            "⚡ Tempo Médio",
            f"{system_status['avg_response_time']:.2f}s",
            delta="Bom" if system_status['avg_response_time'] < 5 else "Alto"
        )
    
    # Gráficos em tempo real
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Tempo de Resposta")
        real_time_data = model_monitor.get_real_time_metrics()
        
        if real_time_data['response_times']:
            df_response = pd.DataFrame({
                'Index': range(len(real_time_data['response_times'])),
                'Response Time (s)': real_time_data['response_times']
            })
            
            fig = px.line(df_response, x='Index', y='Response Time (s)', 
                         title="Últimas Requisições")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado de tempo de resposta disponível")
    
    with col2:
        st.subheader("💾 Uso de Memória")
        
        if real_time_data['memory_usage']:
            df_memory = pd.DataFrame({
                'Index': range(len(real_time_data['memory_usage'])),
                'Memory Usage (%)': real_time_data['memory_usage']
            })
            
            fig = px.line(df_memory, x='Index', y='Memory Usage (%)', 
                         title="Uso de Memória")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado de memória disponível")
    
    # Atividade recente
    st.subheader("🕒 Atividade Recente")
    
    current_operations = real_time_data['current_operations']
    if current_operations:
        df_ops = pd.DataFrame([
            {
                'Operação': op_data['operation'],
                'Duração (s)': f"{op_data['duration_so_far']:.2f}",
                'Início': op_data['start_time']
            }
            for op_id, op_data in current_operations.items()
        ])
        st.dataframe(df_ops, use_container_width=True)
    else:
        st.info("Nenhuma operação em execução")

def show_models_tab():
    """Tab de status dos modelos"""
    st.subheader("🤖 Status dos Modelos")
    
    real_time_data = model_monitor.get_real_time_metrics()
    model_states = real_time_data['model_states']
    
    if model_states:
        # Resumo dos modelos
        col1, col2, col3 = st.columns(3)
        
        active_models = sum(1 for state in model_states.values() if state['status'] == 'active')
        total_requests = sum(state['total_requests'] for state in model_states.values())
        avg_response_time = sum(state['avg_response_time'] for state in model_states.values()) / len(model_states)
        
        with col1:
            st.metric("🟢 Modelos Ativos", active_models)
        
        with col2:
            st.metric("📊 Total de Requisições", total_requests)
        
        with col3:
            st.metric("⚡ Tempo Médio", f"{avg_response_time:.2f}s")
        
        # Tabela detalhada dos modelos
        st.subheader("📋 Detalhes dos Modelos")
        
        model_data = []
        for name, state in model_states.items():
            success_rate = (state['total_requests'] - 0) / state['total_requests'] if state['total_requests'] > 0 else 0
            
            model_data.append({
                'Modelo': name,
                'Status': "🟢 Ativo" if state['status'] == 'active' else "🔴 Inativo",
                'Requisições': state['total_requests'],
                'Taxa de Sucesso': f"{success_rate:.1%}",
                'Tempo Médio (s)': f"{state['avg_response_time']:.2f}",
                'Última Atividade': state['last_activity'] or "Nunca"
            })
        
        df_models = pd.DataFrame(model_data)
        st.dataframe(df_models, use_container_width=True)
        
        # Gráfico de distribuição de tempo de resposta
        st.subheader("📊 Distribuição de Performance")
        
        model_names = list(model_states.keys())
        response_times = [state['avg_response_time'] for state in model_states.values()]
        request_counts = [state['total_requests'] for state in model_states.values()]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=model_names,
            y=response_times,
            name="Tempo de Resposta (s)",
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title="Tempo de Resposta por Modelo",
            xaxis_title="Modelos",
            yaxis_title="Tempo (segundos)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Nenhum modelo monitorado ainda")

def show_performance_tab():
    """Tab de performance detalhada"""
    st.subheader("⚡ Análise de Performance")
    
    # Resumo de performance
    perf_summary = performance_tracker.get_performance_summary()
    
    if perf_summary:
        st.subheader("📊 Resumo de Operações")
        
        perf_data = []
        for operation, stats in perf_summary.items():
            perf_data.append({
                'Operação': operation,
                'Execuções': stats['count'],
                'Tempo Médio (s)': f"{stats['avg_duration']:.2f}",
                'Tempo Mín (s)': f"{stats['min_duration']:.2f}",
                'Tempo Máx (s)': f"{stats['max_duration']:.2f}",
                'Mediana (s)': f"{stats['median_duration']:.2f}",
                'P95 (s)': f"{stats.get('p95', 0):.2f}",
                'P99 (s)': f"{stats.get('p99', 0):.2f}"
            })
        
        df_perf = pd.DataFrame(perf_data)
        st.dataframe(df_perf, use_container_width=True)
        
        # Gráficos de performance
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Tendência de Performance")
            
            # Criar gráfico de tendência (simplificado)
            operations = list(perf_summary.keys())
            avg_times = [stats['avg_duration'] for stats in perf_summary.values()]
            
            fig = px.bar(
                x=operations,
                y=avg_times,
                title="Tempo Médio por Operação"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Distribuição de Tempos")
            
            # Box plot dos tempos (simulado)
            fig = go.Figure()
            
            for operation, stats in perf_summary.items():
                fig.add_trace(go.Box(
                    y=[stats['min_duration'], stats['avg_duration'], stats['max_duration']],
                    name=operation,
                    boxmean=True
                ))
            
            fig.update_layout(
                title="Distribuição de Tempos de Execução",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("Nenhum dado de performance disponível")

def show_mlflow_tab():
    """Tab de experimentos MLflow"""
    st.subheader("📈 Experimentos MLflow")
    
    if experiment_manager.mlflow_available:
        st.success("✅ MLflow conectado")
        
        # Informações do experimento atual
        if experiment_manager.current_run:
            st.info(f"🏃‍♂️ Execução ativa: {experiment_manager.current_run.info.run_id}")
        else:
            st.warning("⚠️ Nenhuma execução ativa")
        
        # Controles MLflow
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Iniciar Nova Execução"):
                run_id = experiment_manager.start_run(
                    run_name=f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    tags={'source': 'dashboard', 'user': 'manual'}
                )
                if run_id:
                    st.success(f"Execução iniciada: {run_id}")
                    st.rerun()
        
        with col2:
            if st.button("⏹️ Finalizar Execução"):
                experiment_manager.end_run()
                st.success("Execução finalizada")
                st.rerun()
        
        with col3:
            if st.button("📊 Exportar Dados"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                experiment_manager.export_experiment_data(f"mlflow_data_{timestamp}.csv")
                st.success("Dados exportados!")
        
        # Comparação de modelos (simplificado)
        st.subheader("🔍 Comparação de Modelos")
        
        # Interface para comparar modelos
        model_names_input = st.text_input(
            "Modelos para comparar (separados por vírgula)",
            placeholder="llama2:7b, mistral:7b, gpt-3.5-turbo"
        )
        
        metric_to_compare = st.selectbox(
            "Métrica para comparação",
            ["response_time", "input_tokens", "output_tokens", "tokens_per_second"]
        )
        
        if st.button("📊 Comparar") and model_names_input:
            model_list = [m.strip() for m in model_names_input.split(',')]
            comparison = experiment_manager.compare_models(model_list, metric_to_compare)
            
            if comparison:
                df_comparison = pd.DataFrame([
                    {
                        'Modelo': model,
                        'Run ID': data['run_id'][:8] + '...',
                        metric_to_compare.title(): data.get(metric_to_compare, 'N/A'),
                        'Status': data['status']
                    }
                    for model, data in comparison.items()
                ])
                st.dataframe(df_comparison, use_container_width=True)
            else:
                st.warning("Nenhum dado encontrado para os modelos especificados")
        
        # Melhor modelo
        st.subheader("🏆 Melhor Modelo")
        best_model = experiment_manager.get_best_model(metric_to_compare)
        
        if best_model:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏆 Modelo", best_model.get('model_name', 'N/A'))
            with col2:
                st.metric("🔧 Provedor", best_model.get('provider', 'N/A'))
            with col3:
                st.metric("📊 Métrica", f"{best_model.get(metric_to_compare, 0):.2f}")
        else:
            st.info("Nenhum dado de modelo disponível")
    
    else:
        st.error("❌ MLflow não disponível")
        st.markdown("""
        Para usar MLflow:
        ```bash
        pip install mlflow
        ```
        """)

def show_system_tab():
    """Tab de métricas do sistema"""
    st.subheader("🔧 Métricas do Sistema")
    
    # Coletar métricas atuais
    system_metrics = metrics_collector.collect_system_metrics()
    
    # Exibir métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🖥️ CPU", f"{system_metrics.cpu_usage:.1f}%")
    
    with col2:
        st.metric("💾 Memória", f"{system_metrics.memory_usage:.1f}%")
    
    with col3:
        st.metric("💿 Disco", f"{system_metrics.disk_usage:.1f}%")
    
    with col4:
        if system_metrics.gpu_utilization:
            st.metric("🎮 GPU", f"{system_metrics.gpu_utilization:.1f}%")
        else:
            st.metric("🎮 GPU", "N/A")
    
    # Informações detalhadas
    st.subheader("📊 Informações Detalhadas")
    
    system_info = {
        'Timestamp': system_metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'CPU Usage (%)': system_metrics.cpu_usage,
        'Memory Usage (%)': system_metrics.memory_usage,
        'Disk Usage (%)': system_metrics.disk_usage,
        'GPU Memory (%)': system_metrics.gpu_memory or 'N/A',
        'GPU Utilization (%)': system_metrics.gpu_utilization or 'N/A'
    }
    
    for key, value in system_info.items():
        st.text(f"{key}: {value}")
    
    # Network I/O
    if system_metrics.network_io:
        st.subheader("🌐 Network I/O")
        col1, col2 = st.columns(2)
        
        with col1:
            bytes_sent = system_metrics.network_io.get('bytes_sent', 0)
            st.metric("📤 Bytes Sent", f"{bytes_sent / 1024 / 1024:.2f} MB")
        
        with col2:
            bytes_recv = system_metrics.network_io.get('bytes_recv', 0)
            st.metric("📥 Bytes Received", f"{bytes_recv / 1024 / 1024:.2f} MB")
    
    # Resumo de métricas coletadas
    st.subheader("📈 Resumo de Métricas")
    metrics_summary = metrics_collector.get_metrics_summary()
    
    if metrics_summary:
        for key, value in metrics_summary.items():
            if isinstance(value, (int, float)):
                st.text(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
            else:
                st.text(f"{key}: {value}")
    else:
        st.info("Nenhuma métrica coletada ainda")

if __name__ == "__main__":
    create_monitoring_dashboard()
