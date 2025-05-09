from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class AuditLogBase(BaseModel):
    user_id: Optional[int] = None
    action_type: str
    target_type: str
    target_id: Optional[int] = None
    payload: Dict[str, Any] = {}
    success: bool = True
    error_message: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogOut(AuditLogBase):
    id: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class AuditLogFilter(BaseModel):
    user_id: Optional[int] = None
    action_type: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    success: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AuditSummary(BaseModel):
    total_logs: int
    success_count: int
    error_count: int
    action_type_counts: Dict[str, int]
    target_type_counts: Dict[str, int]
    recent_errors: List[AuditLogOut] = []
