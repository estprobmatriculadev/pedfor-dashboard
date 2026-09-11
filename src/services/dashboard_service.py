import os
import json
from typing import Dict, Any, List, Optional
from src.data.db import execute_query

MATRICULADOS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "matriculados.json")

class DashboardService:
    """Serviço de Backend para o Dashboard de Matrículas PEDFOR."""

    @classmethod
    def _load_json_data(cls) -> List[Dict[str, Any]]:
        """Carrega a massa real de registros do arquivo db/matriculados.json."""
        if os.path.exists(MATRICULADOS_JSON_PATH):
            with open(MATRICULADOS_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    @classmethod
    def get_kpis(cls, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retorna os KPIs principais do dashboard de matrículas."""
        try:
            sql = "SELECT * FROM vw_kpi_matriculas;"
            rows = execute_query(sql)
            if rows and len(rows) > 0:
                row = rows[0]
                return {
                    "total_matriculas": int(row.get("total_matriculas") or 0),
                    "total_cursistas_unicos": int(row.get("total_cursistas_unicos") or 0),
                    "total_turmas": int(row.get("total_turmas") or 0),
                    "total_formadores": int(row.get("total_formadores") or 0),
                    "emails_enviados": int(row.get("emails_enviados") or 0),
                    "emails_pendentes": int(row.get("emails_pendentes") or 0),
                    "taxa_envio_email_pct": float(row.get("taxa_envio_email_pct") or 0.0),
                    "status": "success"
                }
        except Exception:
            pass

        # Cálculo real baseado no arquivo db/matriculados.json
        data = cls._load_json_data()
        if not data:
            return {
                "total_matriculas": 0, "total_cursistas_unicos": 0, "total_turmas": 0,
                "total_formadores": 0, "emails_enviados": 0, "emails_pendentes": 0,
                "taxa_envio_email_pct": 0.0, "status": "empty"
            }

        total_matriculas = len(data)
        cursistas = set(r.get("cursista_email") for r in data if r.get("cursista_email"))
        turmas = set(r.get("turma_id") for r in data if r.get("turma_id"))
        formadores = set(r.get("turma_formador") for r in data if r.get("turma_formador"))
        enviados = sum(1 for r in data if r.get("status_email") == "enviado")
        pendentes = total_matriculas - enviados
        taxa = round((enviados * 100.0) / total_matriculas, 2) if total_matriculas > 0 else 0.0

        return {
            "total_matriculas": total_matriculas,
            "total_cursistas_unicos": len(cursistas),
            "total_turmas": len(turmas),
            "total_formadores": len(formadores),
            "emails_enviados": enviados,
            "emails_pendentes": pendentes,
            "taxa_envio_email_pct": taxa,
            "status": "json_real"
        }

    @classmethod
    def get_series(cls, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retorna a distribuição de matrículas por Dia da Semana e Horário."""
        try:
            sql = "SELECT * FROM vw_distribuicao_dia_horario;"
            rows = execute_query(sql)
            if rows and len(rows) > 0:
                return [
                    {
                        "dia_semana": r.get("dia_semana"),
                        "horario": r.get("horario"),
                        "total_matriculas": int(r.get("total_matriculas") or 0)
                    }
                    for r in rows
                ]
        except Exception:
            pass

        # Consolidação via db/matriculados.json
        data = cls._load_json_data()
        agrupado: Dict[str, int] = {}
        for r in data:
            dia = r.get("turma_dia", "N/I")
            if dia:
                agrupado[dia] = agrupado.get(dia, 0) + 1

        ordem_dias = ["SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA"]
        return [
            {"dia_semana": dia, "total_matriculas": agrupado.get(dia, 0)}
            for dia in ordem_dias if dia in agrupado
        ]

    @classmethod
    def get_tabela_turmas(cls, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retorna a tabela de Turmas com ocupação e formador responsável."""
        try:
            sql = "SELECT * FROM vw_matriculas_por_turma LIMIT 100;"
            rows = execute_query(sql)
            if rows and len(rows) > 0:
                items = [
                    {
                        "turma_id": r.get("turma_id"),
                        "turma_nome": r.get("turma_nome"),
                        "turma_formador": r.get("turma_formador"),
                        "turma_dia": r.get("turma_dia"),
                        "turma_horario": r.get("turma_horario"),
                        "total_cursistas": int(r.get("total_cursistas") or 0),
                        "emails_enviados": int(r.get("emails_enviados") or 0),
                        "taxa_confirmacao_pct": float(r.get("taxa_confirmacao_pct") or 0.0)
                    }
                    for r in rows
                ]
                return {"items": items, "total": len(items), "status": "success"}
        except Exception:
            pass

        # Consolidação via db/matriculados.json
        data = cls._load_json_data()
        turmas_dict: Dict[str, Dict[str, Any]] = {}
        for r in data:
            tid = r.get("turma_id", "")
            if not tid:
                continue
            if tid not in turmas_dict:
                turmas_dict[tid] = {
                    "turma_id": tid,
                    "turma_nome": r.get("turma_nome", ""),
                    "turma_formador": r.get("turma_formador", ""),
                    "turma_dia": r.get("turma_dia", ""),
                    "turma_horario": r.get("turma_horario", ""),
                    "total_cursistas": 0,
                    "emails_enviados": 0
                }
            turmas_dict[tid]["total_cursistas"] += 1
            if r.get("status_email") == "enviado":
                turmas_dict[tid]["emails_enviados"] += 1

        items = list(turmas_dict.values())
        for t in items:
            t["taxa_confirmacao_pct"] = round((t["emails_enviados"] * 100.0) / t["total_cursistas"], 2) if t["total_cursistas"] > 0 else 0.0

        items.sort(key=lambda x: x["total_cursistas"], reverse=True)
        return {"items": items, "total": len(items), "status": "json_real"}
