from typing import List, Optional, Dict, Any

from fastapi import Depends, HTTPException, status

from app.db.base import InMemoryDB
from app.services.traffic.models.traffic import TrafficSubmission, InvoiceRecord, InvoiceItem
from app.services.traffic.schemas.traffic import (
    TrafficSubmissionCreate, 
    TrafficSubmissionResponse, 
    InvoiceRecordCreate,
    InvoiceRecordResponse,
    ConsolidationRequest,
    ConsolidationResponse,
    SubmissionRequest,
    SubmissionResponse
)
from app.services.traffic.services.traffic_service import TrafficService
from app.auth.token import get_current_user
from app.models.user import User

class TrafficInterface:
    """Interface for Traffic module operations."""
    
    def __init__(self, current_user: Optional[User] = None):
        user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
        self.service = TrafficService(user_id=user_id)
    
    async def upload_invoice_data(self, data: Dict[str, Any]) -> List[InvoiceRecordResponse]:
        """Upload and validate invoice data."""
        return await self.service.upload_invoice_data(data)
    
    async def consolidate_invoices(self, request: ConsolidationRequest) -> ConsolidationResponse:
        """Consolidate multiple invoices into one."""
        return await self.service.consolidate_invoices(request)
    
    async def get_records(self) -> List[InvoiceRecordResponse]:
        """Get all pending invoice records."""
        return await self.service.get_records()
    
    async def get_record(self, record_id: int) -> InvoiceRecordResponse:
        """Get a specific invoice record by ID."""
        return await self.service.get_record(record_id)
    
    async def submit_to_dmce(self, request: SubmissionRequest) -> SubmissionResponse:
        """Submit a record to the DMCE portal."""
        return await self.service.submit_to_dmce(request)
    
    async def get_submission_logs(self) -> List[TrafficSubmissionResponse]:
        """Get submission logs/history."""
        return await self.service.get_submission_logs()
    
    async def get_submission_log(self, submission_id: int) -> TrafficSubmissionResponse:
        """Get detailed log for a specific submission."""
        return await self.service.get_submission_log(submission_id)
