from typing import TypedDict, Optional, List, Any, Dict
from datetime import date

class KPICardData(TypedDict):
    id: str
    label: str
    value: Any
    unit: Optional[str]
    period: str
    change_percentage: Optional[float]
    trend: Optional[str] # 'up', 'down', 'stable'

class FilterParams(TypedDict, total=False):
    start_date: Optional[str]
    end_date: Optional[str]
    unidade_id: Optional[str]
    categoria: Optional[str]
    status: Optional[str]
    search: Optional[str]

class DataQualityReport(TypedDict):
    total_records: int
    null_counts: Dict[str, int]
    duplicate_count: int
    invalid_dates_count: int
    inconsistent_relationships_count: int
    quality_score: float
