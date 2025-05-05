from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class CompanyBase(BaseModel):
    name: str
    location: str
    address: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    is_zona_libre: bool = False
    notes: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    is_zona_libre: Optional[bool] = None
    notes: Optional[str] = None

class CompanyInDB(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Company(CompanyInDB):
    pass

class TaxTypeBase(BaseModel):
    name: str
    authority: str
    description: Optional[str] = None

class TaxTypeCreate(TaxTypeBase):
    pass

class TaxTypeUpdate(BaseModel):
    name: Optional[str] = None
    authority: Optional[str] = None
    description: Optional[str] = None

class TaxTypeInDB(TaxTypeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaxType(TaxTypeInDB):
    pass

class ObligationBase(BaseModel):
    company_id: int
    tax_type_id: int
    name: str
    description: Optional[str] = None
    frequency: str
    due_day: int
    reminder_days: int = 7
    amount: Optional[float] = None
    status: str = "pending"
    next_due_date: datetime
    penalties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ObligationCreate(ObligationBase):
    pass

class ObligationUpdate(BaseModel):
    company_id: Optional[int] = None
    tax_type_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    due_day: Optional[int] = None
    reminder_days: Optional[int] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    next_due_date: Optional[datetime] = None
    penalties: Optional[Dict[str, Any]] = None

class ObligationInDB(ObligationBase):
    id: int
    last_payment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Obligation(ObligationInDB):
    company_name: Optional[str] = None
    tax_type_name: Optional[str] = None

class PaymentBase(BaseModel):
    obligation_id: int
    amount: float
    payment_date: datetime
    receipt_number: Optional[str] = None
    notes: Optional[str] = None
    attachment_id: Optional[int] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_date: Optional[datetime] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None
    attachment_id: Optional[int] = None

class PaymentInDB(PaymentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Payment(PaymentInDB):
    pass

class AttachmentBase(BaseModel):
    file_name: str
    file_type: str
    uploaded_by: Optional[str] = None

class AttachmentCreate(AttachmentBase):
    file_content: str  # Base64 encoded file content

class AttachmentInDB(AttachmentBase):
    id: int
    file_path: str
    upload_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Attachment(AttachmentInDB):
    pass
