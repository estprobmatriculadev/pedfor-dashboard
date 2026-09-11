import pytest
from src.services.classroom_service import GoogleClassroomService

def test_classroom_service_mock_sync():
    """Valida o cálculo de estatísticas de entregas do Classroom."""
    sample_data = [
        {"cursista_email": "prof1@escola.pr.gov.br", "status": "TURNED_IN"},
        {"cursista_email": "prof1@escola.pr.gov.br", "status": "TURNED_IN"},
        {"cursista_email": "prof1@escola.pr.gov.br", "status": "LATE"},
        {"cursista_email": "prof2@escola.pr.gov.br", "status": "NEW"}
    ]
    GoogleClassroomService.save_classroom_data(sample_data)

    stats = GoogleClassroomService.get_classroom_stats_by_email()
    assert "prof1@escola.pr.gov.br" in stats
    assert stats["prof1@escola.pr.gov.br"]["total_atividades"] == 3
    assert stats["prof1@escola.pr.gov.br"]["entregues"] == 2
    assert stats["prof1@escola.pr.gov.br"]["atrasadas"] == 1
    assert stats["prof1@escola.pr.gov.br"]["taxa_entrega_pct"] == 66.67
