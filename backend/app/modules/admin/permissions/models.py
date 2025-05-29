from typing import List
from pydantic import Field
from app.models.base import TimestampModel

class Permission(TimestampModel):
    id: int = 0
    name: str
    description: str
    category: str  # e.g., "contract", "financial", "compliance"
    
class PermissionGroup(TimestampModel):
    id: int = 0
    name: str
    permissions: List[str] = []
