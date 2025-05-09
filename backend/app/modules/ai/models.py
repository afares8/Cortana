from typing import Optional, Dict, Any
from pydantic import Field
from app.models.base import TimestampModel

class AIProfile(TimestampModel):
    id: int = 0
    name: str
    model: str
    embedding_id: str
    temperature: float = 0.7
    top_p: float = 0.95
    context_type: str
    department_id: int
