import pytest
from src.services.dashboard_service import DashboardService

def test_service_get_kpis_consolidado():
    """Valida se o DashboardService retorna os KPIs consolidados dos 2.390 cursistas."""
    kpis = DashboardService.get_kpis()
    assert isinstance(kpis, dict)
    assert kpis["total_inscritos"] == 2390
    assert kpis["total_matriculados"] == 2212
    assert kpis["total_remanejados"] == 141
    assert kpis["total_desistentes"] == 37
    assert kpis["frequencia_media_pct"] > 0

def test_service_filtros_nre_e_situacao():
    """Valida a filtragem por NRE e Situação."""
    filtrados = DashboardService.get_cursistas({"situacao": "Remanejado"})
    assert len(filtrados) == 141
    for r in filtrados:
        assert r["situacao"] == "Remanejado"

def test_service_update_frequencia():
    """Valida o serviço de atualização de frequência do cursista."""
    # Pega um CGM existente
    cursistas = DashboardService.get_cursistas()
    cgm = cursistas[0]["cgm"]
    res = DashboardService.update_frequencia(cgm, 95.0)
    assert res is True
    
    # Verifica se atualizou
    updated = DashboardService.get_cursistas({"search": cgm})
    assert updated[0]["frequencia_pct"] == 95.0
