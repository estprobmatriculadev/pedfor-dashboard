import pytest
from src.services.dashboard_service import DashboardService
from src.data.quality_service import DataQualityEngine
from src.utils.config import Config

def test_validacao_fluxo_indicadores():
    """
    Task 05 - Validação do Fluxo dos Indicadores:
    Mapeamento de consistência:
    Fonte de dados -> Motor de Qualidade -> Serviço Backend -> Resposta de KPIs
    """
    # 1. Simulação de massa de dados brutos
    massa_bruta = [
        {"id": "rec-1", "unidade_id": "u1", "categoria_id": "c1", "data_registro": "2026-05-10", "status": "concluido", "valor": 500.00},
        {"id": "rec-2", "unidade_id": "u1", "categoria_id": "c1", "data_registro": "2026-05-12", "status": "concluido", "valor": 300.00},
        {"id": "rec-3", "unidade_id": "u2", "categoria_id": "c2", "data_registro": "2026-05-15", "status": "pendente", "valor": 200.00},
        {"id": "rec-4", "unidade_id": "u2", "categoria_id": "c2", "data_registro": "2026-05-18", "status": "em_andamento", "valor": 100.00}
    ]

    # 2. Auditoria pelo Motor de Qualidade
    auditoria = DataQualityEngine.audit_dataset(massa_bruta)
    assert auditoria["total_records"] == 4
    assert auditoria["quality_score"] == 100.0

    # 3. Consulta ao serviço de backend
    kpis = DashboardService.get_kpis()
    assert kpis["total_registros"] > 0
    assert kpis["taxa_conclusao_pct"] >= 0.0
    assert kpis["taxa_conclusao_pct"] <= 100.0

def test_resiliencia_e_regressao_api():
    """Valida se alteração de parâmetros e filtros mantém a consistência da API."""
    series = DashboardService.get_series(filters={"start_date": "2026-01-01"})
    assert isinstance(series, list)
    for s in series:
        assert s["total_pedidos"] >= s["concluidos"]

def test_tabela_ranking_consistencia():
    """Valida se os totais e percentuais na tabela de ranking por unidade são coerentes."""
    tabela = DashboardService.get_tabela()
    items = tabela["items"]
    for item in items:
        assert item["concluidos"] <= item["total_atendimentos"]
        assert item["taxa_eficiencia_pct"] >= 0.0 and item["taxa_eficiencia_pct"] <= 100.0
