from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.traffic.interface import TrafficInterface
from app.services.traffic.schemas.traffic import (
    InvoiceDataUpload,
    InvoiceRecordResponse,
    InvoiceDataUploadResponse,
    ConsolidationRequest,
    ConsolidationResponse,
    SubmissionRequest,
    SubmissionResponse,
    TrafficSubmissionResponse
)
from app.auth.token import get_current_user
from app.models.user import User
from app.services.traffic.api.dmce_endpoints import router as dmce_router

router = APIRouter(tags=["traffic"])

router.include_router(dmce_router, prefix="")

@router.post("/upload", response_model=List[InvoiceRecordResponse])
async def upload_invoice_data(
    data: InvoiceDataUpload,
    current_user: Optional[User] = None
):
    """
    Upload invoice data for processing.
    
    This endpoint accepts invoice data in JSON format, validates it,
    and returns a list of processed invoice records with validation results.
    """
    traffic_interface = TrafficInterface(current_user=current_user)
    return await traffic_interface.upload_invoice_data(data.data)

@router.post("/consolidate", response_model=ConsolidationResponse)
async def consolidate_invoices(
    request: ConsolidationRequest,
    current_user: Optional[User] = None
):
    """
    Consolidate multiple invoices into one.
    
    This endpoint combines multiple invoice records into a single consolidated record.
    All invoices must have the same client and movement type.
    """
    traffic_interface = TrafficInterface(current_user=current_user)
    return await traffic_interface.consolidate_invoices(request)

@router.get("/records", response_model=List[InvoiceRecordResponse])
async def get_records(
    current_user: Optional[User] = None
):
    """
    List currently loaded records.
    
    This endpoint returns all pending traffic records (uploaded but not yet submitted)
    for the current user.
    """
    traffic_interface = TrafficInterface(current_user=current_user)
    return await traffic_interface.get_records()

@router.get("/record/{record_id}", response_model=InvoiceRecordResponse)
async def get_record(
    record_id: int,
    current_user: Optional[User] = None
):
    """
    Get details of a specific record.
    
    This endpoint returns the full details of a specific invoice record,
    including header information and line items.
    """
    try:
        traffic_interface = TrafficInterface(current_user=current_user)
        return await traffic_interface.get_record(record_id)
    except Exception as e:
        import logging
        logging.error(f"Error in get_record endpoint: {str(e)}")
        raise

@router.post("/submit", response_model=SubmissionResponse)
async def submit_to_dmce(
    request: SubmissionRequest,
    current_user: Optional[User] = None
):
    """
    Submit a record to the DMCE portal.
    
    This endpoint triggers the RPA process to submit the specified record
    to the DMCE portal. It performs final validations and returns the result
    of the submission.
    """
    traffic_interface = TrafficInterface(current_user=current_user)
    return await traffic_interface.submit_to_dmce(request)

@router.get("/logs", response_model=List[TrafficSubmissionResponse])
async def get_submission_logs(
    current_user: Optional[User] = None
):
    """
    Retrieve audit logs/history.
    
    This endpoint returns a list of past traffic operations for reference,
    including submission status and DMCE numbers.
    """
    traffic_interface = TrafficInterface(current_user=current_user)
    return await traffic_interface.get_submission_logs()

@router.get("/logs/{submission_id}", response_model=TrafficSubmissionResponse)
async def get_submission_log(
    submission_id: int,
    current_user: Optional[User] = None
):
    """
    Detailed log entry.
    
    This endpoint provides detailed information about a specific submission,
    including the full data that was submitted and any error information.
    """
    traffic_interface = TrafficInterface(current_user=current_user)
    return await traffic_interface.get_submission_log(submission_id)
