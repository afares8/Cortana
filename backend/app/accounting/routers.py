from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body, Query, Path
from fastapi.responses import JSONResponse
from pydantic import EmailStr

from app.core.config import settings
from app.accounting.schemas import (
    Company, CompanyCreate, CompanyUpdate,
    TaxType, TaxTypeCreate, TaxTypeUpdate,
    Obligation, ObligationCreate, ObligationUpdate,
    Payment, PaymentCreate, PaymentUpdate,
    Attachment, AttachmentCreate
)
from app.accounting.services import (
    create_company, get_company, get_companies, update_company, delete_company,
    create_tax_type, get_tax_type, get_tax_types, update_tax_type, delete_tax_type,
    create_obligation, get_obligation, get_obligations, update_obligation, delete_obligation,
    create_payment, get_payment, get_payments, update_payment, delete_payment,
    create_attachment, get_attachment, get_attachments, delete_attachment,
    get_upcoming_obligations, get_overdue_obligations, analyze_obligation_history
)

router = APIRouter()

@router.post("/companies", response_model=Company, status_code=201)
async def create_company_endpoint(company: CompanyCreate):
    """Create a new company."""
    return create_company(company.model_dump())

@router.get("/companies", response_model=List[Company])
async def get_companies_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    location: Optional[str] = None,
    is_zona_libre: Optional[bool] = None
):
    """Get a list of companies with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if location:
        filters["location"] = location
    if is_zona_libre is not None:
        filters["is_zona_libre"] = is_zona_libre
    
    return get_companies(skip=skip, limit=limit, filters=filters)

@router.get("/companies/{company_id}", response_model=Company)
async def get_company_endpoint(company_id: int = Path(..., gt=0)):
    """Get a company by ID."""
    company = get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/companies/{company_id}", response_model=Company)
async def update_company_endpoint(
    company_id: int = Path(..., gt=0),
    company_update: CompanyUpdate = Body(...)
):
    """Update a company."""
    company = update_company(company_id, company_update.model_dump(exclude_unset=True))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.delete("/companies/{company_id}", response_model=Dict[str, bool])
async def delete_company_endpoint(company_id: int = Path(..., gt=0)):
    """Delete a company."""
    result = delete_company(company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Company not found or has associated obligations")
    return {"success": True}

@router.post("/tax-types", response_model=TaxType, status_code=201)
async def create_tax_type_endpoint(tax_type: TaxTypeCreate):
    """Create a new tax type."""
    return create_tax_type(tax_type.model_dump())

@router.get("/tax-types", response_model=List[TaxType])
async def get_tax_types_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    authority: Optional[str] = None
):
    """Get a list of tax types with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if authority:
        filters["authority"] = authority
    
    return get_tax_types(skip=skip, limit=limit, filters=filters)

@router.get("/tax-types/{tax_type_id}", response_model=TaxType)
async def get_tax_type_endpoint(tax_type_id: int = Path(..., gt=0)):
    """Get a tax type by ID."""
    tax_type = get_tax_type(tax_type_id)
    if not tax_type:
        raise HTTPException(status_code=404, detail="Tax type not found")
    return tax_type

@router.put("/tax-types/{tax_type_id}", response_model=TaxType)
async def update_tax_type_endpoint(
    tax_type_id: int = Path(..., gt=0),
    tax_type_update: TaxTypeUpdate = Body(...)
):
    """Update a tax type."""
    tax_type = update_tax_type(tax_type_id, tax_type_update.model_dump(exclude_unset=True))
    if not tax_type:
        raise HTTPException(status_code=404, detail="Tax type not found")
    return tax_type

@router.delete("/tax-types/{tax_type_id}", response_model=Dict[str, bool])
async def delete_tax_type_endpoint(tax_type_id: int = Path(..., gt=0)):
    """Delete a tax type."""
    result = delete_tax_type(tax_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tax type not found or in use")
    return {"success": True}

@router.post("/obligations", response_model=Obligation, status_code=201)
async def create_obligation_endpoint(obligation: ObligationCreate):
    """Create a new obligation."""
    result = create_obligation(obligation.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="Company or tax type not found")
    return result

@router.get("/obligations", response_model=List[Obligation])
async def get_obligations_endpoint(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    tax_type_id: Optional[int] = None,
    status: Optional[str] = None,
    frequency: Optional[str] = None,
    due_before: Optional[datetime] = None
):
    """Get a list of obligations with optional filtering."""
    filters = {}
    if company_id:
        filters["company_id"] = company_id
    if tax_type_id:
        filters["tax_type_id"] = tax_type_id
    if status:
        filters["status"] = status
    if frequency:
        filters["frequency"] = frequency
    
    obligations = get_obligations(skip=skip, limit=limit, filters=filters)
    
    if due_before:
        filtered_obligations = []
        for obligation in obligations:
            if obligation.next_due_date < due_before:
                filtered_obligations.append(obligation)
        return filtered_obligations
    
    return obligations

@router.get("/obligations/{obligation_id}", response_model=Obligation)
async def get_obligation_endpoint(obligation_id: int = Path(..., gt=0)):
    """Get an obligation by ID."""
    obligation = get_obligation(obligation_id)
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return obligation

@router.put("/obligations/{obligation_id}", response_model=Obligation)
async def update_obligation_endpoint(
    obligation_id: int = Path(..., gt=0),
    obligation_update: ObligationUpdate = Body(...)
):
    """Update an obligation."""
    obligation = update_obligation(obligation_id, obligation_update.model_dump(exclude_unset=True))
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return obligation

@router.delete("/obligations/{obligation_id}", response_model=Dict[str, bool])
async def delete_obligation_endpoint(obligation_id: int = Path(..., gt=0)):
    """Delete an obligation."""
    result = delete_obligation(obligation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return {"success": True}

@router.post("/payments", response_model=Payment, status_code=201)
async def create_payment_endpoint(payment: PaymentCreate):
    """Create a new payment."""
    result = create_payment(payment.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return result

@router.get("/payments", response_model=List[Payment])
async def get_payments_endpoint(
    skip: int = 0,
    limit: int = 100,
    obligation_id: Optional[int] = None,
    payment_date_from: Optional[datetime] = None,
    payment_date_to: Optional[datetime] = None
):
    """Get a list of payments with optional filtering."""
    filters = {}
    if obligation_id:
        filters["obligation_id"] = obligation_id
    
    payments = get_payments(skip=skip, limit=limit, filters=filters)
    
    if payment_date_from or payment_date_to:
        filtered_payments = []
        for payment in payments:
            if payment_date_from and payment.payment_date < payment_date_from:
                continue
            if payment_date_to and payment.payment_date > payment_date_to:
                continue
            filtered_payments.append(payment)
        return filtered_payments
    
    return payments

@router.get("/payments/{payment_id}", response_model=Payment)
async def get_payment_endpoint(payment_id: int = Path(..., gt=0)):
    """Get a payment by ID."""
    payment = get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.put("/payments/{payment_id}", response_model=Payment)
async def update_payment_endpoint(
    payment_id: int = Path(..., gt=0),
    payment_update: PaymentUpdate = Body(...)
):
    """Update a payment."""
    payment = update_payment(payment_id, payment_update.model_dump(exclude_unset=True))
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/payments/{payment_id}", response_model=Dict[str, bool])
async def delete_payment_endpoint(payment_id: int = Path(..., gt=0)):
    """Delete a payment."""
    result = delete_payment(payment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"success": True}

@router.post("/attachments", response_model=Attachment, status_code=201)
async def create_attachment_endpoint(attachment: AttachmentCreate):
    """Create a new attachment."""
    return create_attachment(attachment.model_dump())

@router.get("/attachments", response_model=List[Attachment])
async def get_attachments_endpoint(
    skip: int = 0,
    limit: int = 100,
    file_type: Optional[str] = None,
    uploaded_by: Optional[str] = None
):
    """Get a list of attachments with optional filtering."""
    filters = {}
    if file_type:
        filters["file_type"] = file_type
    if uploaded_by:
        filters["uploaded_by"] = uploaded_by
    
    return get_attachments(skip=skip, limit=limit, filters=filters)

@router.get("/attachments/{attachment_id}", response_model=Attachment)
async def get_attachment_endpoint(attachment_id: int = Path(..., gt=0)):
    """Get an attachment by ID."""
    attachment = get_attachment(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment

@router.delete("/attachments/{attachment_id}", response_model=Dict[str, bool])
async def delete_attachment_endpoint(attachment_id: int = Path(..., gt=0)):
    """Delete an attachment."""
    result = delete_attachment(attachment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return {"success": True}

@router.get("/alerts", response_model=Dict[str, List])
async def get_alerts():
    """
    Get upcoming and overdue obligations.
    """
    upcoming = get_upcoming_obligations()
    overdue = get_overdue_obligations()
    
    return {
        "upcoming": upcoming,
        "overdue": overdue
    }

@router.post("/ai/analyze", response_model=Dict[str, Any])
async def analyze_company_obligations(
    request: Dict[str, Any]
):
    """
    Analyze obligation and payment history for a company using AI.
    """
    company_id = request.get("company_id")
    months = request.get("months", 6)
    language = request.get("language", "es")
    
    if not company_id:
        raise HTTPException(status_code=400, detail="company_id is required")
    
    result = await analyze_obligation_history(company_id, months, language)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
