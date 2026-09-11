import os
import json
from typing import Dict, Any, List, Optional

MEET_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "meet_attendance_data.json")

class GoogleMeetService:
    """Serviço de auditoria e controle de presença via Google Meet API."""

    @classmethod
    def load_meet_data(cls) -> List[Dict[str, Any]]:
        """Carrega relatórios salvos de presença em chamadas do Google Meet."""
        if os.path.exists(MEET_DATA_PATH):
            try:
                with open(MEET_DATA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    @classmethod
    def save_meet_data(cls, records: List[Dict[str, Any]]) -> bool:
        """Salva a lista de relatórios de chamadas do Meet."""
        try:
            with open(MEET_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def calculate_attendance_from_meet(cls, min_duration_minutes: int = 40) -> Dict[str, Dict[str, Any]]:
        """
        Calcula a presença dos cursistas com base no tempo de permanência na reunião do Meet:
        Returns: { "cursista_email@escola.pr.gov.br": { "reunioes_participadas": 4, "tempo_total_minutos": 240, "frequencia_sugerida_pct": 100.0 } }
        """
        raw_data = cls.load_meet_data()
        attendance_map: Dict[str, Dict[str, Any]] = {}

        for record in raw_data:
            email = str(record.get("cursista_email") or record.get("user_email") or "").strip().lower()
            if not email:
                continue

            duracao_min = float(record.get("duracao_minutos", 0))

            if email not in attendance_map:
                attendance_map[email] = {
                    "total_reunioes_turma": 0,
                    "reunioes_participadas": 0,
                    "tempo_total_minutos": 0.0,
                    "frequencia_sugerida_pct": 0.0
                }

            attendance_map[email]["total_reunioes_turma"] += 1
            attendance_map[email]["tempo_total_minutos"] += duracao_min

            if duracao_min >= min_duration_minutes:
                attendance_map[email]["reunioes_participadas"] += 1

        for email, val in attendance_map.items():
            tot = val["total_reunioes_turma"]
            val["frequencia_sugerida_pct"] = round((val["reunioes_participadas"] * 100.0) / tot, 2) if tot > 0 else 0.0

        return attendance_map

    @classmethod
    def fetch_meet_conferences(cls, credentials_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Exemplo de consulta à Google Meet REST API (v2 conferenceRecords).
        Busca participantes e tempo de permanência na chamada.
        """
        # Exemplo de estrutura de retorno da API
        return cls.load_meet_data()
