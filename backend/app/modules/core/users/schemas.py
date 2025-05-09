from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID

class UserDepartmentAssignment(BaseModel):
    user_id: int
    department_id: int
    role_id: int

class UserDepartmentAssignmentResponse(BaseModel):
    user_id: int
    department_id: int
    role_id: int
    id: int
    
    model_config = {
        "from_attributes": True
    }

class UserDepartmentRoleResponse(BaseModel):
    user_id: int
    department_id: int
    role_id: int
    department_name: str
    role_name: str
    
    model_config = {
        "from_attributes": True
    }
