from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID

class RoleBase(BaseModel):
    name: str
    description: str
    department_id: int
    permissions: List[str] = []

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleOut(RoleBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

class RoleAssignmentBase(BaseModel):
    user_id: int
    department_id: int
    role_id: int

class RoleAssignmentCreate(RoleAssignmentBase):
    pass

class RoleAssignmentOut(RoleAssignmentBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }
