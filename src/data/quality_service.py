from typing import List, Dict, Any
from datetime import datetime

class DataQualityEngine:
    """Motor de auditoria de qualidade de dados para matrículas PEDFOR."""

    @staticmethod
    def audit_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Realiza auditoria completa na lista de registros de matrículas."""
        total = len(records)
        if total == 0:
            return {
                "total_records": 0,
                "null_counts": {},
                "duplicate_count": 0,
                "invalid_dates_count": 0,
                "quality_score": 100.0,
                "status": "vazio"
            }

        null_counts = {
            "cursista_email": 0,
            "turma_id": 0,
            "vaga_id": 0,
            "status_email": 0
        }
        invalid_dates = 0
        seen_keys = set()
        duplicates = 0

        for r in records:
            # 1. Checagem de nulos
            for field in null_counts.keys():
                if not r.get(field):
                    null_counts[field] += 1

            # 2. Checagem de chaves duplicadas
            rec_id = r.get("id")
            if rec_id:
                if rec_id in seen_keys:
                    duplicates += 1
                else:
                    seen_keys.add(rec_id)

            # 3. Validação de data de confirmação
            data_conf = r.get("data_confirmacao")
            if data_conf:
                try:
                    # Exemplo: 2026-07-10 16:53:20.153974+00
                    dt_str = str(data_conf)[:19]
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    if dt > datetime.now():
                        invalid_dates += 1
                except Exception:
                    invalid_dates += 1

        total_nulls = sum(null_counts.values())
        errors_total = total_nulls + duplicates + invalid_dates
        quality_score = max(0.0, round(100.0 - (errors_total * 100.0 / (total * 4)), 2))

        return {
            "total_records": total,
            "null_counts": null_counts,
            "duplicate_count": duplicates,
            "invalid_dates_count": invalid_dates,
            "quality_score": quality_score,
            "status": "excelente" if quality_score >= 95 else ("aceitavel" if quality_score >= 80 else "critico")
        }
