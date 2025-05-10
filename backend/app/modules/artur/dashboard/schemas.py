from typing import Dict, Any, Optional
from pydantic import BaseModel

class DepartmentHealthOut(BaseModel):
    department_id: int
    department_name: str
    health_score: int
    active_suggestions: int
    recent_interventions: int
    metrics: Dict[str, Any]
