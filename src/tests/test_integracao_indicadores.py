import pytest
from src.services.dashboard_service import DashboardService
from src.data.quality_service import DataQualityEngine

def test_validacao_fluxo_indicadores_matricula():
    """
    Task 05 - Validação do Fluxo dos Indicadores de Matrícula:
    Fonte de dados (matriculados.json) -> Motor de Qualidade -> Serviço Backend -> Resposta de KPIs
    """
    data = DashboardService._load_json_data()
    assert len(data) == 2288

    auditoria = DataQualityEngine.audit_dataset(data)
    assert auditoria["quality_score"] >= 95.0

    kpis = DashboardService.get_kpis()
    assert kpis["total_matriculas"] == 2288
    assert kpis["total_turmas"] == 150
    assert kpis["total_formadores"] == 25
    assert kpis["emails_enviados"] + kpis["emails_pendentes"] == 2288

def test_tabela_turmas_consistencia():
    """Valida se a lista de turmas no backend soma o número correto de cursistas."""
    res = DashboardService.get_tabela_turmas()
    items = res["items"]
    soma_cursistas = sum(t["total_cursistas"] for t in items)
    assert soma_cursistas == 2288
