from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ArturInterventionBase(BaseModel):
    suggestion_id: int
    intervention_type: str
    department_id: Optional[int] = None
    state_before: Dict[str, Any] = {}
    state_after: Dict[str, Any] = {}

class ArturInterventionCreate(ArturInterventionBase):
    status: str = "pending"
    user_id: Optional[int] = None

class ArturInterventionUpdate(BaseModel):
    status: str
    executed_at: Optional[datetime] = None

class ArturInterventionOut(ArturInterventionBase):
    id: int
    status: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

class ExecuteInterventionRequest(BaseModel):
    suggestion_id: int
    intervention_type: str

class InterventionLogOut(BaseModel):
    id: int
    intervention_type: str
    status: str
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    state_before: Dict[str, Any] = {}
    state_after: Dict[str, Any] = {}
    explanation: str
    context: Optional[str] = None
    confidence_score: float
    impact_level: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    user_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }
