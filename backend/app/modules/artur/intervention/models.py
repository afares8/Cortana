from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field
from app.models.base import TimestampModel

class InterventionType:
    MERGE_FUNCTIONS = "merge_functions"
    MERGE_RULES = "merge_rules"
    CREATE_WORKFLOW = "create_workflow"
    REMOVE_ENTITY = "remove_entity"
    UPDATE_AI_PROFILE = "update_ai_profile"
    REASSIGN_ROLE = "reassign_role"

class InterventionStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class ArturIntervention(TimestampModel):
    id: int = 0
    suggestion_id: int
    intervention_type: str
    department_id: Optional[int] = None
    state_before: Dict[str, Any] = {}
    state_after: Dict[str, Any] = {}
    status: str = InterventionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    user_id: Optional[int] = None  # If approved by a user
