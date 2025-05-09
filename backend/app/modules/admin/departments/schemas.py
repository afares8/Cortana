from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class DepartmentBase(BaseModel):
    name: str
    type: str
    ai_enabled: bool = False
    ai_profile: Optional[str] = None
    country: str
    timezone: str
    company_id: UUID

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    ai_enabled: Optional[bool] = None
    ai_profile: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None

class DepartmentOut(DepartmentBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }
