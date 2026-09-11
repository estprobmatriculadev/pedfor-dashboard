import os
import pytest
from src.utils.config import Config
from src.data.db import get_db_config

def test_diretorios_fundacao_existem():
    """Valida se a estrutura de diretórios exigida pela Task 01 foi criada."""
    diretorios = [
        "src/components",
        "src/pages",
        "src/services",
        "src/data",
        "src/hooks",
        "src/utils",
        "src/types",
        "src/tests"
    ]
    for d in diretorios:
        assert os.path.exists(d), f"Diretório {d} deve existir"

def test_db_config_estrutura():
    """Valida se a função get_db_config retorna os campos obrigatórios para o TiDB."""
    config = get_db_config()
    assert "host" in config
    assert "port" in config
    assert "user" in config
    assert "password" in config
    assert "database" in config
    assert "ssl" in config

def test_config_validation_funcao():
    """Valida o validador de variáveis de ambiente."""
    missing = Config.validate()
    # Retorna lista de variáveis faltantes caso não preenchidas no .env
    assert isinstance(missing, list)
