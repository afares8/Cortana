from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

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
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
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
            
            for invoice_data in data.get("invoices", []):
                record = self._process_invoice(invoice_data)
                invoice_records.append(record)
            
            self.db.add_all(invoice_records)
            self.db.commit()
            
            for record in invoice_records:
                self.db.refresh(record)
            
            await self._get_ai_suggestions(invoice_records)
            
            response_records = [
                InvoiceRecordResponse.from_orm(record) 
                for record in invoice_records
            ]
            
            return response_records
            
        except Exception as e:
            self.db.rollback()
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
        
        record = InvoiceRecord(
            user_id=self.user_id,
            invoice_number=invoice_number,
            invoice_date=datetime.fromisoformat(invoice_data.get("invoice_date")),
            client_name=invoice_data.get("client_name"),
            client_id=invoice_data.get("client_id"),
            movement_type=invoice_data.get("movement_type"),
            total_value=float(invoice_data.get("total_value", 0)),
            total_weight=float(invoice_data.get("total_weight", 0)),
            status="Validated",
            validation_errors=[],
            ai_suggestions=[]
        )
        
        validation_errors = []
        if not record.client_name:
            validation_errors.append("Client name is required")
        if not record.client_id:
            validation_errors.append("Client ID is required")
        
        if validation_errors:
            record.status = "Error"
            record.validation_errors = validation_errors
        
        items = []
        for item_data in invoice_data.get("items", []):
            item = InvoiceItem(
                tariff_code=item_data.get("tariff_code"),
                description=item_data.get("description"),
                quantity=float(item_data.get("quantity", 0)),
                unit=item_data.get("unit", ""),
                weight=float(item_data.get("weight", 0)),
                value=float(item_data.get("value", 0)),
                volume=float(item_data.get("volume", 0)) if item_data.get("volume") else None
            )
            items.append(item)
        
        if not items:
            validation_errors.append("Invoice must have at least one item")
            record.status = "Error"
            record.validation_errors = validation_errors
        
        record.items = items
        
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
            else:
                suggestions_by_id = await self.ai_analyzer.analyze_invoices_batch(valid_records)
                
                # Update each record with its suggestions
                for record in valid_records:
                    if record.id in suggestions_by_id:
                        record.ai_suggestions = suggestions_by_id[record.id]
            
            self.db.commit()
                
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
                record = self.db.query(InvoiceRecord).filter(
                    InvoiceRecord.id == invoice_id,
                    InvoiceRecord.user_id == self.user_id
                ).first()
                
                if not record:
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
                validation_errors=[],
                ai_suggestions=[]
            )
            
            all_items = []
            for record in invoice_records:
                for item in record.items:
                    new_item = InvoiceItem(
                        tariff_code=item.tariff_code,
                        description=item.description,
                        quantity=item.quantity,
                        unit=item.unit,
                        weight=item.weight,
                        value=item.value,
                        volume=item.volume
                    )
                    all_items.append(new_item)
            
            consolidated_record.items = all_items
            
            for record in invoice_records:
                record.status = "Consolidated"
                record.consolidated_into_id = consolidated_record.id
            
            self.db.add(consolidated_record)
            self.db.commit()
            self.db.refresh(consolidated_record)
            
            await self._get_ai_suggestions([consolidated_record])
            
            return ConsolidationResponse(
                consolidated_record=InvoiceRecordResponse.from_orm(consolidated_record),
                message=f"Successfully consolidated {len(invoice_records)} invoices"
            )
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error consolidating invoices: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error consolidating invoices: {str(e)}"
            )
    
    def get_records(self) -> List[InvoiceRecordResponse]:
        """
        Get all pending invoice records for the current user.
        
        Returns:
            List of invoice records
        """
        try:
            records = self.db.query(InvoiceRecord).filter(
                InvoiceRecord.user_id == self.user_id,
                InvoiceRecord.status.in_(["Validated", "Error"])
            ).all()
            
            return [InvoiceRecordResponse.from_orm(record) for record in records]
            
        except Exception as e:
            logger.error(f"Error getting invoice records: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting invoice records: {str(e)}"
            )
    
    def get_record(self, record_id: int) -> InvoiceRecordResponse:
        """
        Get a specific invoice record by ID.
        
        Args:
            record_id: ID of the invoice record
            
        Returns:
            Invoice record details
        """
        try:
            record = self.db.query(InvoiceRecord).filter(
                InvoiceRecord.id == record_id,
                InvoiceRecord.user_id == self.user_id
            ).first()
            
            if not record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Invoice record with ID {record_id} not found"
                )
            
            return InvoiceRecordResponse.from_orm(record)
            
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
            record = self.db.query(InvoiceRecord).filter(
                InvoiceRecord.id == record_id,
                InvoiceRecord.user_id == self.user_id
            ).first()
            
            if not record:
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
            
            submission = TrafficSubmission(
                user_id=self.user_id,
                movement_type=record.movement_type,
                client_name=record.client_name,
                client_id=record.client_id,
                total_value=record.total_value,
                total_weight=record.total_weight,
                total_items=len(record.items),
                status="Pending",
                is_consolidated=record.is_consolidated,
                original_invoice_ids=request.invoice_record_ids if record.is_consolidated else None
            )
            
            self.db.add(submission)
            self.db.commit()
            self.db.refresh(submission)
            
            record.submission_id = submission.id
            record.status = "Submitted"
            self.db.commit()
            
            success, dmce_number, error_message = await self.rpa.submit_to_dmce(
                record=record,
                items=record.items
            )
            
            submission.status = "Submitted" if success else "Failed"
            submission.dmce_number = dmce_number
            submission.error_message = error_message
            self.db.commit()
            
            return SubmissionResponse(
                success=success,
                dmce_number=dmce_number,
                error_message=error_message,
                submission_id=submission.id
            )
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error submitting to DMCE: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error submitting to DMCE: {str(e)}"
            )
    
    def get_submission_logs(self) -> List[TrafficSubmissionResponse]:
        """
        Get submission logs/history for the current user.
        
        Returns:
            List of submission logs
        """
        try:
            submissions = self.db.query(TrafficSubmission).filter(
                TrafficSubmission.user_id == self.user_id
            ).order_by(TrafficSubmission.submission_date.desc()).all()
            
            return [TrafficSubmissionResponse.from_orm(submission) for submission in submissions]
            
        except Exception as e:
            logger.error(f"Error getting submission logs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting submission logs: {str(e)}"
            )
    
    def get_submission_log(self, submission_id: int) -> TrafficSubmissionResponse:
        """
        Get detailed log for a specific submission.
        
        Args:
            submission_id: ID of the submission
            
        Returns:
            Detailed submission log
        """
        try:
            submission = self.db.query(TrafficSubmission).filter(
                TrafficSubmission.id == submission_id,
                TrafficSubmission.user_id == self.user_id
            ).first()
            
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission with ID {submission_id} not found"
                )
            
            return TrafficSubmissionResponse.from_orm(submission)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting submission log: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting submission log: {str(e)}"
            )
