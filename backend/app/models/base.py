from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TimestampModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
