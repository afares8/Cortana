from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import Field
from app.models.base import TimestampModel

class SuggestionSource:
    FUNCTION_USAGE = "function_usage"
    RULE_OVERLAP = "rule_overlap"
    AI_USAGE = "ai_usage"
    DEPARTMENT_ACTIVITY = "department_activity"
    ROLE_ASSIGNMENT = "role_assignment"

class SuggestionStatus:
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    IGNORED = "ignored"
    SIMULATED = "simulated"

class ArturSuggestion(TimestampModel):
    id: int = 0
    department_id: Optional[int] = None
    issue_summary: str
    suggested_action: Dict[str, Any] = {}
    confidence_score: float
    source: str
    status: str = SuggestionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
