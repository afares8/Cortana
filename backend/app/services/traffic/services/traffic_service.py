from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import logging

from fastapi import HTTPException, status

from app.services.traffic.db import traffic_submissions_db, invoice_records_db, invoice_items_db
from app.services.traffic.models.traffic import TrafficSubmission, InvoiceRecord, InvoiceItem
from app.services.traffic.schemas.traffic import (
    InvoiceRecordCreate, 
    InvoiceRecordResponse,
    TrafficSubmissionCreate,
    TrafficSubmissionResponse,
    ConsolidationRequest,
    ConsolidationResponse,
    SubmissionRequest,
    SubmissionResponse
)
from app.services.traffic.utils.rpa import DMCEAutomator
from app.services.traffic.utils.ai_analyzer import TrafficAIAnalyzer

logger = logging.getLogger(__name__)

class TrafficService:
    """Service for Traffic module operations."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.rpa = DMCEAutomator()
        self.ai_analyzer = TrafficAIAnalyzer()
    
    async def upload_invoice_data(self, data: Dict[str, Any]) -> List[InvoiceRecordResponse]:
        """
        Upload and validate invoice data.
        
        Args:
            data: JSON data containing invoice information
            
        Returns:
            List of validated invoice records
        """
        try:
            invoice_records = []
            validation_errors = {}
            
            if "invoices" in data:
                invoice_data_list = data.get("invoices", [])
            else:
                invoice_data_list = [data]
            
            for invoice_data in invoice_data_list:
                record = self._process_invoice(invoice_data)
                saved_record = invoice_records_db.create(obj_in=record)
                
                for item in record.items:
                    item.invoice_id = saved_record.id
                    invoice_items_db.create(obj_in=item)
                
                invoice_records.append(saved_record)
            
            await self._get_ai_suggestions(invoice_records)
            
            response_records = [
                InvoiceRecordResponse.model_validate(record.model_dump()) 
                for record in invoice_records
            ]
            
            return response_records
            
        except Exception as e:
            logger.error(f"Error processing invoice data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing invoice data: {str(e)}"
            )
    
    def _process_invoice(self, invoice_data: Dict[str, Any]) -> InvoiceRecord:
        """Process a single invoice from the uploaded data."""
        invoice_number = invoice_data.get("invoice_number")
        if not invoice_number:
            raise ValueError("Invoice number is required")
        
        validation_errors = []
        if not invoice_data.get("client_name"):
            validation_errors.append("Client name is required")
        if not invoice_data.get("client_id"):
            validation_errors.append("Client ID is required")
        
        status = "Error" if validation_errors else "Validated"
        
        items = []
        for item_data in invoice_data.get("items", []):
            item = InvoiceItem(
                id=0,  # Will be set by InMemoryDB
                invoice_id=0,  # Will be set later
                tariff_code=item_data.get("tariff_code", ""),
                description=item_data.get("description", ""),
                quantity=float(item_data.get("quantity", 0)),
                unit=item_data.get("unit", ""),
                weight=float(item_data.get("weight", 0)),
                value=float(item_data.get("value", 0)),
                volume=float(item_data.get("volume", 0)) if item_data.get("volume") else None
            )
            items.append(item)
        
        if not items:
            validation_errors.append("Invoice must have at least one item")
            status = "Error"
        
        record = InvoiceRecord(
            id=0,  # Will be set by InMemoryDB
            user_id=self.user_id,
            invoice_number=invoice_number,
            invoice_date=datetime.fromisoformat(invoice_data.get("invoice_date")),
            client_name=invoice_data.get("client_name", ""),
            client_id=invoice_data.get("client_id", ""),
            movement_type=invoice_data.get("movement_type", ""),
            total_value=float(invoice_data.get("total_value", 0)),
            total_weight=float(invoice_data.get("total_weight", 0)),
            status=status,
            validation_errors=validation_errors if validation_errors else None,
            ai_suggestions=None,
            items=items
        )
        
        return record
    
    async def _get_ai_suggestions(self, invoice_records: List[InvoiceRecord]) -> None:
        """
        Get AI suggestions for invoice records.
        
        This method uses the TrafficAIAnalyzer to analyze invoice records
        and attach AI suggestions to each record.
        
        Args:
            invoice_records: List of invoice records to analyze
        """
        try:
            valid_records = [r for r in invoice_records if r.status != "Error"]
            
            if not valid_records:
                return
            
            if len(valid_records) == 1:
                record = valid_records[0]
                suggestions = await self.ai_analyzer.analyze_invoice(record)
                record.ai_suggestions = suggestions
                
                invoice_records_db.update(
                    id=record.id, 
                    obj_in=record
                )
            else:
                suggestions_by_id = await self.ai_analyzer.analyze_invoices_batch(valid_records)
                
                # Update each record with its suggestions
                for record in valid_records:
                    if record.id in suggestions_by_id:
                        record.ai_suggestions = suggestions_by_id[record.id]
                        
                        invoice_records_db.update(
                            id=record.id, 
                            obj_in=record
                        )
                
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {str(e)}")
            pass
    
    async def consolidate_invoices(self, request: ConsolidationRequest) -> ConsolidationResponse:
        """
        Consolidate multiple invoices into one.
        
        Args:
            request: Consolidation request with invoice record IDs
            
        Returns:
            Consolidated invoice record
        """
        try:
            invoice_ids = request.invoice_record_ids
            if len(invoice_ids) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least two invoices are required for consolidation"
                )
            
            invoice_records = []
            for invoice_id in invoice_ids:
                record = invoice_records_db.get(invoice_id)
                
                if not record or record.user_id != self.user_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Invoice record with ID {invoice_id} not found"
                    )
                
                if record.status in ["Consolidated", "Submitted"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invoice record with ID {invoice_id} has already been processed"
                    )
                
                invoice_records.append(record)
            
            client_name = invoice_records[0].client_name
            client_id = invoice_records[0].client_id
            movement_type = invoice_records[0].movement_type
            
            for record in invoice_records[1:]:
                if record.client_name != client_name:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="All invoices must have the same client"
                    )
                
                if record.movement_type != movement_type:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="All invoices must have the same movement type"
                    )
            
            consolidated_record = InvoiceRecord(
                id=0,  # Will be set by InMemoryDB
                user_id=self.user_id,
                invoice_number=f"CONS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                invoice_date=max([record.invoice_date for record in invoice_records]),
                client_name=client_name,
                client_id=client_id,
                movement_type=movement_type,
                total_value=sum([record.total_value for record in invoice_records]),
                total_weight=sum([record.total_weight for record in invoice_records]),
                status="Validated",
                is_consolidated=True,
                validation_errors=None,
                ai_suggestions=None,
                items=[]
            )
            
            saved_record = invoice_records_db.create(obj_in=consolidated_record)
            
            all_items = []
            for record in invoice_records:
                record_items = []
                for item_filter in invoice_items_db.get_multi(filters={"invoice_id": record.id}):
                    record_items.append(item_filter)
                
                for item in record_items:
                    new_item = InvoiceItem(
                        id=0,  # Will be set by InMemoryDB
                        invoice_id=saved_record.id,
                        tariff_code=item.tariff_code,
                        description=item.description,
                        quantity=item.quantity,
                        unit=item.unit,
                        weight=item.weight,
                        value=item.value,
                        volume=item.volume
                    )
                    saved_item = invoice_items_db.create(obj_in=new_item)
                    all_items.append(saved_item)
            
            for record in invoice_records:
                record.status = "Consolidated"
                record.consolidated_into_id = saved_record.id
                invoice_records_db.update(id=record.id, obj_in=record)
            
            # Get AI suggestions for the consolidated record
            await self._get_ai_suggestions([saved_record])
            
            # Get the updated record with AI suggestions
            updated_record = invoice_records_db.get(saved_record.id)
            
            return ConsolidationResponse(
                consolidated_record=InvoiceRecordResponse.model_validate(updated_record.model_dump()),
                message=f"Successfully consolidated {len(invoice_records)} invoices"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error consolidating invoices: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error consolidating invoices: {str(e)}"
            )
    
    async def get_records(self) -> List[InvoiceRecordResponse]:
        """
        Get all pending invoice records for the current user.
        
        Returns:
            List of invoice records
        """
        try:
            all_records = invoice_records_db.get_multi()
            
            records = [
                record for record in all_records 
                if record.user_id == self.user_id and record.status in ["Validated", "Error"]
            ]
            
            return [InvoiceRecordResponse.model_validate(record.model_dump()) for record in records]
            
        except Exception as e:
            logger.error(f"Error getting invoice records: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting invoice records: {str(e)}"
            )
    
    async def get_record(self, record_id: int) -> InvoiceRecordResponse:
        """
        Get a specific invoice record by ID.
        
        Args:
            record_id: ID of the invoice record
            
        Returns:
            Invoice record details
        """
        try:
            record_id = int(record_id)
            logger.info(f"Retrieving record with ID {record_id}")
            
            record = invoice_records_db.get(record_id)
            
            if not record:
                logger.error(f"No record found with ID {record_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Invoice record with ID {record_id} not found"
                )
            
            logger.info(f"Found record: {record.invoice_number}")
            
            if record.user_id != self.user_id:
                logger.error(f"Record {record_id} belongs to user {record.user_id}, not current user {self.user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Invoice record with ID {record_id} not found"
                )
            
            items = invoice_items_db.get_multi(filters={"invoice_id": record_id})
            logger.info(f"Found {len(items)} items for record {record_id}")
            
            # Attach items to record
            record.items = items
            
            return InvoiceRecordResponse.model_validate(record.model_dump())
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting invoice record: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting invoice record: {str(e)}"
            )
    
    async def submit_to_dmce(self, request: SubmissionRequest) -> SubmissionResponse:
        """
        Submit a record to the DMCE portal.
        
        Args:
            request: Submission request with record ID
            
        Returns:
            Submission result
        """
        try:
            record_id = request.record_id
            
            all_records = invoice_records_db.get_multi()
            
            matching_records = [r for r in all_records if r.id == record_id]
            
            if not matching_records:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Invoice record with ID {record_id} not found"
                )
            
            record = matching_records[0]
            
            if record.user_id != self.user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Invoice record with ID {record_id} not found"
                )
            
            if record.status not in ["Validated"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invoice record with ID {record_id} is not ready for submission"
                )
            
            if not record.movement_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Movement type is required for DMCE submission"
                )
            
            items = []
            for item in invoice_items_db.get_multi(filters={"invoice_id": record_id}):
                items.append(item)
            
            submission = TrafficSubmission(
                id=0,  # Will be set by InMemoryDB
                user_id=self.user_id,
                movement_type=record.movement_type,
                client_name=record.client_name,
                client_id=record.client_id,
                total_value=record.total_value,
                total_weight=record.total_weight,
                total_items=len(items),
                status="Pending",
                is_consolidated=record.is_consolidated,
                original_invoice_ids=[record_id],
                invoice_records=[]
            )
            
            # Save submission
            saved_submission = traffic_submissions_db.create(obj_in=submission)
            
            record.submission_id = saved_submission.id
            record.status = "Submitted"
            invoice_records_db.update(id=record.id, obj_in=record)
            
            success, dmce_number, error_message = await self.rpa.submit_to_dmce(
                record=record,
                items=items
            )
            
            saved_submission.status = "Submitted" if success else "Failed"
            saved_submission.dmce_number = dmce_number
            saved_submission.error_message = error_message
            traffic_submissions_db.update(id=saved_submission.id, obj_in=saved_submission)
            
            return SubmissionResponse(
                success=success,
                dmce_number=dmce_number,
                error_message=error_message,
                submission_id=saved_submission.id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error submitting to DMCE: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error submitting to DMCE: {str(e)}"
            )
    
    async def get_submission_logs(self) -> List[TrafficSubmissionResponse]:
        """
        Get submission logs/history for the current user.
        
        Returns:
            List of submission logs
        """
        try:
            all_submissions = traffic_submissions_db.get_multi()
            
            submissions = [
                submission for submission in all_submissions 
                if submission.user_id == self.user_id
            ]
            
            submissions.sort(key=lambda x: x.submission_date, reverse=True)
            
            return [TrafficSubmissionResponse.model_validate(submission.model_dump()) for submission in submissions]
            
        except Exception as e:
            logger.error(f"Error getting submission logs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting submission logs: {str(e)}"
            )
    
    async def get_submission_log(self, submission_id: int) -> TrafficSubmissionResponse:
        """
        Get detailed log for a specific submission.
        
        Args:
            submission_id: ID of the submission
            
        Returns:
            Detailed submission log
        """
        try:
            all_submissions = traffic_submissions_db.get_multi()
            
            matching_submissions = [s for s in all_submissions if s.id == submission_id]
            
            if not matching_submissions:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission with ID {submission_id} not found"
                )
            
            submission = matching_submissions[0]
            
            if submission.user_id != self.user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission with ID {submission_id} not found"
                )
            
            # Get related invoice records
            invoice_records = []
            for record in invoice_records_db.get_multi(filters={"submission_id": submission_id}):
                invoice_records.append(record)
            
            # Attach invoice records to submission
            submission.invoice_records = invoice_records
            
            return TrafficSubmissionResponse.model_validate(submission.model_dump())
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting submission log: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting submission log: {str(e)}"
            )
