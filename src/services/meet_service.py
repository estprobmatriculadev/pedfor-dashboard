import os
import json
import io
import pandas as pd
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEET_DATA_PATH = os.path.join(BASE_DIR, "db", "meet_attendance_data.json")
CONSOLIDADO_PATH = os.path.join(BASE_DIR, "db", "matriculas_consolidadas.json")

class GoogleMeetService:
    """Serviço de auditoria e controle de presença via Google Meet API e relatórios de chamada."""

    @classmethod
    def load_meet_data(cls) -> List[Dict[str, Any]]:
        """Carrega relatórios salvos de presença em chamadas do Google Meet. Se não existir, gera a base inicial."""
        if os.path.exists(MEET_DATA_PATH):
            try:
                with open(MEET_DATA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return cls.seed_default_meet_data()

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
    def seed_default_meet_data(cls) -> List[Dict[str, Any]]:
        """Gera registros iniciais de presença do Google Meet baseados nos cursistas do PEDFOR."""
        records = []
        if os.path.exists(CONSOLIDADO_PATH):
            try:
                with open(CONSOLIDADO_PATH, "r", encoding="utf-8") as f:
                    cursistas = json.load(f)
                
                for c in cursistas:
                    email = c.get("cursista_email")
                    sit = c.get("situacao", "Matriculado")
                    if email:
                        duracao = 60.0 if sit in ["Matriculado", "Remanejado"] else 0.0
                        records.append({
                            "cursista_email": email,
                            "turma_nome": c.get("turma_nome", ""),
                            "formador": c.get("turma_formador", ""),
                            "data_reuniao": "2026-08-12",
                            "duracao_minutos": duracao,
                            "status_presenca": "presente" if duracao >= 40 else "ausente"
                        })
                cls.save_meet_data(records)
            except Exception:
                pass
        return records

    @classmethod
    def parse_meet_csv(cls, file_content: str) -> List[Dict[str, Any]]:
        """Processa arquivo CSV exportado do Google Meet ou Admin SDK Reports."""
        try:
            df = pd.read_csv(io.StringIO(file_content))
            records = []
            for _, row in df.iterrows():
                email = row.get("E-mail") or row.get("Email") or row.get("cursista_email")
                duracao = row.get("Duração (minutos)") or row.get("Duracao") or row.get("duracao_minutos", 60)
                if email:
                    records.append({
                        "cursista_email": str(email).strip().lower(),
                        "duracao_minutos": float(duracao),
                        "status_presenca": "presente" if float(duracao) >= 40 else "ausente"
                    })
            if records:
                cls.save_meet_data(records)
            return records
        except Exception:
            return []

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
