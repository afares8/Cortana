from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr

class AuditLogBase(BaseModel):
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str  # create, update, delete, view, approve, reject
    entity_type: str  # contract, client, workflow, task
    entity_id: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogInDBBase(AuditLogBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AuditLog(AuditLogInDBBase):
    pass
