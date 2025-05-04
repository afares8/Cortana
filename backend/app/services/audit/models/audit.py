from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

from app.models.base import TimestampModel

class AuditLog(TimestampModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str  # create, update, delete, view, approve, reject
    entity_type: str  # contract, client, workflow, task
    entity_id: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
