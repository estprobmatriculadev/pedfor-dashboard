import os
import glob
import json
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLASSROOM_DATA_PATH = os.path.join(BASE_DIR, "db", "classroom_data.json")

class GoogleClassroomService:
    """Serviço de integração direta com o Google Classroom API."""

    @classmethod
    def find_client_secret_file(cls) -> Optional[str]:
        """Localiza automaticamente o arquivo de credenciais do Google Cloud na raiz."""
        patterns = [
            os.path.join(BASE_DIR, "client_secret*.json"),
            os.path.join(BASE_DIR, "credentials.json")
        ]
        for p in patterns:
            files = glob.glob(p)
            if files:
                return files[0]
        return None

    @classmethod
    def load_classroom_data(cls) -> List[Dict[str, Any]]:
        """Carrega dados salvos do Classroom."""
        if os.path.exists(CLASSROOM_DATA_PATH):
            try:
                with open(CLASSROOM_DATA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    @classmethod
    def save_classroom_data(cls, records: List[Dict[str, Any]]) -> bool:
        """Salva os registros obtidos do Classroom."""
        try:
            with open(CLASSROOM_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def get_classroom_stats_by_email(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna mapa de estatísticas de entregas do Classroom indexadas pelo e-mail do cursista."""
        raw = cls.load_classroom_data()
        stats: Dict[str, Dict[str, Any]] = {}

        for item in raw:
            email = item.get("cursista_email") or item.get("email") or item.get("user_email")
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
    def sync_from_google_api(cls, port: int = 8501) -> Dict[str, Any]:
        """
        Realiza a autenticação e sincronização oficial via Google Classroom API.
        Ajusta a redirect_uri para bater exatamente com a URI configurada no Google Cloud.
        """
        secret_file = cls.find_client_secret_file()
        if not secret_file:
            return {
                "success": False,
                "message": "Nenhum arquivo client_secret*.json encontrado na raiz.",
                "total_synced": 0
            }

        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            scopes = [
                'https://www.googleapis.com/auth/classroom.courses.readonly',
                'https://www.googleapis.com/auth/classroom.coursework.students.readonly',
                'https://www.googleapis.com/auth/classroom.rosters.readonly'
            ]

            flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes)

            # Tenta utilizar o redirect_uri cadastrado no JSON (ex: http://localhost:8501/)
            with open(secret_file, "r", encoding="utf-8") as f:
                c_data = json.load(f)

            key_type = 'web' if 'web' in c_data else ('installed' if 'installed' in c_data else None)
            registered_uris = c_data.get(key_type, {}).get('redirect_uris', []) if key_type else []

            target_port = port
            if registered_uris:
                # Extrai a porta da primeira URI cadastrada
                uri = registered_uris[0]
                flow.redirect_uri = uri
                if ":" in uri:
                    port_str = uri.split(":")[-1].replace("/", "")
                    if port_str.isdigit():
                        target_port = int(port_str)

            # Executa o servidor local de autenticação na porta especificada
            creds = flow.run_local_server(port=target_port, prompt='consent')
            service = build('classroom', 'v1', credentials=creds)

            # Buscar Turmas do Classroom
            courses_result = service.courses().list(pageSize=100).execute()
            courses = courses_result.get('courses', [])

            records = []

            for c in courses:
                cid = c['id']
                course_name = c.get('name', '')
                
                students_map = {}
                try:
                    stud_res = service.courses().students().list(courseId=cid).execute()
                    for st in stud_res.get('students', []):
                        profile = st.get('profile', {})
                        students_map[st.get('userId')] = profile.get('emailAddress', '')
                except Exception:
                    pass

                works_res = service.courses().courseWork().list(courseId=cid).execute()
                works = works_res.get('courseWork', [])

                for w in works:
                    wid = w['id']
                    wtitle = w.get('title', '')
                    
                    subs_res = service.courses().courseWork().studentSubmissions().list(
                        courseId=cid, courseWorkId=wid
                    ).execute()
                    for sub in subs_res.get('studentSubmissions', []):
                        uid = sub.get('userId')
                        email = students_map.get(uid, '')
                        records.append({
                            "course_id": cid,
                            "course_name": course_name,
                            "work_id": wid,
                            "work_title": wtitle,
                            "user_id": uid,
                            "cursista_email": email,
                            "status": sub.get('state', 'NEW'),
                            "assigned_grade": sub.get('assignedGrade')
                        })

            cls.save_classroom_data(records)
            return {
                "success": True,
                "message": f"Sincronização concluída com sucesso! {len(records)} entregas registradas.",
                "total_synced": len(records)
            }
        except Exception as e:
            err_msg = str(e)
            if "redirect_uri_mismatch" in err_msg or "400" in err_msg:
                return {
                    "success": False,
                    "message": "Erro de Redirecionamento (redirect_uri_mismatch): Adicione 'http://localhost:8080/' ou crie uma credencial do tipo 'Desktop App' no Google Cloud Console.",
                    "total_synced": 0
                }
            return {
                "success": False,
                "message": f"Erro na conexão Google: {err_msg}",
                "total_synced": 0
            }

if __name__ == "__main__":
    res = GoogleClassroomService.sync_from_google_api()
    print(res)
