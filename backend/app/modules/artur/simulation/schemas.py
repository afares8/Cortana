from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class ArturSimulationBase(BaseModel):
    suggestion_id: int
    simulation_parameters: Dict[str, Any] = {}
    expected_outcomes: Dict[str, Any] = {}
    dependencies: List[Dict[str, Any]] = []

class ArturSimulationCreate(ArturSimulationBase):
    status: str = "pending"

class ArturSimulationUpdate(BaseModel):
    status: str
    result: Optional[str] = None
    actual_outcomes: Dict[str, Any] = {}
    completed_at: Optional[datetime] = None

class ArturSimulationOut(ArturSimulationBase):
    id: int
    status: str
    result: Optional[str] = None
    actual_outcomes: Dict[str, Any] = {}
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RunSimulationRequest(BaseModel):
    suggestion_id: int
    simulation_type: str

class SimulationResultOut(BaseModel):
    success: bool
    result: str
    details: Dict[str, Any] = {}
    impact_assessment: Dict[str, Any] = {}
    dependencies_affected: List[Dict[str, Any]] = []
    recommendation: str
    
    model_config = {
        "from_attributes": True
    }
