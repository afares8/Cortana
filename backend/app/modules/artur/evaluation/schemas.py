from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ArturSuggestionBase(BaseModel):
    department_id: Optional[int] = None
    issue_summary: str
    suggested_action: Dict[str, Any] = {}
    confidence_score: float
    source: str

class ArturSuggestionCreate(ArturSuggestionBase):
    status: str = "pending"

class ArturSuggestionUpdate(BaseModel):
    status: str

class ArturSuggestionOut(ArturSuggestionBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
