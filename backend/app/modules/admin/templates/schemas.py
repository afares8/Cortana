from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel

class DepartmentTemplateBase(BaseModel):
    name: str
    description: str
    predefined_modules: List[str] = []
    roles: Dict[str, Any] = {}
    functions: Dict[str, Any] = {}
    ai_profile: Dict[str, Any] = {}

class DepartmentTemplateCreate(DepartmentTemplateBase):
    pass

class DepartmentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    predefined_modules: Optional[List[str]] = None
    roles: Optional[Dict[str, Any]] = None
    functions: Optional[Dict[str, Any]] = None
    ai_profile: Optional[Dict[str, Any]] = None

class DepartmentTemplateOut(DepartmentTemplateBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

class DepartmentFromTemplateRequest(BaseModel):
    template_id: int
    department_name: str
    company_id: str
    country: str
    timezone: str
    customize: Optional[Dict[str, Any]] = None
