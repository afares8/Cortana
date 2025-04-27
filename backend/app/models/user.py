from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from app.models.base import TimestampModel


class User(TimestampModel):
    id: Optional[int] = None
    email: EmailStr
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False


class UserInDB(User):
    pass
