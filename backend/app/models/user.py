from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from app.models.base import TimestampModel


class UserRole(str, Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    VIEWER = "viewer"


class User(TimestampModel):
    id: Optional[int] = None
    email: EmailStr
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    role: UserRole = UserRole.VIEWER


class UserInDB(User):
    pass
