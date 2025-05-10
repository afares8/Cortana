from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field
from app.models.base import TimestampModel

class InsightCategory:
    DEPARTMENT_CREATION = "department_creation"
    FUNCTION_USAGE = "function_usage"
    RULE_EXECUTION = "rule_execution"
    AI_CONSUMPTION = "ai_consumption"
    ORPHANED_ENTITY = "orphaned_entity"
    INACTIVE_ENTITY = "inactive_entity"
    OVERLAPPING_ENTITY = "overlapping_entity"

class EntityType:
    DEPARTMENT = "department"
    ROLE = "role"
    FUNCTION = "function"
    AUTOMATION_RULE = "automation_rule"
    USER = "user"
    AI_PROFILE = "ai_profile"
    
class ArturInsight(TimestampModel):
    id: int = 0
    category: str
    entity_type: str
    entity_id: Optional[int] = None
    department_id: Optional[int] = None
    metrics: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
