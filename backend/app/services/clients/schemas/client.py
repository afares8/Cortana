from typing import Optional, List
from datetime import date
from pydantic import BaseModel, EmailStr, validator
from app.services.clients.models.client import Director, UBO

class ClientBase(BaseModel):
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    kyc_verified: bool = False
    notes: Optional[str] = None
    client_type: Optional[str] = None
    country: Optional[str] = None
    dob: Optional[date] = None
    nationality: Optional[str] = None
    registration_number: Optional[str] = None
    incorporation_date: Optional[date] = None
    incorporation_country: Optional[str] = None
    directors: List[Director] = []
    ubos: List[UBO] = []

class ClientCreate(ClientBase):
    @validator('dob', 'nationality')
    def validate_individual_fields(cls, v, values):
        client_type = values.get('client_type')
        if client_type == 'individual' and v is None:
            raise ValueError('Field is required for individual clients')
        return v
    
    @validator('registration_number', 'incorporation_date', 'incorporation_country')
    def validate_legal_entity_fields(cls, v, values):
        client_type = values.get('client_type')
        if client_type == 'legal' and v is None:
            raise ValueError('Field is required for legal entity clients')
        return v

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    kyc_verified: Optional[bool] = None
    notes: Optional[str] = None
    client_type: Optional[str] = None
    country: Optional[str] = None
    dob: Optional[date] = None
    nationality: Optional[str] = None
    registration_number: Optional[str] = None
    incorporation_date: Optional[date] = None
    incorporation_country: Optional[str] = None
    directors: Optional[List[Director]] = None
    ubos: Optional[List[UBO]] = None

class ClientInDBBase(ClientBase):
    id: int
    
    class Config:
        from_attributes = True

class Client(ClientInDBBase):
    pass
