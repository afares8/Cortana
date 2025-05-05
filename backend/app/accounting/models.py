from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr

from app.models.base import TimestampModel

class Company(TimestampModel):
    id: int
    name: str
    location: str  # Chitré, Arraiján, Zona Libre de Colón, etc.
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_zona_libre: bool = False  # Whether the company is in Zona Libre de Colón
    notes: Optional[str] = None

class TaxType(TimestampModel):
    id: int
    name: str  # ITBMS, ISR, CSS, Municipal, etc.
    authority: str  # DGI, CSS, Municipio, ANIP/ZLC
    description: Optional[str] = None

class Obligation(TimestampModel):
    id: int
    company_id: int
    tax_type_id: int
    name: str
    description: Optional[str] = None
    frequency: str  # monthly, quarterly, annual
    due_day: int  # Day of the month/quarter/year
    reminder_days: int = 7  # Days before due date to send reminder
    amount: Optional[float] = None
    status: str = "pending"  # pending, completed, overdue
    last_payment_date: Optional[datetime] = None
    next_due_date: datetime
    penalties: Optional[Dict[str, Any]] = None  # Dictionary with penalty information

class Payment(TimestampModel):
    id: int
    obligation_id: int
    amount: float
    payment_date: datetime
    receipt_number: Optional[str] = None
    notes: Optional[str] = None
    attachment_id: Optional[int] = None

class Attachment(TimestampModel):
    id: int
    file_name: str
    file_path: str
    file_type: str
    uploaded_by: Optional[str] = None
    upload_date: datetime
