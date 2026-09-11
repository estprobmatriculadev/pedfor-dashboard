import pytest
from src.services.dashboard_service import DashboardService

def test_service_get_kpis_matricula():
    """Valida se o DashboardService retorna os KPIs reais de matrícula (2.288 registros)."""
    kpis = DashboardService.get_kpis()
    assert isinstance(kpis, dict)
    assert "total_matriculas" in kpis
    assert "total_turmas" in kpis
    assert "total_formadores" in kpis
    assert "emails_enviados" in kpis
    assert kpis["total_matriculas"] == 2288
    assert kpis["total_turmas"] == 150
    assert kpis["total_formadores"] == 25

def test_service_get_series_matricula():
    """Valida a distribuição por dia da semana."""
    series = DashboardService.get_series()
    assert isinstance(series, list)
    assert len(series) > 0
    item = series[0]
    assert "dia_semana" in item
    assert "total_matriculas" in item

def test_service_get_tabela_turmas():
    """Valida a tabela de ocupação por turma."""
    res = DashboardService.get_tabela_turmas()
    assert isinstance(res, dict)
    assert "items" in res
    assert isinstance(res["items"], list)
    assert res["total"] == 150
