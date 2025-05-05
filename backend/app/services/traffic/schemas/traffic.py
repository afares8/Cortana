from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class InvoiceItemBase(BaseModel):
    tariff_code: str
    description: str
    quantity: float
    unit: str
    weight: float
    value: float
    volume: Optional[float] = None

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemResponse(InvoiceItemBase):
    id: int
    
    class Config:
        orm_mode = True

class InvoiceRecordBase(BaseModel):
    invoice_number: str
    invoice_date: datetime
    client_name: str
    client_id: str
    movement_type: Optional[str] = None  # "Exit" or "Transfer"
    total_value: float
    total_weight: float

class InvoiceRecordCreate(InvoiceRecordBase):
    items: List[InvoiceItemCreate]

class InvoiceRecordResponse(InvoiceRecordBase):
    id: int
    upload_date: datetime
    status: str
    validation_errors: Optional[List[str]] = None
    ai_suggestions: Optional[List[str]] = None
    is_consolidated: bool = False
    consolidated_into_id: Optional[int] = None
    items: List[InvoiceItemResponse]
    
    class Config:
        orm_mode = True

class TrafficSubmissionBase(BaseModel):
    movement_type: str  # "Exit" or "Transfer"
    client_name: str
    client_id: str
    total_value: float
    total_weight: float
    total_items: int

class TrafficSubmissionCreate(TrafficSubmissionBase):
    invoice_record_ids: List[int]

class TrafficSubmissionResponse(TrafficSubmissionBase):
    id: int
    submission_date: datetime
    dmce_number: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    is_consolidated: bool = False
    original_invoice_ids: Optional[List[int]] = None
    
    class Config:
        orm_mode = True

class ConsolidationRequest(BaseModel):
    invoice_record_ids: List[int] = Field(..., description="IDs of invoice records to consolidate")

class ConsolidationResponse(BaseModel):
    consolidated_record: InvoiceRecordResponse
    message: str = "Invoices consolidated successfully"

class SubmissionRequest(BaseModel):
    record_id: int = Field(..., description="ID of the invoice record to submit")

class SubmissionResponse(BaseModel):
    success: bool
    dmce_number: Optional[str] = None
    error_message: Optional[str] = None
    submission_id: Optional[int] = None

class InvoiceDataUpload(BaseModel):
    data: Dict[str, Any] = Field(..., description="JSON data containing invoice information")

class InvoiceDataUploadResponse(BaseModel):
    records: List[InvoiceRecordResponse]
    validation_summary: Dict[str, Any]
