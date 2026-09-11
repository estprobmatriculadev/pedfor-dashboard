from typing import List, Dict, Any

class DataQualityEngine:
    """Motor de auditoria de qualidade dos dados consolidados do PEDFOR."""

    @staticmethod
    def audit_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(records)
        if total == 0:
            return {
                "total_records": 0,
                "null_counts": {},
                "duplicate_count": 0,
                "invalid_situacao_count": 0,
                "quality_score": 100.0,
                "status": "vazio"
            }

        null_counts = {
            "cgm": 0,
            "cursista_nome": 0,
            "turma_nome": 0,
            "turma_formador": 0,
            "situacao": 0,
            "nre": 0
        }
        invalid_situacao = 0
        seen_keys = set()
        duplicates = 0

        for r in records:
            # 1. Checagem de nulos
            for field in null_counts.keys():
                if not r.get(field):
                    null_counts[field] += 1

            # 2. Checagem de duplicatas por CGM
            cgm = r.get("cgm")
            if cgm:
                if cgm in seen_keys:
                    duplicates += 1
                else:
                    seen_keys.add(cgm)

            # 3. Validação de situação permitida
            sit = r.get("situacao")
            if sit not in ["Matriculado", "Remanejado", "Desistente"]:
                invalid_situacao += 1

        total_nulls = sum(null_counts.values())
        errors_total = total_nulls + duplicates + invalid_situacao
        quality_score = max(0.0, round(100.0 - (errors_total * 100.0 / (total * 6)), 2))

        return {
            "total_records": total,
            "null_counts": null_counts,
            "duplicate_count": duplicates,
            "invalid_situacao_count": invalid_situacao,
            "quality_score": quality_score,
            "status": "excelente" if quality_score >= 95 else ("aceitavel" if quality_score >= 80 else "critico")
        }
