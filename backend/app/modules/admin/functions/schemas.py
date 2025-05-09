from typing import Optional, Dict, Any
from pydantic import BaseModel

class FunctionBase(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}
    department_id: int

class FunctionCreate(FunctionBase):
    pass

class FunctionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

class FunctionOut(FunctionBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }
