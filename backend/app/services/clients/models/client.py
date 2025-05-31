from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr

from app.models.base import TimestampModel

class Director(BaseModel):
    name: str
    dob: date
    country: str

class UBO(BaseModel):
    name: str
    dob: date
    country: str
    percentage_ownership: float

class ClientDocument(TimestampModel):
    id: int
    client_id: int
    type: str
    file_path: str
    received_date: date
    expiry_date: Optional[date] = None
    is_validated: bool = False

class Client(TimestampModel):
    id: int
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    kyc_verified: bool = False
    notes: Optional[str] = None
    dob: Optional[date] = None
    nationality: Optional[str] = None
    registration_number: Optional[str] = None
    incorporation_date: Optional[date] = None
    incorporation_country: Optional[str] = None
    directors: List[Dict[str, Any]] = []
    ubos: List[Dict[str, Any]] = []
