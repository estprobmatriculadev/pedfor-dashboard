from typing import List, Dict, Any
from datetime import datetime

class DataQualityEngine:
    """Motor de verificação e garantia de qualidade dos dados do PEDFOR Dashboard."""

    @staticmethod
    def audit_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Realiza auditoria completa em uma lista de registros de pedidos/atendimentos."""
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

        null_counts = {"unidade_id": 0, "categoria_id": 0, "data_registro": 0, "status": 0}
        invalid_dates = 0
        seen_keys = set()
        duplicates = 0

        for r in records:
            # 1. Checagem de nulos em campos obrigatórios
            for field in null_counts.keys():
                if not r.get(field):
                    null_counts[field] += 1

            # 2. Checagem de chave duplicada
            rec_id = r.get("id")
            if rec_id:
                if rec_id in seen_keys:
                    duplicates += 1
                else:
                    seen_keys.add(rec_id)

            # 3. Validação de data
            data_reg = r.get("data_registro")
            if data_reg:
                try:
                    if isinstance(data_reg, str):
                        dt = datetime.strptime(data_reg[:10], "%Y-%m-%d")
                    elif isinstance(data_reg, datetime):
                        dt = data_reg
                    else:
                        dt = None

                    if dt and dt > datetime.now():
                        invalid_dates += 1
                except Exception:
                    invalid_dates += 1

        # Cálculo do Score de Qualidade (0 - 100%)
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
