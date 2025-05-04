from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class WorkflowStepBase(BaseModel):
    step_id: str
    role: str
    approver_email: Optional[str] = None
    is_approved: bool = False

class WorkflowTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]

class WorkflowTemplateCreate(WorkflowTemplateBase):
    id: str

class WorkflowTemplateUpdate(WorkflowTemplateBase):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None

class WorkflowTemplateInDBBase(WorkflowTemplateBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkflowTemplate(WorkflowTemplateInDBBase):
    pass

class WorkflowInstanceBase(BaseModel):
    template_id: str
    contract_id: int
    current_step_id: str
    status: str  # pending, approved, rejected
    steps: List[Dict[str, Any]]

class WorkflowInstanceCreate(WorkflowInstanceBase):
    pass

class WorkflowInstanceUpdate(BaseModel):
    current_step_id: Optional[str] = None
    status: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None

class WorkflowInstanceInDBBase(WorkflowInstanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkflowInstance(WorkflowInstanceInDBBase):
    pass
