from typing import Optional, List
from pydantic import BaseModel

class PermissionBase(BaseModel):
    name: str
    description: str
    category: str

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class PermissionOut(PermissionBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

class PermissionGroupBase(BaseModel):
    name: str
    permissions: List[str] = []

class PermissionGroupCreate(PermissionGroupBase):
    pass

class PermissionGroupUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[List[str]] = None

class PermissionGroupOut(PermissionGroupBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }
