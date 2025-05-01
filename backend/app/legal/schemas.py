from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class ClientBase(BaseModel):
    name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    kyc_verified: bool = False
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None

class ClientInDB(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Client(ClientInDB):
    pass

class ContractBase(BaseModel):
    title: str
    client_id: int
    contract_type: str = Field(..., description="Type of contract (NDA, Service Agreement, etc.)")
    start_date: datetime
    expiration_date: Optional[datetime] = None
    responsible_lawyer: str
    description: Optional[str] = None
    status: str = "draft"  # draft, active, expired, terminated
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ContractCreate(ContractBase):
    file_content: Optional[str] = None  # Base64 encoded file content

class ContractUpdate(BaseModel):
    title: Optional[str] = None
    client_id: Optional[int] = None
    contract_type: Optional[str] = None
    start_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    responsible_lawyer: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    file_content: Optional[str] = None  # Base64 encoded file content

class ContractVersion(BaseModel):
    id: int
    contract_id: int
    version: int
    file_path: str
    changes_description: Optional[str] = None
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True

class ContractInDB(ContractBase):
    id: int
    file_path: str
    versions: List[ContractVersion] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Contract(ContractInDB):
    client_name: Optional[str] = None  # Added for convenience in API responses

class ApprovalStep(BaseModel):
    step_id: str
    role: str
    approver_email: Optional[EmailStr] = None
    approver_id: Optional[int] = None
    is_approved: bool = False
    approved_at: Optional[datetime] = None
    comments: Optional[str] = None

class WorkflowTemplate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    steps: List[ApprovalStep]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkflowInstance(BaseModel):
    id: int
    template_id: str
    contract_id: int
    current_step_id: str
    status: str  # pending, approved, rejected
    steps: List[ApprovalStep]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    related_contract_id: Optional[int] = None
    related_client_id: Optional[int] = None
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: str = "medium"  # low, medium, high, urgent
    ai_generated: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class TaskInDB(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Task(TaskInDB):
    contract_title: Optional[str] = None
    client_name: Optional[str] = None

class AuditLogEntry(BaseModel):
    id: int
    entity_type: str  # client, contract, task, workflow
    entity_id: int
    action: str  # created, updated, deleted, status_changed, etc.
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True
