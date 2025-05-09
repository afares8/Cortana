from typing import Optional, Dict, Any, List
from pydantic import Field
from app.models.base import TimestampModel

class DepartmentTemplate(TimestampModel):
    id: int = 0
    name: str
    description: str
    predefined_modules: List[str] = []
    roles: Dict[str, Any] = {}
    functions: Dict[str, Any] = {}
    ai_profile: Dict[str, Any] = {}
