import pytest
from src.services.dashboard_service import DashboardService

def test_service_get_kpis_contrato():
    """Valida a estrutura da resposta de KPIs pelo DashboardService."""
    kpis = DashboardService.get_kpis()
    assert isinstance(kpis, dict)
    assert "total_registros" in kpis
    assert "total_concluidos" in kpis
    assert "valor_total" in kpis
    assert "taxa_conclusao_pct" in kpis
    assert kpis["total_registros"] >= 0

def test_service_get_series_contrato():
    """Valida a estrutura da resposta de séries temporais."""
    series = DashboardService.get_series()
    assert isinstance(series, list)
    assert len(series) > 0
    item = series[0]
    assert "mes_ano" in item
    assert "total_pedidos" in item
    assert "concluidos" in item

def test_service_get_tabela_contrato():
    """Valida a resposta da tabela de ranking por unidade."""
    res = DashboardService.get_tabela()
    assert isinstance(res, dict)
    assert "items" in res
    assert "total" in res
    assert isinstance(res["items"], list)
    assert res["total"] >= 0
