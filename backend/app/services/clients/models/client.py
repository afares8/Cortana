from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr

from app.models.base import TimestampModel

class Client(TimestampModel):
    id: int
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    kyc_verified: bool = False
    notes: Optional[str] = None
