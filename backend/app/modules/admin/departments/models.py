from typing import Optional
from pydantic import Field
from uuid import UUID, uuid4
from datetime import datetime
from app.models.base import TimestampModel

class Department(TimestampModel):
    id: int = 0
    name: str
    type: str  # legal, accounting, traffic, etc.
    ai_enabled: bool = False
    ai_profile: Optional[str] = None
    country: str
    timezone: str
    company_id: UUID
