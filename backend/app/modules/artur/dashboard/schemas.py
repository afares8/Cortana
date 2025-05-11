from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class DepartmentHealthOut(BaseModel):
    department_id: int
    department_name: str
    health_score: int
    active_suggestions: int
    recent_interventions: int
    metrics: Dict[str, Any]

class HeatmapDataItem(BaseModel):
    department_id: int
    department_name: str
    ia_token_usage: int
    function_executions: int
    rule_triggers: int
    health_score: int
    hotspots: List[Dict[str, Any]]

class HeatmapDataOut(BaseModel):
    items: List[HeatmapDataItem]
    max_token_usage: int
    max_executions: int
    max_triggers: int

class PredictionItem(BaseModel):
    id: int
    department_id: int
    department_name: str
    prediction_type: str
    summary: str
    details: Dict[str, Any]
    confidence: float
    impact_score: int
    predicted_timestamp: str

class PredictionsOut(BaseModel):
    items: List[PredictionItem]
