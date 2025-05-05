from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import os
import uuid
import json
import base64
from pathlib import Path

from app.db.init_db import users_db
from app.core.config import settings
from app.accounting.models import (
    Company,
    TaxType,
    Obligation,
    Payment,
    Attachment
)
from app.db.base import InMemoryDB

companies_db = InMemoryDB[Company](Company)
tax_types_db = InMemoryDB[TaxType](TaxType)
obligations_db = InMemoryDB[Obligation](Obligation)
payments_db = InMemoryDB[Payment](Payment)
attachments_db = InMemoryDB[Attachment](Attachment)

ACCOUNTING_UPLOADS_DIR = Path("uploads/accounting")
ACCOUNTING_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

def create_company(company_data: Dict[str, Any]) -> Company:
    """Create a new company."""
    company = companies_db.create(obj_in=Company(**company_data))
    return company

def get_company(company_id: int) -> Optional[Company]:
    """Get a company by ID."""
    return companies_db.get(company_id)

def get_companies(skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Company]:
    """Get a list of companies with optional filtering."""
    return companies_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_company(company_id: int, company_data: Dict[str, Any]) -> Optional[Company]:
    """Update a company."""
    company = companies_db.get(company_id)
    if not company:
        return None
    
    updated_company = companies_db.update(company_id, company_data)
    return updated_company

def delete_company(company_id: int) -> bool:
    """Delete a company."""
    company = companies_db.get(company_id)
    if not company:
        return False
    
    company_obligations = obligations_db.get_multi(filters={"company_id": company_id})
    if company_obligations:
        return False
    
    result = companies_db.remove(company_id)
    return result

def create_tax_type(tax_type_data: Dict[str, Any]) -> TaxType:
    """Create a new tax type."""
    tax_type = tax_types_db.create(obj_in=TaxType(**tax_type_data))
    return tax_type

def get_tax_type(tax_type_id: int) -> Optional[TaxType]:
    """Get a tax type by ID."""
    return tax_types_db.get(tax_type_id)

def get_tax_types(skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[TaxType]:
    """Get a list of tax types with optional filtering."""
    return tax_types_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_tax_type(tax_type_id: int, tax_type_data: Dict[str, Any]) -> Optional[TaxType]:
    """Update a tax type."""
    tax_type = tax_types_db.get(tax_type_id)
    if not tax_type:
        return None
    
    updated_tax_type = tax_types_db.update(tax_type_id, tax_type_data)
    return updated_tax_type

def delete_tax_type(tax_type_id: int) -> bool:
    """Delete a tax type."""
    tax_type = tax_types_db.get(tax_type_id)
    if not tax_type:
        return False
    
    tax_type_obligations = obligations_db.get_multi(filters={"tax_type_id": tax_type_id})
    if tax_type_obligations:
        return False
    
    result = tax_types_db.remove(tax_type_id)
    return result

def create_obligation(obligation_data: Dict[str, Any]) -> Obligation:
    """Create a new obligation."""
    company = companies_db.get(obligation_data.get("company_id"))
    tax_type = tax_types_db.get(obligation_data.get("tax_type_id"))
    
    if not company or not tax_type:
        return None
    
    obligation = obligations_db.create(obj_in=Obligation(**obligation_data))
    return obligation

def get_obligation(obligation_id: int) -> Optional[Obligation]:
    """Get an obligation by ID with company and tax type names."""
    obligation = obligations_db.get(obligation_id)
    if not obligation:
        return None
    
    company = companies_db.get(obligation.company_id)
    tax_type = tax_types_db.get(obligation.tax_type_id)
    
    if company:
        obligation.company_name = company.name
    
    if tax_type:
        obligation.tax_type_name = tax_type.name
    
    return obligation

def get_obligations(skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Obligation]:
    """Get a list of obligations with optional filtering."""
    obligations = obligations_db.get_multi(skip=skip, limit=limit, filters=filters)
    
    for obligation in obligations:
        company = companies_db.get(obligation.company_id)
        tax_type = tax_types_db.get(obligation.tax_type_id)
        
        if company:
            obligation.company_name = company.name
        
        if tax_type:
            obligation.tax_type_name = tax_type.name
    
    return obligations

def update_obligation(obligation_id: int, obligation_data: Dict[str, Any]) -> Optional[Obligation]:
    """Update an obligation."""
    obligation = obligations_db.get(obligation_id)
    if not obligation:
        return None
    
    if "company_id" in obligation_data:
        company = companies_db.get(obligation_data["company_id"])
        if not company:
            return None
    
    if "tax_type_id" in obligation_data:
        tax_type = tax_types_db.get(obligation_data["tax_type_id"])
        if not tax_type:
            return None
    
    updated_obligation = obligations_db.update(obligation_id, obligation_data)
    return get_obligation(obligation_id)  # Return with company and tax type names

def delete_obligation(obligation_id: int) -> bool:
    """Delete an obligation."""
    obligation = obligations_db.get(obligation_id)
    if not obligation:
        return False
    
    obligation_payments = payments_db.get_multi(filters={"obligation_id": obligation_id})
    for payment in obligation_payments:
        payments_db.remove(payment.id)
    
    result = obligations_db.remove(obligation_id)
    return result

def create_payment(payment_data: Dict[str, Any]) -> Payment:
    """Create a new payment."""
    obligation = obligations_db.get(payment_data.get("obligation_id"))
    if not obligation:
        return None
    
    payment = payments_db.create(obj_in=Payment(**payment_data))
    
    obligations_db.update(obligation.id, {
        "last_payment_date": payment.payment_date,
        "status": "completed"
    })
    
    return payment

def get_payment(payment_id: int) -> Optional[Payment]:
    """Get a payment by ID."""
    return payments_db.get(payment_id)

def get_payments(skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Payment]:
    """Get a list of payments with optional filtering."""
    return payments_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_payment(payment_id: int, payment_data: Dict[str, Any]) -> Optional[Payment]:
    """Update a payment."""
    payment = payments_db.get(payment_id)
    if not payment:
        return None
    
    updated_payment = payments_db.update(payment_id, payment_data)
    
    if "payment_date" in payment_data:
        obligations_db.update(payment.obligation_id, {
            "last_payment_date": payment_data["payment_date"]
        })
    
    return updated_payment

def delete_payment(payment_id: int) -> bool:
    """Delete a payment."""
    payment = payments_db.get(payment_id)
    if not payment:
        return False
    
    result = payments_db.remove(payment_id)
    
    obligation = obligations_db.get(payment.obligation_id)
    if obligation:
        other_payments = payments_db.get_multi(filters={"obligation_id": payment.obligation_id})
        if not other_payments:
            obligations_db.update(obligation.id, {
                "last_payment_date": None,
                "status": "pending"
            })
        else:
            latest_payment = max(other_payments, key=lambda p: p.payment_date)
            obligations_db.update(obligation.id, {
                "last_payment_date": latest_payment.payment_date
            })
    
    return result

def save_attachment_file(file_content: str, file_name: str, file_type: str) -> str:
    """Save an attachment file to disk and return the file path."""
    if not file_content:
        return ""
    
    try:
        file_data = base64.b64decode(file_content)
    except Exception:
        return ""
    
    filename = f"{uuid.uuid4()}_{file_name}"
    file_path = ACCOUNTING_UPLOADS_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    return str(file_path)

def create_attachment(attachment_data: Dict[str, Any]) -> Attachment:
    """Create a new attachment."""
    file_content = attachment_data.pop("file_content", None)
    
    file_path = ""
    if file_content:
        file_path = save_attachment_file(
            file_content, 
            attachment_data.get("file_name", "attachment"), 
            attachment_data.get("file_type", "application/octet-stream")
        )
    
    attachment_dict = {
        **attachment_data, 
        "file_path": file_path,
        "upload_date": datetime.utcnow()
    }
    
    attachment = attachments_db.create(obj_in=Attachment(**attachment_dict))
    return attachment

def get_attachment(attachment_id: int) -> Optional[Attachment]:
    """Get an attachment by ID."""
    return attachments_db.get(attachment_id)

def get_attachments(skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Attachment]:
    """Get a list of attachments with optional filtering."""
    return attachments_db.get_multi(skip=skip, limit=limit, filters=filters)

def delete_attachment(attachment_id: int) -> bool:
    """Delete an attachment."""
    attachment = attachments_db.get(attachment_id)
    if not attachment:
        return False
    
    if attachment.file_path and os.path.exists(attachment.file_path):
        try:
            os.remove(attachment.file_path)
        except Exception:
            pass
    
    result = attachments_db.remove(attachment_id)
    return result

def init_accounting_db():
    """Initialize the accounting database with sample data."""
    if not tax_types_db.get_multi():
        create_tax_type({
            "id": 1,
            "name": "ITBMS",
            "authority": "DGI",
            "description": "Impuesto de Transferencia de Bienes Muebles y Servicios (7% sales tax)",
            "created_at": datetime.utcnow()
        })
        
        create_tax_type({
            "id": 2,
            "name": "ISR",
            "authority": "DGI",
            "description": "Impuesto Sobre la Renta (Income tax)",
            "created_at": datetime.utcnow()
        })
        
        create_tax_type({
            "id": 3,
            "name": "CSS",
            "authority": "CSS",
            "description": "Caja de Seguro Social (Social security contributions)",
            "created_at": datetime.utcnow()
        })
        
        create_tax_type({
            "id": 4,
            "name": "Municipal",
            "authority": "Municipio",
            "description": "Municipal taxes and fees",
            "created_at": datetime.utcnow()
        })
        
        create_tax_type({
            "id": 5,
            "name": "ANIP/ZLC",
            "authority": "ANIP/ZLC",
            "description": "Aviso de Operaciones (0.5% annual tax on declared sales)",
            "created_at": datetime.utcnow()
        })
    
    if not companies_db.get_multi():
        create_company({
            "id": 1,
            "name": "Magnate Spes",
            "location": "Chitré",
            "address": "Calle Principal, Chitré, Herrera",
            "contact_email": "contact@magnatespes.com",
            "contact_phone": "+507 123-4567",
            "is_zona_libre": False,
            "notes": "Regular business subject to standard DGI and municipal obligations",
            "created_at": datetime.utcnow()
        })
        
        create_company({
            "id": 2,
            "name": "Magnate Maximus",
            "location": "Zona Libre de Colón",
            "address": "Zona Libre de Colón, Colón",
            "contact_email": "contact@magnatemaximus.com",
            "contact_phone": "+507 765-4321",
            "is_zona_libre": True,
            "notes": "Operates in Zona Libre de Colón with special tax exemptions",
            "created_at": datetime.utcnow()
        })
        
        create_company({
            "id": 3,
            "name": "Parfums El Magnate",
            "location": "Zona Libre de Colón",
            "address": "Zona Libre de Colón, Colón",
            "contact_email": "contact@parfumsmagnate.com",
            "contact_phone": "+507 987-6543",
            "is_zona_libre": True,
            "notes": "Operates in Zona Libre de Colón with special tax exemptions",
            "created_at": datetime.utcnow()
        })
    
    if not obligations_db.get_multi():
        create_obligation({
            "id": 1,
            "company_id": 1,
            "tax_type_id": 1,  # ITBMS
            "name": "Monthly ITBMS Declaration",
            "description": "Monthly 7% sales tax declaration",
            "frequency": "monthly",
            "due_day": 15,  # Due on the 15th of each month
            "reminder_days": 7,
            "status": "pending",
            "next_due_date": datetime.utcnow().replace(day=15) + timedelta(days=30),
            "created_at": datetime.utcnow()
        })
        
        create_obligation({
            "id": 2,
            "company_id": 1,
            "tax_type_id": 2,  # ISR
            "name": "Annual Income Tax Declaration",
            "description": "Annual income tax declaration",
            "frequency": "annual",
            "due_day": 31,  # Due on March 31st
            "reminder_days": 30,
            "status": "pending",
            "next_due_date": datetime(datetime.utcnow().year + 1, 3, 31),
            "created_at": datetime.utcnow()
        })
        
        create_obligation({
            "id": 3,
            "company_id": 1,
            "tax_type_id": 3,  # CSS
            "name": "Monthly CSS Planilla",
            "description": "Monthly social security contributions (M-02)",
            "frequency": "monthly",
            "due_day": 20,  # Due on the 20th of each month
            "reminder_days": 7,
            "status": "pending",
            "next_due_date": datetime.utcnow().replace(day=20) + timedelta(days=30),
            "created_at": datetime.utcnow()
        })
        
        create_obligation({
            "id": 4,
            "company_id": 1,
            "tax_type_id": 4,  # Municipal
            "name": "Municipal License Renewal",
            "description": "Annual municipal license renewal",
            "frequency": "annual",
            "due_day": 31,  # Due on January 31st
            "reminder_days": 30,
            "status": "pending",
            "next_due_date": datetime(datetime.utcnow().year + 1, 1, 31),
            "created_at": datetime.utcnow()
        })
        
        create_obligation({
            "id": 5,
            "company_id": 2,
            "tax_type_id": 5,  # ANIP/ZLC
            "name": "Annual Aviso de Operaciones",
            "description": "Annual 0.5% tax on declared sales",
            "frequency": "annual",
            "due_day": 31,  # Due on December 31st
            "reminder_days": 30,
            "status": "pending",
            "next_due_date": datetime(datetime.utcnow().year, 12, 31),
            "created_at": datetime.utcnow()
        })
        
        create_obligation({
            "id": 6,
            "company_id": 2,
            "tax_type_id": 3,  # CSS
            "name": "Monthly CSS Planilla",
            "description": "Monthly social security contributions (M-02)",
            "frequency": "monthly",
            "due_day": 20,  # Due on the 20th of each month
            "reminder_days": 7,
            "status": "pending",
            "next_due_date": datetime.utcnow().replace(day=20) + timedelta(days=30),
            "created_at": datetime.utcnow()
        })
        
        create_obligation({
            "id": 7,
            "company_id": 3,
            "tax_type_id": 5,  # ANIP/ZLC
            "name": "Annual Aviso de Operaciones",
            "description": "Annual 0.5% tax on declared sales",
            "frequency": "annual",
            "due_day": 31,  # Due on December 31st
            "reminder_days": 30,
            "status": "pending",
            "next_due_date": datetime(datetime.utcnow().year, 12, 31),
            "created_at": datetime.utcnow()
        })
        
        create_obligation({
            "id": 8,
            "company_id": 3,
            "tax_type_id": 3,  # CSS
            "name": "Monthly CSS Planilla",
            "description": "Monthly social security contributions (M-02)",
            "frequency": "monthly",
            "due_day": 20,  # Due on the 20th of each month
            "reminder_days": 7,
            "status": "pending",
            "next_due_date": datetime.utcnow().replace(day=20) + timedelta(days=30),
            "created_at": datetime.utcnow()
        })
