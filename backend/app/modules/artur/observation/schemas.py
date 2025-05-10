from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ArturInsightBase(BaseModel):
    category: str
    entity_type: str
    entity_id: Optional[int] = None
    department_id: Optional[int] = None
    metrics: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

class ArturInsightCreate(ArturInsightBase):
    pass

class ArturInsightOut(ArturInsightBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
