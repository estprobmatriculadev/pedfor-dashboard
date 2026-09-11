import os
import pytest
from src.data.quality_service import DataQualityEngine
from src.services.dashboard_service import DashboardService

def test_etl_e_dados_consolidados_existem():
    """Valida a existência do dataset gerado pelo ETL (matriculas_consolidadas.json)."""
    assert os.path.exists("db/matriculas_consolidadas.json")
    data = DashboardService._load_data()
    assert len(data) == 2390

def test_auditoria_qualidade_consolidadas():
    """Valida o score de qualidade dos 2.390 registros unificados."""
    data = DashboardService._load_data()
    report = DataQualityEngine.audit_dataset(data)
    assert report["total_records"] == 2390
    assert report["invalid_situacao_count"] == 0
    assert report["quality_score"] >= 95.0
