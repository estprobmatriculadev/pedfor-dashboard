import os
import json
from typing import Dict, Any, List, Optional

CLASSROOM_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "classroom_data.json")

class GoogleClassroomService:
    """Serviço de integração com o Google Classroom API e conversão de entregas de atividades."""

    @classmethod
    def load_classroom_data(cls) -> List[Dict[str, Any]]:
        """Carrega os dados de entregas do Classroom salvos localmente ou vindos do Apps Script."""
        if os.path.exists(CLASSROOM_DATA_PATH):
            try:
                with open(CLASSROOM_DATA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    @classmethod
    def save_classroom_data(cls, records: List[Dict[str, Any]]) -> bool:
        """Salva a lista de entregas enviadas pelo Apps Script ou via API."""
        try:
            with open(CLASSROOM_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def get_classroom_stats_by_email(cls) -> Dict[str, Dict[str, Any]]:
        """
        Retorna um dicionário indexado pelo e-mail do cursista com estatísticas de entregas:
        { "email@escola.pr.gov.br": { "entregues": 8, "pendentes": 1, "atrasadas": 0, "taxa_entrega_pct": 88.89 } }
        """
        raw = cls.load_classroom_data()
        stats: Dict[str, Dict[str, Any]] = {}

        for item in raw:
            email = item.get("cursista_email") or item.get("email")
            if not email:
                continue
            email = str(email).strip().lower()

            if email not in stats:
                stats[email] = {
                    "total_atividades": 0,
                    "entregues": 0,
                    "pendentes": 0,
                    "atrasadas": 0,
                    "taxa_entrega_pct": 0.0
                }

            stats[email]["total_atividades"] += 1
            st_sub = str(item.get("status", "TURNED_IN")).upper()
            if st_sub in ["TURNED_IN", "RETURNED", "ENTREGUE"]:
                stats[email]["entregues"] += 1
            elif st_sub in ["LATE", "ATRASADO"]:
                stats[email]["atrasadas"] += 1
            else:
                stats[email]["pendentes"] += 1

        for email, val in stats.items():
            tot = val["total_atividades"]
            val["taxa_entrega_pct"] = round((val["entregues"] * 100.0) / tot, 2) if tot > 0 else 0.0

        return stats

    @classmethod
    def sync_from_python_api(cls, client_secret_path: str = "credentials.json") -> bool:
        """
        Realiza autenticação OAuth2 e busca dados das turmas diretamente na API do Google Classroom em Python.
        """
        if not os.path.exists(client_secret_path):
            return False

        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            scopes = [
                'https://www.googleapis.com/auth/classroom.courses.readonly',
                'https://www.googleapis.com/auth/classroom.coursework.students.readonly'
            ]
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
            creds = flow.run_local_server(port=0)
            service = build('classroom', 'v1', credentials=creds)

            # Busca lista de turmas
            courses_result = service.courses().list(pageSize=50).execute()
            courses = courses_result.get('courses', [])

            submissions_all = []

            for c in courses:
                cid = c['id']
                course_name = c.get('name', '')
                # Busca tarefas da turma
                works_res = service.courses().courseWork().list(courseId=cid).execute()
                works = works_res.get('courseWork', [])

                for w in works:
                    wid = w['id']
                    wtitle = w.get('title', '')
                    subs_res = service.courses().courseWork().studentSubmissions().list(
                        courseId=cid, courseWorkId=wid
                    ).execute()
                    subs = subs_res.get('studentSubmissions', [])

                    for s in subs:
                        user_id = s.get('userId')
                        state = s.get('state')
                        submissions_all.append({
                            "course_id": cid,
                            "course_name": course_name,
                            "work_id": wid,
                            "work_title": wtitle,
                            "user_id": user_id,
                            "status": state
                        })

            return cls.save_classroom_data(submissions_all)
        except Exception:
            return False
