from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

from app.models.base import TimestampModel

class Task(TimestampModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    related_contract_id: Optional[int] = None
    related_client_id: Optional[int] = None
    status: str  # pending, in_progress, completed, cancelled
    priority: str  # low, medium, high, urgent
    ai_generated: bool = False
