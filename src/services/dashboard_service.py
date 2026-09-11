import os
import json
from typing import Dict, Any, List, Optional
from src.data.db import execute_query

CONSOLIDADO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "matriculas_consolidadas.json")

class DashboardService:
    """Serviço Backend unificado para o Dashboard de Matrículas e Frequência do PEDFOR."""

    @classmethod
    def _load_data(cls) -> List[Dict[str, Any]]:
        """Carrega os dados consolidados do arquivo JSON."""
        if os.path.exists(CONSOLIDADO_PATH):
            with open(CONSOLIDADO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    @classmethod
    def _save_data(cls, data: List[Dict[str, Any]]) -> bool:
        """Salva as alterações (ex: atualização de frequência) no arquivo JSON."""
        try:
            with open(CONSOLIDADO_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def get_kpis(cls, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retorna os KPIs consolidados com base nos filtros aplicados."""
        data = cls.get_cursistas(filters)
        if not data:
            return {
                "total_inscritos": 0, "total_matriculados": 0, "total_remanejados": 0,
                "total_desistentes": 0, "total_turmas": 0, "total_formadores": 0,
                "total_nres": 0, "frequencia_media_pct": 0.0, "status": "empty"
            }

        total_inscritos = len(data)
        matriculados = sum(1 for r in data if r.get("situacao") == "Matriculado")
        remanejados = sum(1 for r in data if r.get("situacao") == "Remanejado")
        desistentes = sum(1 for r in data if r.get("situacao") == "Desistente")
        
        turmas = set(r.get("turma_nome") for r in data if r.get("turma_nome"))
        formadores = set(r.get("turma_formador") for r in data if r.get("turma_formador"))
        nres = set(r.get("nre") for r in data if r.get("nre"))

        freq_sum = sum(float(r.get("frequencia_pct", 100.0)) for r in data)
        freq_avg = round(freq_sum / total_inscritos, 2) if total_inscritos > 0 else 0.0

        return {
            "total_inscritos": total_inscritos,
            "total_matriculados": matriculados,
            "total_remanejados": remanejados,
            "total_desistentes": desistentes,
            "total_turmas": len(turmas),
            "total_formadores": len(formadores),
            "total_nres": len(nres),
            "frequencia_media_pct": freq_avg,
            "status": "success"
        }

    @classmethod
    def get_cursistas(cls, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retorna a lista filtrada de cursistas e suas informações."""
        data = cls._load_data()
        if not filters:
            return data

        filtered = []
        for r in data:
            if filters.get("turma_nome") and filters["turma_nome"] != "Todas" and filters["turma_nome"] not in r.get("turma_nome", ""):
                continue
            if filters.get("formador") and filters["formador"] != "Todos" and r.get("turma_formador") != filters["formador"]:
                continue
            if filters.get("tutora") and filters["tutora"] != "Todas" and r.get("tutora") != filters["tutora"]:
                continue
            if filters.get("dia_semana") and filters["dia_semana"] != "Todos" and r.get("turma_dia") != filters["dia_semana"]:
                continue
            if filters.get("periodo_turno") and filters["periodo_turno"] != "Todos" and filters["periodo_turno"].lower() not in r.get("periodo_turno", "").lower():
                continue
            if filters.get("situacao") and filters["situacao"] != "Todas" and r.get("situacao") != filters["situacao"]:
                continue
            if filters.get("nre") and filters["nre"] != "Todos" and r.get("nre") != filters["nre"]:
                continue
            if filters.get("search"):
                q = filters["search"].lower()
                matched = (
                    q in r.get("cursista_nome", "").lower() or
                    q in str(r.get("cgm", "")).lower() or
                    q in r.get("cursista_email", "").lower() or
                    q in r.get("turma_nome", "").lower() or
                    q in r.get("turma_formador", "").lower()
                )
                if not matched:
                    continue
            filtered.append(r)

        return filtered

    @classmethod
    def get_cursistas_por_formador(cls, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retorna o ranking de contagem de cursistas por Formador / Tutora."""
        data = cls.get_cursistas(filters)
        agrupado: Dict[str, Dict[str, Any]] = {}
        
        for r in data:
            f = r.get("turma_formador", "N/I")
            if f not in agrupado:
                agrupado[f] = {
                    "formador": f,
                    "total_cursistas": 0,
                    "matriculados": 0,
                    "remanejados": 0,
                    "desistentes": 0,
                    "turmas_set": set(),
                    "freq_total": 0.0
                }
            agrupado[f]["total_cursistas"] += 1
            sit = r.get("situacao", "Matriculado")
            if sit == "Matriculado": agrupado[f]["matriculados"] += 1
            elif sit == "Remanejado": agrupado[f]["remanejados"] += 1
            elif sit == "Desistente": agrupado[f]["desistentes"] += 1

            if r.get("turma_nome"):
                agrupado[f]["turmas_set"].add(r.get("turma_nome"))
            agrupado[f]["freq_total"] += float(r.get("frequencia_pct", 100.0))

        result = []
        for f, val in agrupado.items():
            cnt = val["total_cursistas"]
            result.append({
                "formador": f,
                "qtd_turmas": len(val["turmas_set"]),
                "total_cursistas": cnt,
                "matriculados": val["matriculados"],
                "remanejados": val["remanejados"],
                "desistentes": val["desistentes"],
                "frequencia_media_pct": round(val["freq_total"] / cnt, 2) if cnt > 0 else 0.0
            })

        result.sort(key=lambda x: x["total_cursistas"], reverse=True)
        return result

    @classmethod
    def update_frequencia(cls, cgm: str, nova_frequencia_pct: float) -> bool:
        """Atualiza a porcentagem de frequência de um cursista pelo seu CGM."""
        data = cls._load_data()
        updated = False
        for r in data:
            if str(r.get("cgm")) == str(cgm) or r.get("id") == str(cgm):
                r["frequencia_pct"] = max(0.0, min(100.0, float(nova_frequencia_pct)))
                updated = True

        if updated:
            return cls._save_data(data)
        return False
