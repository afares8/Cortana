from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field
from app.models.base import TimestampModel

class ActionType:
    FUNCTION_EXECUTION = "function_execution"
    AUTOMATION_TRIGGER = "automation_trigger"
    AI_PROMPT = "ai_prompt"
    AI_RESPONSE = "ai_response"
    DEPARTMENT_CHANGE = "department_change"
    ROLE_CHANGE = "role_change"
    TEMPLATE_CHANGE = "template_change"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"

class TargetType:
    DEPARTMENT = "department"
    ROLE = "role"
    FUNCTION = "function"
    AUTOMATION_RULE = "automation_rule"
    AI_PROFILE = "ai_profile"
    TEMPLATE = "template"
    USER = "user"
    SYSTEM = "system"

class AuditLog(TimestampModel):
    id: int = 0
    user_id: Optional[int] = None
    action_type: str
    target_type: str
    target_id: Optional[int] = None
    payload: Dict[str, Any] = {}
    success: bool = True
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
