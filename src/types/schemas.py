from typing import TypedDict, Optional, List, Dict, Any

class MatriculaRecord(TypedDict):
    id: str
    cursista_id: str
    cursista_nome: str
    cursista_email: str
    turma_id: str
    turma_nome: str
    turma_formador: str
    turma_dia: str
    turma_horario: str
    vaga_id: str
    data_confirmacao: str
    status_email: str

class KPIMatriculas(TypedDict):
    total_matriculas: int
    total_cursistas_unicos: int
    total_turmas: int
    total_formadores: int
    emails_enviados: int
    emails_pendentes: int
    taxa_envio_email_pct: float
    status: str

class TurmaResumo(TypedDict):
    turma_id: str
    turma_nome: str
    turma_formador: str
    turma_dia: str
    turma_horario: str
    total_cursistas: int
    emails_enviados: int
    taxa_confirmacao_pct: float

class FilterMatriculaParams(TypedDict, total=False):
    turma_id: Optional[str]
    formador: Optional[str]
    dia_semana: Optional[str]
    horario: Optional[str]
    status_email: Optional[str]
    search: Optional[str]
