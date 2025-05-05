from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field

from app.models.base import TimestampModel

class Company(TimestampModel):
    id: Optional[int] = None
    name: str
    location: str  # Chitré, Arraiján, Zona Libre de Colón, etc.
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_zona_libre: bool = False  # Whether the company is in Zona Libre de Colón
    notes: Optional[str] = None

class TaxType(TimestampModel):
    id: Optional[int] = None
    name: str  # ITBMS, ISR, CSS, Municipal, etc.
    authority: str  # DGI, CSS, Municipio, ANIP/ZLC
    description: Optional[str] = None

class Obligation(TimestampModel):
    id: Optional[int] = None
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
    company_name: Optional[str] = None  # Added for frontend display
    tax_type_name: Optional[str] = None  # Added for frontend display

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


class AccessPermission(str, Enum):
    READ = "read"
    WRITE = "write"


class UserCompanyAccess(TimestampModel):
    id: Optional[int] = None
    user_id: int
    company_id: int
    permissions: AccessPermission = AccessPermission.READ
    
    # These fields are added for frontend display
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    company_name: Optional[str] = None

class Notification(TimestampModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: int
    message: str
    read: bool = False
    related_obligation_id: Optional[UUID] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": 1,
                "message": "ITBMS filing due in 5 days",
                "read": False,
                "related_obligation_id": "123e4567-e89b-12d3-a456-426614174001",
                "created_at": "2023-05-01T12:00:00Z",
                "updated_at": "2023-05-01T12:00:00Z"
            }
        }
        
class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class AuditLog(TimestampModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: int
    action: AuditAction
    entity_type: str  # obligation, payment, attachment, company
    entity_id: UUID
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
