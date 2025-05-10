from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import Field
from app.models.base import TimestampModel

class SimulationStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SimulationResult:
    RECOMMENDED = "recommended"
    NEUTRAL = "neutral"
    NOT_RECOMMENDED = "not_recommended"

class ArturSimulation(TimestampModel):
    id: int = 0
    suggestion_id: int
    simulation_parameters: Dict[str, Any] = {}
    expected_outcomes: Dict[str, Any] = {}
    actual_outcomes: Dict[str, Any] = {}
    dependencies: List[Dict[str, Any]] = []
    status: str = SimulationStatus.PENDING
    result: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
