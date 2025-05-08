from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.base import TimestampModel

class SystemSetting(TimestampModel):
    """
    Model for system settings stored in the database.
    Follows the key-value store pattern with category grouping.
    """
    id: Optional[int] = None
    category: str
    key: str
    value: Dict[str, Any]  # Represents JSONB in the database

class SystemSettingInDB(SystemSetting):
    """
    Database representation of a system setting.
    Ensures id is always present for database records.
    """
    id: int
