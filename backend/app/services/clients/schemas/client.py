from typing import Optional
from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    kyc_verified: bool = False
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    kyc_verified: Optional[bool] = None
    notes: Optional[str] = None

class ClientInDBBase(ClientBase):
    id: int
    
    class Config:
        from_attributes = True

class Client(ClientInDBBase):
    pass
