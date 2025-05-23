from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr

from app.models.base import TimestampModel

class Client(TimestampModel):
    id: int
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    kyc_verified: bool = False
    notes: Optional[str] = None

class Contract(TimestampModel):
    id: int
    title: str
    client_id: int
    contract_type: str
    start_date: datetime
    expiration_date: Optional[datetime] = None
    responsible_lawyer: str
    description: Optional[str] = None
    status: str  # draft, active, expired, terminated
    file_path: str
    metadata: Dict[str, Any] = {}

class ContractVersion(TimestampModel):
    id: int
    contract_id: int
    version: int
    file_path: str
    changes_description: Optional[str] = None
    created_by: str

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

class AuditLog(TimestampModel):
    id: int
    entity_type: str  # client, contract, task, workflow
    entity_id: int
    action: str  # created, updated, deleted, status_changed, etc.
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    details: Dict[str, Any] = {}
    timestamp: datetime
