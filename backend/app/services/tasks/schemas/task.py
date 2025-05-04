from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr

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
    related_contract_id: Optional[int] = None
    related_client_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    ai_generated: Optional[bool] = None

class TaskInDBBase(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    pass
