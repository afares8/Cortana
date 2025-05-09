from typing import Optional
from pydantic import BaseModel

class AIProfileBase(BaseModel):
    name: str
    model: str
    embedding_id: str
    temperature: float = 0.7
    top_p: float = 0.95
    context_type: str
    department_id: int

class AIProfileCreate(AIProfileBase):
    pass

class AIProfileUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    embedding_id: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    context_type: Optional[str] = None

class AIProfileOut(AIProfileBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }
