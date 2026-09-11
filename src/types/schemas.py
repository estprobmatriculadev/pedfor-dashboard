from typing import TypedDict, Optional, List, Dict, Any

class CursistaRecord(TypedDict):
    id: str
    cgm: str
    cursista_nome: str
    cursista_email: str
    nre: str
    turma_id: str
    turma_nome: str
    turma_formador: str
    tutora: str
    turma_dia: str
    turma_horario: str
    periodo_turno: str
    situacao: str # 'Matriculado', 'Remanejado', 'Desistente'
    frequencia_pct: float
    status_email: str

class KPIMatriculasConsolidado(TypedDict):
    total_inscritos: int
    total_matriculados: int
    total_remanejados: int
    total_desistentes: int
    total_turmas: int
    total_formadores: int
    total_nres: int
    frequencia_media_pct: float
    status: str

class FilterParamsMatricula(TypedDict, total=False):
    turma_nome: Optional[str]
    formador: Optional[str]
    tutora: Optional[str]
    dia_semana: Optional[str]
    periodo_turno: Optional[str]
    situacao: Optional[str]
    nre: Optional[str]
    search: Optional[str]
