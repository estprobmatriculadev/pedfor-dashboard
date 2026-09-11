import os
import pytest

def test_frontend_arquivos_existem():
    """Valida se a estrutura visual do frontend foi criada."""
    assert os.path.exists("src/pages/index.html")
    assert os.path.exists("src/components/theme.css")
    assert os.path.exists("src/app.py")

def test_html_semantico_e_acessibilidade():
    """Valida presenca de elementos HTML5 semanticos e atributos de acessibilidade."""
    with open("src/pages/index.html", "r", encoding="utf-8") as f:
      content = f.read()
    assert "<header" in content
    assert "<main" in content
    assert "<section" in content
    assert "<article" in content
    assert "<table" in content
    assert "aria-label" in content

def test_css_design_system_tokens():
    """Valida tokens do design system no CSS."""
    with open("src/components/theme.css", "r", encoding="utf-8") as f:
      content = f.read()
    assert "--bg-dark:" in content
    assert "--accent-primary:" in content
    assert ".glass-card" in content
    assert ".kpi-grid" in content
    assert ".modern-table" in content
