from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body, Query, Path
from fastapi.responses import JSONResponse, FileResponse
from pydantic import EmailStr

from app.core.config import settings
from app.accounting.dependencies import (
    get_current_user,
    company_read_permission,
    company_write_permission,
    admin_only
)
from app.models.user import User
from app.accounting.schemas import (
    Company, CompanyCreate, CompanyUpdate,
    # … demás esquemas …
)
from app.accounting.services import (
    create_company, get_company, get_companies, update_company, delete_company,
    # … demás servicios …
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
    filters: Dict[str, Any] = {}
    if name:
        filters["name"] = name
    if location:
        filters["location"] = location
    if is_zona_libre is not None:
        filters["is_zona_libre"] = is_zona_libre

    return get_companies(skip=skip, limit=limit, filters=filters)

@router.get("/companies/{company_id}", response_model=Company)
async def get_company_endpoint(
    company_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
):
    """Get a company by ID."""
    # Verifica permisos de lectura
    await company_read_permission(company_id)(current_user)

    company = get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/companies/{company_id}", response_model=Company)
async def update_company_endpoint(
    company_id: int = Path(..., gt=0),
    company_update: CompanyUpdate = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Update a company."""
    # Verifica permisos de escritura
    await company_write_permission(company_id)(current_user)

    company = update_company(company_id, company_update.model_dump(exclude_unset=True))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.delete("/companies/{company_id}", response_model=Dict[str, bool])
async def delete_company_endpoint(
    company_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
):
    """Delete a company."""
    # Verifica permisos de escritura
    await company_write_permission(company_id)(current_user)

    success = delete_company(company_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Company not found or has associated obligations"
        )
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
async def create_obligation_endpoint(
    obligation: ObligationCreate,
    current_user: Optional[User] = None
):
    """Create a new obligation."""
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    result = create_obligation_with_audit(
        obligation_data=obligation.model_dump(),
        user_id=user_id
    )
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
    obligation_update: ObligationUpdate = Body(...),
    current_user: Optional[User] = None
):
    """Update an obligation."""
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    obligation = update_obligation_with_audit(
        obligation_id=obligation_id, 
        obligation_data=obligation_update.model_dump(exclude_unset=True),
        user_id=user_id
    )
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return obligation

@router.delete("/obligations/{obligation_id}", response_model=Dict[str, bool])
async def delete_obligation_endpoint(
    obligation_id: int = Path(..., gt=0),
    current_user: Optional[User] = None
):
    """Delete an obligation."""
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    result = delete_obligation_with_audit(
        obligation_id=obligation_id,
        user_id=user_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return {"success": True}

@router.post("/payments", response_model=Payment, status_code=201)
async def create_payment_endpoint(
    payment: PaymentCreate,
    current_user: Optional[User] = None
):
    """Create a new payment."""
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    result = create_payment_with_audit(
        payment_data=payment.model_dump(),
        user_id=user_id
    )
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
    payment_update: PaymentUpdate = Body(...),
    current_user: Optional[User] = None
):
    """Update a payment."""
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    payment = update_payment_with_audit(
        payment_id=payment_id, 
        payment_data=payment_update.model_dump(exclude_unset=True),
        user_id=user_id
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/payments/{payment_id}", response_model=Dict[str, bool])
async def delete_payment_endpoint(
    payment_id: int = Path(..., gt=0),
    current_user: Optional[User] = None
):
    """Delete a payment."""
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    result = delete_payment_with_audit(
        payment_id=payment_id,
        user_id=user_id
    )
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

@router.post("/ai/email-draft", response_model=Dict[str, Any])
async def generate_email_draft_endpoint(
    request: Dict[str, Any]
):
    """
    Generate an email draft using Mistral AI.
    
    Request body:
    {
        "company_id": int,
        "recipient": str,  # "CSS", "DGI", "Municipio", etc.
        "context": str,    # "Declaración fuera de tiempo de la planilla de abril"
        "obligation_id": Optional[int],
        "payment_id": Optional[int],
        "language": Optional[str]  # defaults to "es"
    }
    """
    from app.accounting.email_drafts import generate_email_draft
    
    company_id = request.get("company_id")
    recipient = request.get("recipient")
    context = request.get("context")
    obligation_id = request.get("obligation_id")
    payment_id = request.get("payment_id")
    language = request.get("language", "es")
    
    if not company_id:
        raise HTTPException(status_code=400, detail="company_id is required")
    if not recipient:
        raise HTTPException(status_code=400, detail="recipient is required")
    if not context:
        raise HTTPException(status_code=400, detail="context is required")
    
    result = await generate_email_draft(
        company_id=company_id,
        recipient=recipient,
        context=context,
        obligation_id=obligation_id,
        payment_id=payment_id,
        language=language
    )
    
    if "error" in result:
        return result  # Return error but don't raise exception to allow fallback
    
    return result

@router.get("/templates/{template_name}", response_class=FileResponse)
async def get_template_file_endpoint(template_name: str = Path(...)):
    """
    Get a template file by name.
    """
    file_path = get_template_file(template_name)
    if not file_path:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return FileResponse(
        file_path, 
        filename=f"{template_name}.pdf",
        media_type="application/pdf"
    )

@router.get("/forms/{template_name}", response_class=FileResponse)
async def generate_form_endpoint(
    template_name: str = Path(...),
    company_id: int = Query(..., description="ID of the company"),
    period: Optional[str] = Query(None, description="Period in YYYY-MM format")
):
    """
    Generate a form from a template.
    
    Args:
        template_name: Name of the template
        company_id: ID of the company
        period: Optional period in YYYY-MM format
    """
    from app.accounting.document_generator import document_generator
    
    output_path = document_generator.generate_form(template_name, company_id, period)
    
    if not output_path:
        raise HTTPException(status_code=404, detail="Failed to generate form")
    
    _, ext = os.path.splitext(output_path)
    if ext.lower() == '.pdf':
        media_type = "application/pdf"
    elif ext.lower() == '.docx':
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        output_path,
        filename=os.path.basename(output_path),
        media_type=media_type
    )

@router.get("/reports/obligations", response_model=Dict[str, Any])
async def export_obligations_endpoint(
    company_id: Optional[int] = None,
    month: Optional[str] = None,
    status: Optional[str] = None,
    format: Optional[str] = None
):
    """
    Export obligations data.
    
    Args:
        company_id: Optional filter by company
        month: Optional filter by month (YYYY-MM format)
        status: Optional filter by status
        format: Export format ('excel' or default JSON)
    """
    if format == "excel":
        file_path = await export_obligations_to_excel(company_id, month, status)
        if not file_path:
            raise HTTPException(status_code=404, detail="No data found for export")
        
        return FileResponse(
            file_path,
            filename=os.path.basename(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    filters = {}
    if company_id:
        filters["company_id"] = company_id
    if status:
        filters["status"] = status
    
    obligations = get_obligations(filters=filters)
    
    if month:
        try:
            month_date = datetime.strptime(month, "%Y-%m")
            month_start = month_date.replace(day=1)
            if month_date.month == 12:
                month_end = datetime(month_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(month_date.year, month_date.month + 1, 1) - timedelta(days=1)
                
            filtered_obligations = []
            for obligation in obligations:
                if isinstance(obligation.next_due_date, str):
                    due_date = datetime.fromisoformat(obligation.next_due_date.replace("Z", "+00:00"))
                else:
                    due_date = obligation.next_due_date
                    
                if month_start <= due_date <= month_end:
                    filtered_obligations.append(obligation)
            
            obligations = filtered_obligations
        except ValueError:
            pass
    
    return {"obligations": obligations}

@router.get("/reports/payments", response_model=Dict[str, Any])
async def export_payments_endpoint(
    company_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    format: Optional[str] = None
):
    """
    Export payments data.
    
    Args:
        company_id: Optional filter by company
        from_date: Optional filter by start date (YYYY-MM-DD format)
        to_date: Optional filter by end date (YYYY-MM-DD format)
        format: Export format ('excel' or default JSON)
    """
    if format == "excel":
        file_path = await export_payments_to_excel(company_id, from_date, to_date)
        if not file_path:
            raise HTTPException(status_code=404, detail="No data found for export")
        
        return FileResponse(
            file_path,
            filename=os.path.basename(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    all_payments = get_payments()
    filtered_payments = []
    
    for payment in all_payments: 
        obligation = get_obligation(payment.obligation_id)
        if not obligation:
            continue
            
        if company_id and obligation.company_id != company_id:
            continue
        
        payment_date = payment.payment_date
        if isinstance(payment_date, str):
            payment_date = datetime.fromisoformat(payment_date.replace("Z", "+00:00"))
            
        if from_date:
            try:
                from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
                if payment_date < from_datetime:
                    continue
            except ValueError:
                pass
                
        if to_date:
            try:
                to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
                if payment_date > to_datetime:
                    continue
            except ValueError:
                pass
                
        filtered_payments.append(payment)
    
    return {"payments": filtered_payments}


@router.post("/user-company-access", response_model=Dict[str, Any], status_code=201)
async def create_user_company_access_endpoint(
    data: Dict[str, Any] = Body(...),
    current_user: Optional[User] = None
):
    """
    Create a new user company access record.
    """
    from app.accounting.services import create_user_company_access
    
    result = create_user_company_access(data)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid user or company")
    
    return result.dict()

@router.get("/user-company-access", response_model=List[Dict[str, Any]])
async def get_user_company_accesses_endpoint(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    company_id: Optional[int] = None,
    current_user: Optional[User] = None
):
    """
    Get user company accesses with optional filtering.
    """
    from app.accounting.services import get_user_company_accesses
    
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if company_id:
        filters["company_id"] = company_id
    
    accesses = get_user_company_accesses(skip=skip, limit=limit, filters=filters)
    return [access.dict() for access in accesses]

@router.put("/user-company-access/{access_id}", response_model=Dict[str, Any])
async def update_user_company_access_endpoint(
    access_id: int = Path(..., gt=0),
    data: Dict[str, Any] = Body(...),
    current_user: Optional[User] = None
):
    """
    Update a user company access.
    """
    from app.accounting.services import update_user_company_access
    
    result = update_user_company_access(access_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="User company access not found")
    
    return result.dict()

@router.delete("/user-company-access/{access_id}", response_model=Dict[str, bool])
async def delete_user_company_access_endpoint(
    access_id: int = Path(..., gt=0),
    current_user: Optional[User] = None
):
    """
    Delete a user company access.
    """
    from app.accounting.services import delete_user_company_access
    
    result = delete_user_company_access(access_id)
    if not result:
        raise HTTPException(status_code=404, detail="User company access not found")
    
    return {"success": True}

@router.get("/users/me/companies", response_model=List[Dict[str, Any]])
async def get_my_companies_endpoint(
    current_user: Optional[User] = None
):
    """
    Get companies accessible to the current user.
    """
    from app.accounting.services import get_user_company_accesses, get_companies, get_company
    
    if current_user is None or current_user.is_superuser or getattr(current_user, "role", None) == "admin":
        companies = get_companies()
        return [company.dict() for company in companies]
    
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    accesses = get_user_company_accesses(filters={"user_id": user_id})
    company_ids = [access.company_id for access in accesses]
    
    companies = []
    for company_id in company_ids:
        company = get_company(company_id)
        if company:
            companies.append(company)
    
    return [company.dict() for company in companies]
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications_endpoint(
    skip: int = 0,
    limit: int = 100,
    read: Optional[bool] = None,
    current_user: Optional[User] = None
):
    """Get notifications for the current user."""
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    filters = {"user_id": user_id}
    if read is not None:
        filters["read"] = read
    
    return get_notifications(skip=skip, limit=limit, filters=filters)


@router.post("/notifications/{notification_id}/mark-read", response_model=NotificationResponse)
async def mark_notification_read_endpoint(
    notification_id: uuid.UUID,
    current_user: Optional[User] = None
):
    """Mark a notification as read."""
    notification = get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    user_id = current_user.id if current_user else 1  # Default to user_id 1 if no user provided
    
    if current_user and notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this notification")
    
    return mark_notification_read(notification_id)

@router.get("/audit", response_model=List[Dict[str, Any]])
async def get_audit_logs_endpoint(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    current_user: Optional[User] = None
):
    """Get audit logs with optional filtering."""
    from app.accounting.audit import get_audit_logs, get_company_audit_logs
    
    if company_id:
        company = get_company(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        audit_logs = get_company_audit_logs(company_id, skip, limit)
    else:
        filters = {}
        if entity_type:
            filters["entity_type"] = entity_type
            
        audit_logs = get_audit_logs(skip, limit, filters)
    
    return [log.dict() for log in audit_logs]
