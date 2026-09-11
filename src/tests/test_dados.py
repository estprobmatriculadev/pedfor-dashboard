import os
import pytest
from src.data.quality_service import DataQualityEngine
from src.services.dashboard_service import DashboardService

def test_migrations_existencia():
    """Valida a presença dos arquivos de DDL e Views em db/migrations/."""
    assert os.path.exists("db/migrations/001_initial_schema.sql")
    assert os.path.exists("db/migrations/002_create_views.sql")

def test_auditoria_matriculados_json_real():
    """Valida a auditoria de qualidade dos 2.288 registros reais de db/matriculados.json."""
    data = DashboardService._load_json_data()
    assert len(data) == 2288
    report = DataQualityEngine.audit_dataset(data)
    assert report["total_records"] == 2288
    assert report["duplicate_count"] == 0
    assert report["quality_score"] >= 95.0
