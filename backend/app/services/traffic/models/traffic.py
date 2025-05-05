from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.models.base import TimestampModel

class InvoiceItem(TimestampModel):
    """Model for individual items in an invoice."""
    id: int
    invoice_id: int
    tariff_code: str
    description: str
    quantity: float
    unit: str
    weight: float
    value: float
    volume: Optional[float] = None
    
    class Config:
        from_attributes = True

class InvoiceRecord(TimestampModel):
    """Model for invoice records uploaded to the system."""
    id: int
    user_id: int
    submission_id: Optional[int] = None
    upload_date: datetime = datetime.utcnow()
    invoice_number: str
    invoice_date: datetime
    client_name: str
    client_id: str
    movement_type: str  # "Exit" or "Transfer"
    total_value: float
    total_weight: float
    status: str  # "Validated", "Error", "Consolidated", "Submitted"
    validation_errors: Optional[Dict[str, Any]] = None
    ai_suggestions: Optional[List[str]] = None
    is_consolidated: bool = False
    consolidated_into_id: Optional[int] = None  # ID of the consolidated record this was merged into
    items: List[InvoiceItem] = []
    
    class Config:
        from_attributes = True

class TrafficSubmission(TimestampModel):
    """Model for tracking DMCE submissions."""
    id: int
    user_id: int
    submission_date: datetime = datetime.utcnow()
    movement_type: str  # "Exit" or "Transfer"
    client_name: str
    client_id: str
    total_value: float
    total_weight: float
    total_items: int
    dmce_number: Optional[str] = None  # Will be null until successful submission
    status: str  # "Pending", "Submitted", "Failed"
    error_message: Optional[str] = None
    is_consolidated: bool = False
    original_invoice_ids: Optional[List[int]] = None  # Store IDs of original invoices if consolidated
    invoice_records: List[InvoiceRecord] = []
    
    class Config:
        from_attributes = True
