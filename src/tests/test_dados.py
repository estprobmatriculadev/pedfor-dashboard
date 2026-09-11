import os
import pytest
from src.data.quality_service import DataQualityEngine

def test_migrations_existencia():
    """Valida a presença dos arquivos de DDL e Views em db/migrations/."""
    assert os.path.exists("db/migrations/001_initial_schema.sql")
    assert os.path.exists("db/migrations/002_create_views.sql")

def test_auditoria_dados_perfeitos():
    """Valida score de qualidade 100% para um conjunto de dados sem falhas."""
    dataset = [
        {"id": "1", "unidade_id": "u1", "categoria_id": "c1", "data_registro": "2026-01-15", "status": "concluido"},
        {"id": "2", "unidade_id": "u2", "categoria_id": "c1", "data_registro": "2026-02-10", "status": "pendente"}
    ]
    report = DataQualityEngine.audit_dataset(dataset)
    assert report["total_records"] == 2
    assert report["quality_score"] == 100.0
    assert report["duplicate_count"] == 0

def test_auditoria_dados_com_inconsistencias():
    """Valida a detecção de duplicados e nulos pelo motor de qualidade."""
    dataset = [
        {"id": "1", "unidade_id": "u1", "categoria_id": "c1", "data_registro": "2026-01-15", "status": "concluido"},
        {"id": "1", "unidade_id": None, "categoria_id": "c1", "data_registro": "2099-12-31", "status": "pendente"} # id duplicado, nulo e data futura
    ]
    report = DataQualityEngine.audit_dataset(dataset)
    assert report["duplicate_count"] == 1
    assert report["null_counts"]["unidade_id"] == 1
    assert report["invalid_dates_count"] == 1
    assert report["quality_score"] < 100.0
