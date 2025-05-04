from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.models.base import TimestampModel

class WorkflowTemplate(TimestampModel):
    id: str
    name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]  # Serialized ApprovalStep objects

class WorkflowInstance(TimestampModel):
    id: int
    template_id: str
    contract_id: int
    current_step_id: str
    status: str  # pending, approved, rejected
    steps: List[Dict[str, Any]]  # Serialized ApprovalStep objects with approval status
