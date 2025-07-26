"""
Testes para validação de dados e estruturas
"""
import pytest
from pathlib import Path
import sys

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent.parent))

from llm_pdf_reading.orchestrator import PDFReadingOrchestrator

def test_orchestrator_initialization():
    """Testa se o orquestrador é inicializado corretamente"""
    orchestrator = PDFReadingOrchestrator()
    assert orchestrator is not None
    assert orchestrator.pdf_processor is not None

def test_project_structure():
    """Testa se a estrutura do projeto está correta"""
    project_root = Path(__file__).parent.parent
    
    # Verificar diretórios essenciais
    assert (project_root / "llm_pdf_reading").exists()
    assert (project_root / "data").exists()
    assert (project_root / "models").exists()
    assert (project_root / "tests").exists()
    
    # Verificar arquivos essenciais
    assert (project_root / "requirements.txt").exists()
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / ".env").exists()

def test_config_imports():
    """Testa se as configurações podem ser importadas"""
    try:
        from llm_pdf_reading import config
        assert hasattr(config, 'PROJECT_ROOT')
        assert hasattr(config, 'PDF_CONFIG')
    except ImportError:
        pytest.fail("Não foi possível importar configurações")

def test_main_module_imports():
    """Testa se o módulo principal pode ser importado"""
    try:
        import llm_pdf_reading
        assert hasattr(llm_pdf_reading, 'PDFProcessor')
        assert hasattr(llm_pdf_reading, 'PDFReadingOrchestrator')
    except ImportError:
        pytest.fail("Não foi possível importar módulo principal")
