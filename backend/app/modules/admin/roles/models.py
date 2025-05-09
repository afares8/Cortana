from typing import Optional, List
from pydantic import Field
from uuid import UUID
from app.models.base import TimestampModel

class Role(TimestampModel):
    id: int = 0
    name: str
    description: str
    department_id: int
    permissions: List[str] = []

class UserDepartmentRole(TimestampModel):
    id: int = 0
    user_id: int
    department_id: int
    role_id: int
