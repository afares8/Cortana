from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.base import TimestampModel


class Contract(TimestampModel):
    id: Optional[int] = None
    title: str
    client_name: str
    contract_type: str
    start_date: date
    expiration_date: date
    responsible_lawyer: str
    file_path: str
    description: Optional[str] = None
    status: str = "active"  # active, expired, terminated


class ContractInDB(Contract):
    id: int
