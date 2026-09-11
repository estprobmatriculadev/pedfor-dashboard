import pytest
from src.services.dashboard_service import DashboardService
from src.data.quality_service import DataQualityEngine

def test_validacao_fluxo_indicadores_consolidados():
    """
    Task 05 - Validação de Consistência Matemática do Fluxo:
    XLS + JSON -> ETL -> Quality Audit -> Backend Service -> KPIs (2390 cursistas)
    """
    data = DashboardService.get_cursistas()
    assert len(data) == 2390

    kpis = DashboardService.get_kpis()
    assert kpis["total_inscritos"] == 2390
    assert kpis["total_matriculados"] + kpis["total_remanejados"] + kpis["total_desistentes"] == 2390

def test_ranking_formadores_consistencia():
    """Valida se o ranking por formador soma exatamente 2.390 cursistas."""
    formadores = DashboardService.get_cursistas_por_formador()
    assert len(formadores) > 0
    soma_cursistas = sum(f["total_cursistas"] for f in formadores)
    assert soma_cursistas == 2390
