import os
import json
import re
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_PATH = os.path.join(BASE_DIR, "db", "matriculados.json")
XLS_PATH = os.path.join(BASE_DIR, "db", "rel_matriculas_por_turma.xls")
OUTPUT_PATH = os.path.join(BASE_DIR, "db", "matriculas_consolidadas.json")

def run_etl():
    """Consolida os dados do arquivo SERE (.xls) e do matriculados.json."""
    json_data = []
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            json_data = json.load(f)

    def norm_name(name):
        if not name: return ""
        return re.sub(r"\s+", " ", str(name).strip().upper())

    json_by_name = {norm_name(r.get("cursista_nome")): r for r in json_data}

    df = pd.read_excel(XLS_PATH)
    current_turma_nome = ""
    current_turno = ""
    current_nre = "NRE CURITIBA"

    records = []

    for idx, row in df.iterrows():
        vals = [str(v).strip() for v in row.values if pd.notna(v)]
        if not vals:
            continue
        line = " ".join(vals)
        if "CURITIBA" in line or "NRE" in line:
            current_nre = vals[0] if vals[0] else "NRE CURITIBA"
        if "Curso:" in line and "Turma:" in line:
            for v in vals:
                if "Turma:" in v:
                    current_turma_nome = v.replace("Turma:", "").strip()
                if "Turno:" in v:
                    current_turno = v.replace("Turno:", "").strip()

        # Linha de aluno
        if vals[0].isdigit() and len(vals) >= 7:
            cgm = vals[1] if len(vals) > 1 else ""
            nome = vals[2] if len(vals) > 2 else ""
            norm_n = norm_name(nome)
            
            sit = "Matriculado"
            for v in vals:
                if v in ["Matriculado", "Remanejado", "Desistente"]:
                    sit = v
                    break

            json_match = json_by_name.get(norm_n, {})
            
            freq_padrao = 100.0 if sit == "Matriculado" else (60.0 if sit == "Remanejado" else 0.0)

            records.append({
                "id": json_match.get("id", f"cgm-{cgm}"),
                "cgm": cgm,
                "cursista_nome": nome,
                "cursista_email": json_match.get("cursista_email", f"{cgm.lower()}@escola.pr.gov.br"),
                "nre": current_nre if current_nre else "NRE CURITIBA",
                "turma_id": json_match.get("turma_id", f"turma-{current_turma_nome}"),
                "turma_nome": json_match.get("turma_nome", f"PEDFOR {current_turma_nome} {current_turno.upper()}"),
                "turma_formador": json_match.get("turma_formador", "DOROTEA BARBOSA KRUMMENAUER"),
                "tutora": json_match.get("turma_formador", "DOROTEA BARBOSA KRUMMENAUER"),
                "turma_dia": json_match.get("turma_dia", "QUARTA-FEIRA"),
                "turma_horario": json_match.get("turma_horario", "8h às 9h40"),
                "periodo_turno": current_turno if current_turno else "Manhã",
                "situacao": sit,
                "status_email": json_match.get("status_email", "enviado"),
                "data_confirmacao": json_match.get("data_confirmacao", "2026-07-10 16:53:20.153974+00"),
                "frequencia_pct": freq_padrao
            })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"ETL Concluído! {len(records)} registros gerados em {OUTPUT_PATH}")
    return records

if __name__ == "__main__":
    run_etl()
