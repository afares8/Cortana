from datetime import date
from typing import Optional
from pydantic import BaseModel


class ContractBase(BaseModel):
    title: str
    client_name: str
    contract_type: str
    start_date: date
    expiration_date: date
    responsible_lawyer: str
    description: Optional[str] = None
    status: str = "active"  # active, expired, terminated


class ContractCreate(ContractBase):
    pass


class ContractUpdate(ContractBase):
    title: Optional[str] = None
    client_name: Optional[str] = None
    contract_type: Optional[str] = None
    start_date: Optional[date] = None
    expiration_date: Optional[date] = None
    responsible_lawyer: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ContractInDBBase(ContractBase):
    id: int
    file_path: str
    created_at: date
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True


class Contract(ContractInDBBase):
    pass
