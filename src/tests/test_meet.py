import pytest
from src.services.meet_service import GoogleMeetService

def test_meet_attendance_calculation():
    """Valida o cálculo do tempo de presença do cursista no Google Meet."""
    sample_records = [
        {"cursista_email": "aluno1@escola.pr.gov.br", "duracao_minutos": 60},
        {"cursista_email": "aluno1@escola.pr.gov.br", "duracao_minutos": 50},
        {"cursista_email": "aluno2@escola.pr.gov.br", "duracao_minutos": 10} # < 40 min = falta
    ]
    GoogleMeetService.save_meet_data(sample_records)

    map_result = GoogleMeetService.calculate_attendance_from_meet(min_duration_minutes=40)
    assert "aluno1@escola.pr.gov.br" in map_result
    assert map_result["aluno1@escola.pr.gov.br"]["reunioes_participadas"] == 2
    assert map_result["aluno1@escola.pr.gov.br"]["frequencia_sugerida_pct"] == 100.0

    assert "aluno2@escola.pr.gov.br" in map_result
    assert map_result["aluno2@escola.pr.gov.br"]["reunioes_participadas"] == 0
    assert map_result["aluno2@escola.pr.gov.br"]["frequencia_sugerida_pct"] == 0.0
