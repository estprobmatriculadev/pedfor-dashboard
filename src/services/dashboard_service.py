from typing import Dict, Any, List, Optional
from src.data.db import execute_query
from src.data.quality_service import DataQualityEngine

class DashboardService:
    """Serviço de Backend responsável pela lógica de negócios e consolidação de dados para o Dashboard."""

    @staticmethod
    def get_kpis(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retorna os KPIs principais do dashboard (Cards de Metricas)."""
        try:
            sql = "SELECT * FROM vw_kpi_resumo;"
            rows = execute_query(sql)
            if rows and len(rows) > 0:
                row = rows[0]
                return {
                    "total_registros": int(row.get("total_registros") or 0),
                    "total_concluidos": int(row.get("total_concluidos") or 0),
                    "total_em_andamento": int(row.get("total_em_andamento") or 0),
                    "total_pendentes": int(row.get("total_pendentes") or 0),
                    "total_cancelados": int(row.get("total_cancelados") or 0),
                    "valor_total": float(row.get("valor_total") or 0.0),
                    "valor_medio": float(row.get("valor_medio") or 0.0),
                    "taxa_conclusao_pct": float(row.get("taxa_conclusao_pct") or 0.0),
                    "status": "success"
                }
        except Exception:
            pass

        # Fallback de dados para desenvolvimento / demonstração inicial
        return {
            "total_registros": 1248,
            "total_concluidos": 940,
            "total_em_andamento": 185,
            "total_pendentes": 98,
            "total_cancelados": 25,
            "valor_total": 354200.50,
            "valor_medio": 283.81,
            "taxa_conclusao_pct": 75.32,
            "status": "fallback"
        }

    @staticmethod
    def get_series(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retorna as séries temporais consolidadas para os gráficos de tendência."""
        try:
            sql = "SELECT * FROM vw_series_temporais ORDER BY mes_ano ASC;"
            rows = execute_query(sql)
            if rows and len(rows) > 0:
                return [
                    {
                        "mes_ano": r.get("mes_ano"),
                        "total_pedidos": int(r.get("total_pedidos") or 0),
                        "concluidos": int(r.get("concluidos") or 0),
                        "pendentes": int(r.get("pendentes") or 0),
                        "montante_financeiro": float(r.get("montante_financeiro") or 0.0)
                    }
                    for r in rows
                ]
        except Exception:
            pass

        # Fallback para desenvolvimento
        return [
            {"mes_ano": "2026-04", "total_pedidos": 180, "concluidos": 140, "pendentes": 40, "montante_financeiro": 48500.00},
            {"mes_ano": "2026-05", "total_pedidos": 210, "concluidos": 165, "pendentes": 45, "montante_financeiro": 59200.00},
            {"mes_ano": "2026-06", "total_pedidos": 245, "concluidos": 190, "pendentes": 55, "montante_financeiro": 71000.00},
            {"mes_ano": "2026-07", "total_pedidos": 290, "concluidos": 225, "pendentes": 65, "montante_financeiro": 84500.00},
            {"mes_ano": "2026-08", "total_pedidos": 323, "concluidos": 220, "pendentes": 103, "montante_financeiro": 91000.50}
        ]

    @staticmethod
    def get_tabela(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retorna a tabela paginada com o ranking e detalhamento de desempenho por unidade."""
        try:
            sql = "SELECT * FROM vw_ranking_unidades LIMIT 50;"
            rows = execute_query(sql)
            if rows and len(rows) > 0:
                items = [
                    {
                        "unidade_id": r.get("unidade_id"),
                        "unidade_nome": r.get("unidade_nome"),
                        "uf": r.get("uf"),
                        "total_atendimentos": int(r.get("total_atendimentos") or 0),
                        "concluidos": int(r.get("concluidos") or 0),
                        "valor_total": float(r.get("valor_total") or 0.0),
                        "taxa_eficiencia_pct": float(r.get("taxa_eficiencia_pct") or 0.0)
                    }
                    for r in rows
                ]
                return {"items": items, "total": len(items), "status": "success"}
        except Exception:
            pass

        # Fallback para desenvolvimento
        fallback_items = [
            {"unidade_id": "u-01", "unidade_nome": "Núcleo Curitiba Central", "uf": "PR", "total_atendimentos": 420, "concluidos": 350, "valor_total": 125000.00, "taxa_eficiencia_pct": 83.33},
            {"unidade_id": "u-02", "unidade_nome": "Regional Londrina", "uf": "PR", "total_atendimentos": 310, "concluidos": 240, "valor_total": 89000.00, "taxa_eficiencia_pct": 77.42},
            {"unidade_id": "u-03", "unidade_nome": "Regional Maringá", "uf": "PR", "total_atendimentos": 280, "concluidos": 210, "valor_total": 78000.00, "taxa_eficiencia_pct": 75.00},
            {"unidade_id": "u-04", "unidade_nome": "Regional Cascavel", "uf": "PR", "total_atendimentos": 150, "concluidos": 110, "valor_total": 42200.50, "taxa_eficiencia_pct": 73.33},
            {"unidade_id": "u-05", "unidade_nome": "Regional Ponta Grossa", "uf": "PR", "total_atendimentos": 88, "concluidos": 30, "valor_total": 20000.00, "taxa_eficiencia_pct": 34.09}
        ]
        return {"items": fallback_items, "total": len(fallback_items), "status": "fallback"}
