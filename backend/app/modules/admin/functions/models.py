from typing import Optional, Dict, Any
from pydantic import Field
from app.models.base import TimestampModel

class Function(TimestampModel):
    id: int = 0
    name: str
    description: str
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}
    department_id: int
