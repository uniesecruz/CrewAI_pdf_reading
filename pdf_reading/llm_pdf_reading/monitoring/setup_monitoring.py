#!/usr/bin/env python3
"""
Script de configuração rápida do sistema de monitoramento
Execute este script para configurar tudo automaticamente
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🔧 {text}")
    print("="*60)

def print_step(step_num, text):
    """Imprime passo numerado"""
    print(f"\n📋 Passo {step_num}: {text}")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"✅ {text}")

def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"⚠️ {text}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"❌ {text}")

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ é necessário")
        return False
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_packages():
    """Instala pacotes opcionais para monitoramento"""
    packages = [
        ("mlflow", "MLflow para rastreamento de experimentos"),
        ("psutil", "Métricas de sistema"),
        ("GPUtil", "Monitoramento de GPU"),
        ("streamlit", "Dashboard web"),
        ("plotly", "Gráficos interativos"),
        ("pandas", "Manipulação de dados")
    ]
    
    print_step(1, "Instalando dependências opcionais")
    
    for package, description in packages:
        try:
            __import__(package)
            print_success(f"{package} já instalado ({description})")
        except ImportError:
            print(f"📦 Instalando {package} ({description})...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print_success(f"{package} instalado com sucesso")
            except subprocess.CalledProcessError:
                print_warning(f"Falha ao instalar {package} - funcionalidade limitada")

def setup_directories():
    """Cria diretórios necessários"""
    print_step(2, "Configurando diretórios")
    
    base_dir = Path(__file__).parent
    dirs_to_create = [
        base_dir / "monitoring_data",
        base_dir / "monitoring_data" / "logs",
        base_dir / "monitoring_data" / "exports",
        base_dir / "monitoring_data" / "mlflow"
    ]
    
    for dir_path in dirs_to_create:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Diretório criado: {dir_path}")
        except Exception as e:
            print_error(f"Erro ao criar {dir_path}: {e}")

def test_monitoring_system():
    """Testa se o sistema de monitoramento está funcionando"""
    print_step(3, "Testando sistema de monitoramento")
    
    try:
        # Adicionar path do projeto
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        # Testar imports das classes individualmente
        from llm_pdf_reading.monitoring.metrics_collector import MetricsCollector
        from llm_pdf_reading.monitoring.performance_tracker import PerformanceTracker
        from llm_pdf_reading.monitoring.experiment_manager import ExperimentManager
        from llm_pdf_reading.monitoring.model_monitor import ModelMonitor
        
        print_success("Classes de monitoramento importadas")
        
        # Testar cada funcionalidade individualmente
        print("🔍 Testando MetricsCollector...")
        metrics_collector = MetricsCollector()
        if metrics_collector is not None:
            system_metrics = metrics_collector.collect_system_metrics()
            if system_metrics is not None:
                print_success(f"Métricas do sistema coletadas: CPU {system_metrics.cpu_usage:.1f}%")
            else:
                print_warning("Métricas do sistema retornaram None")
        else:
            print_error("MetricsCollector retornou None")
            return False
        
        print("🔍 Testando PerformanceTracker...")
        performance_tracker = PerformanceTracker()
        if performance_tracker is not None:
            with performance_tracker.track_operation("test_operation"):
                import time
                time.sleep(0.1)
            print_success("Performance tracker funcionando")
        else:
            print_error("PerformanceTracker retornou None")
            return False
        
        print("🔍 Testando ExperimentManager...")
        experiment_manager = ExperimentManager()
        if experiment_manager is not None:
            if experiment_manager.mlflow_available:
                print_success("MLflow disponível")
            else:
                print_warning("MLflow não disponível - funcionalidade limitada")
        else:
            print_error("ExperimentManager retornou None")
            return False
        
        print("🔍 Testando ModelMonitor...")
        model_monitor = ModelMonitor()
        if model_monitor is not None:
            print_success("ModelMonitor criado com sucesso")
        else:
            print_error("ModelMonitor retornou None")
            return False
        
        print_success("Todos os testes passaram!")
        return True
        
    except Exception as e:
        print_error(f"Erro ao testar sistema: {e}")
        import traceback
        print("📋 Detalhes do erro:")
        traceback.print_exc()
        return False

def setup_mlflow():
    """Configura MLflow"""
    print_step(4, "Configurando MLflow")
    
    try:
        import mlflow
        
        # Configurar diretório de tracking (usar SQLite para Windows)
        mlflow_dir = Path(__file__).parent / "monitoring_data" / "mlflow"
        mlflow_dir.mkdir(parents=True, exist_ok=True)
        
        # Usar SQLite backend para compatibilidade
        db_path = mlflow_dir / "mlflow.db"
        mlflow_uri = f"sqlite:///{db_path}"
        
        mlflow.set_tracking_uri(mlflow_uri)
        print_success(f"MLflow tracking URI configurado: SQLite database")
        
        # Criar experimento padrão
        experiment_name = "llm_pdf_reading_default"
        try:
            experiment_id = mlflow.create_experiment(experiment_name)
            print_success(f"Experimento criado: {experiment_name} (ID: {experiment_id})")
        except Exception as e:
            # Experimento já existe ou outro erro
            try:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if experiment:
                    print_success(f"Usando experimento existente: {experiment_name}")
                else:
                    print_warning(f"Erro ao configurar experimento: {e}")
            except:
                print_warning("MLflow configurado, mas experimento padrão não pôde ser criado")
        
        mlflow.set_experiment(experiment_name)
        print_success("MLflow configurado com sucesso!")
        return True
        
    except ImportError:
        print_warning("MLflow não instalado - funcionalidade de experimentos limitada")
        return False
    except Exception as e:
        print_warning(f"Erro na configuração do MLflow: {e}")
        print_warning("MLflow disponível mas com funcionalidade limitada")
        return False

def create_startup_script():
    """Cria script de inicialização"""
    print_step(5, "Criando script de inicialização")
    
    startup_script = Path(__file__).parent / "start_monitoring.py"
    
    script_content = '''#!/usr/bin/env python3
"""
Script para iniciar o sistema de monitoramento
Execute este script no início da sua aplicação
"""

import sys
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from llm_pdf_reading.monitoring import model_monitor, experiment_manager

def start_monitoring():
    """Inicia o sistema de monitoramento"""
    print("🚀 Iniciando sistema de monitoramento...")
    
    # Configurar alertas
    def on_high_response_time(model_name: str, response_time: float):
        print(f"⚠️ ALERTA: {model_name} - Tempo alto: {response_time:.2f}s")
    
    def on_model_error(model_name: str, error: str):
        print(f"❌ ERRO: {model_name} - {error}")
    
    # Registrar callbacks
    model_monitor.add_alert_callback("high_response_time", on_high_response_time)
    model_monitor.add_alert_callback("model_error", on_model_error)
    
    # Iniciar monitoramento
    model_monitor.start_monitoring()
    print("✅ Monitoramento de modelos iniciado")
    
    # Iniciar sessão MLflow (se disponível)
    if experiment_manager.mlflow_available:
        run_id = experiment_manager.start_run(
            run_name="monitoring_session",
            tags={
                "project": "llm_pdf_reading",
                "environment": "development",
                "auto_started": "true"
            }
        )
        print(f"📊 Sessão MLflow iniciada: {run_id}")
    
    print("🎯 Sistema de monitoramento pronto!")
    return True

if __name__ == "__main__":
    start_monitoring()
'''
    
    try:
        with open(startup_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        startup_script.chmod(0o755)  # Tornar executável
        print_success(f"Script de inicialização criado: {startup_script}")
        return True
    except Exception as e:
        print_error(f"Erro ao criar script: {e}")
        return False

def create_dashboard_launcher():
    """Cria script para lançar dashboard"""
    print_step(6, "Criando launcher do dashboard")
    
    launcher_script = Path(__file__).parent / "launch_dashboard.py"
    
    launcher_content = '''#!/usr/bin/env python3
"""
Script para lançar o dashboard de monitoramento
"""

import sys
import subprocess
from pathlib import Path

def launch_dashboard():
    """Lança o dashboard Streamlit"""
    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit não instalado")
        print("📦 Instale com: pip install streamlit plotly pandas")
        return False
    
    dashboard_path = Path(__file__).parent / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard não encontrado: {dashboard_path}")
        return False
    
    print("🚀 Lançando dashboard...")
    print("📱 O dashboard abrirá no seu navegador")
    print("🔗 URL: http://localhost:8501")
    print("⏹️ Pressione Ctrl+C para parar")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n✅ Dashboard encerrado")
    except Exception as e:
        print(f"❌ Erro ao lançar dashboard: {e}")
        return False
    
    return True

if __name__ == "__main__":
    launch_dashboard()
'''
    
    try:
        with open(launcher_script, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        launcher_script.chmod(0o755)  # Tornar executável
        print_success(f"Launcher do dashboard criado: {launcher_script}")
        return True
    except Exception as e:
        print_error(f"Erro ao criar launcher: {e}")
        return False

def show_usage_instructions():
    """Mostra instruções de uso"""
    print_header("CONFIGURAÇÃO CONCLUÍDA!")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("\n1. 🚀 Para iniciar o monitoramento:")
    print("   python start_monitoring.py")
    
    print("\n2. 📱 Para abrir o dashboard:")
    print("   python launch_dashboard.py")
    print("   # ou diretamente:")
    print("   streamlit run dashboard.py")
    
    print("\n3. 🔗 Para integrar com seu código existente:")
    print("   # Adicione esta linha no início da sua aplicação:")
    print("   from llm_pdf_reading.monitoring.start_monitoring import start_monitoring")
    print("   start_monitoring()")
    
    print("\n4. 📊 Para usar decoradores (recomendado):")
    print("   from llm_pdf_reading.monitoring.decorators import monitor_llm_operation")
    print("   ")
    print("   @monitor_llm_operation(operation_name='minha_funcao')")
    print("   def minha_funcao():")
    print("       # seu código aqui")
    print("       return resultado")
    
    print("\n5. 📈 Para acessar MLflow UI:")
    print("   mlflow ui --backend-store-uri file://./monitoring_data/mlflow")
    print("   # Acesse: http://localhost:5000")
    
    print("\n📚 Para mais detalhes, consulte:")
    print("   - README_MONITORING.md")
    print("   - integration_examples.py")
    
    print("\n✨ SISTEMA PRONTO PARA USO!")

def main():
    """Função principal de configuração"""
    print_header("CONFIGURAÇÃO AUTOMÁTICA DO SISTEMA DE MONITORAMENTO")
    print("Este script irá configurar todo o sistema de monitoramento automaticamente")
    
    # Verificar Python
    if not check_python_version():
        return False
    
    # Instalar pacotes
    install_packages()
    
    # Configurar diretórios
    setup_directories()
    
    # Testar sistema
    if not test_monitoring_system():
        print_error("Falha nos testes - verifique a instalação")
        return False
    
    # Configurar MLflow
    setup_mlflow()
    
    # Criar scripts
    create_startup_script()
    create_dashboard_launcher()
    
    # Mostrar instruções
    show_usage_instructions()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("\n💥 FALHA NA CONFIGURAÇÃO")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Configuração cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERRO INESPERADO: {e}")
        sys.exit(1)
