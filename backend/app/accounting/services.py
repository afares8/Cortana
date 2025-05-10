from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import os
import uuid
import json
import base64
from pathlib import Path

from app.db.init_db import users_db
from app.core.config import settings
from app.models.user import UserRole
from app.accounting.models import (
    Company,
    TaxType,
    Obligation,
    Payment,
    Attachment,
    UserCompanyAccess,
    AccessPermission,
    Notification
)
from app.accounting.exports import (
    get_template_file,
    export_obligations_to_excel,
    export_payments_to_excel
)
from app.db.base import InMemoryDB

companies_db = InMemoryDB[Company](Company)
tax_types_db = InMemoryDB[TaxType](TaxType)
obligations_db = InMemoryDB[Obligation](Obligation)
payments_db = InMemoryDB[Payment](Payment)
attachments_db = InMemoryDB[Attachment](Attachment)
notifications_db = InMemoryDB[Notification](Notification)

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
    
    updated_company = companies_db.update(id=company_id, obj_in=Company(**company_data))
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
    
    updated_tax_type = tax_types_db.update(id=tax_type_id, obj_in=TaxType(**tax_type_data))
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
    
    old_status = obligation.status if hasattr(obligation, "status") else None
    new_status = obligation_data.get("status")
    
    updated_obligation = obligations_db.update(id=obligation_id, obj_in=Obligation(**obligation_data))
    updated_obligation = get_obligation(obligation_id)  # Get updated obligation with company and tax type names
    
    if old_status != "overdue" and new_status == "overdue":
        notify_overdue_obligation(updated_obligation)
    
    return updated_obligation

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
    
    obligations_db.update(id=obligation.id, obj_in=Obligation(**{
        "last_payment_date": payment.payment_date,
        "status": "completed"
    }))
    
    notify_payment_registered(payment)
    
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
    
    updated_payment = payments_db.update(id=payment_id, obj_in=Payment(**payment_data))
    
    if "payment_date" in payment_data:
        obligations_db.update(id=payment.obligation_id, obj_in=Obligation(**{
            "last_payment_date": payment_data["payment_date"]
        }))
    
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
            obligations_db.update(id=obligation.id, obj_in=Obligation(**{
                "last_payment_date": None,
                "status": "pending"
            }))
        else:
            latest_payment = max(other_payments, key=lambda p: p.payment_date)
            obligations_db.update(id=obligation.id, obj_in=Obligation(**{
                "last_payment_date": latest_payment.payment_date
            }))
    
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
def get_upcoming_obligations(days: int = 15) -> List[Obligation]:
    """Get obligations that are due within the specified number of days."""
    today = datetime.utcnow().date()
    obligations = get_obligations(filters={"status": "pending"})
    
    upcoming = []
    for obligation in obligations:
        due_date = obligation.next_due_date.date() if isinstance(obligation.next_due_date, datetime) else obligation.next_due_date
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00")).date()
            except:
                continue
        
        days_until_due = (due_date - today).days
        if days_until_due >= 0 and days_until_due <= days:
            upcoming.append(obligation)
    
    return upcoming

def get_overdue_obligations() -> List[Obligation]:
    """Get obligations that are overdue."""
    today = datetime.utcnow().date()
    obligations = get_obligations()
    
    overdue = []
    for obligation in obligations:
        due_date = obligation.next_due_date.date() if isinstance(obligation.next_due_date, datetime) else obligation.next_due_date
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00")).date()
            except:
                continue
        
        if due_date < today and obligation.status == "pending":
            overdue.append(obligation)
    
    return overdue

async def get_obligation_history(company_id: int, months: int = 6) -> Dict[str, Any]:
    """Get obligation and payment history for a company."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)
    
    company = get_company(company_id)
    if not company:
        return {"error": "Company not found"}
    
    company_obligations = get_obligations(filters={"company_id": company_id})
    
    obligation_ids = [o.id for o in company_obligations]
    all_payments = []
    for obligation_id in obligation_ids:
        payments = get_payments(filters={"obligation_id": obligation_id})
        payments = [p for p in payments if p.payment_date >= start_date]
        all_payments.extend(payments)
    
    result = {
        "company": company.dict(),
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "months": months
        },
        "obligations": [o.dict() for o in company_obligations],
        "payments": [p.dict() for p in all_payments]
    }
    
    return result

async def analyze_obligation_history(company_id: int, months: int = 6, language: str = "es") -> Dict[str, Any]:
    """Analyze obligation and payment history using Mistral AI."""
    from app.services.ai.mistral_client import mistral_client
    
    history = await get_obligation_history(company_id, months)
    
    if "error" in history:
        return history
    
    company = history["company"]
    
    if language.lower() == "es":
        prompt = f"""
        Eres un asistente contable. Aquí tienes el historial de obligaciones y pagos de la empresa {company['name']} en los últimos {months} meses:
        
        Información de la empresa:
        Nombre: {company['name']}
        Ubicación: {company['location']}
        Zona Libre: {"Sí" if company['is_zona_libre'] else "No"}
        
        Obligaciones fiscales:
        """
        
        for obligation in history["obligations"]:
            prompt += f"""
            - {obligation['name']} ({obligation['frequency']})
              Estado: {obligation['status']}
              Próximo vencimiento: {obligation['next_due_date']}
            """
        
        prompt += """
        
        Pagos realizados:
        """
        
        for payment in history["payments"]:
            prompt += f"""
            - Obligación ID: {payment['obligation_id']}
              Monto: ${payment['amount']}
              Fecha: {payment['payment_date']}
            """
        
        prompt += """
        
        Analiza la información anterior y responde:
        1. ¿Hay obligaciones vencidas o próximas a vencer que requieran atención inmediata?
        2. ¿Identificas alguna anomalía en los montos o frecuencia de pagos?
        3. ¿Qué recomendaciones darías para mejorar el cumplimiento fiscal?
        """
    else:
        prompt = f"""
        You are an accounting assistant. Here is the obligation and payment history for the company {company['name']} for the last {months} months:
        
        Company Information:
        Name: {company['name']}
        Location: {company['location']}
        Free Zone: {"Yes" if company['is_zona_libre'] else "No"}
        
        Tax Obligations:
        """
        
        for obligation in history["obligations"]:
            prompt += f"""
            - {obligation['name']} ({obligation['frequency']})
              Status: {obligation['status']}
              Next due date: {obligation['next_due_date']}
            """
        
        prompt += """
        
        Payments made:
        """
        
        for payment in history["payments"]:
            prompt += f"""
            - Obligation ID: {payment['obligation_id']}
              Amount: ${payment['amount']}
              Date: {payment['payment_date']}
            """
        
        prompt += """
        
        Analyze the information above and answer:
        1. Are there any overdue or upcoming obligations that require immediate attention?
        2. Do you identify any anomalies in the amounts or frequency of payments?
        3. What recommendations would you give to improve tax compliance?
        """
    
    try:
        analysis = await mistral_client.generate(prompt)
        return {
            "company_id": company_id,
            "analysis": analysis,
            "language": language,
            "prompt": prompt
        }
    except Exception as e:
        return {
            "company_id": company_id,
            "error": str(e),
            "language": language
        }


user_company_access_db = InMemoryDB[UserCompanyAccess](UserCompanyAccess)


def create_user_company_access(data: Dict[str, Any]) -> UserCompanyAccess:
    """Create a new user company access record."""
    try:
        print(f"DEBUG: Creating user company access - user_id={data.get('user_id')}, company_id={data.get('company_id')}, permissions={data.get('permissions')}")
        
        users = users_db.get_multi(filters={"id": data["user_id"]})
        if not users:
            return None
            
        company = get_company(data["company_id"])
        if not company:
            return None
            
        # Get all accesses for this user
        all_accesses = user_company_access_db.get_multi()
        
        # Manually filter by user_id and company_id
        existing_accesses = [
            access for access in all_accesses 
            if access.user_id == data["user_id"] and access.company_id == data["company_id"]
        ]
        
        if existing_accesses:
            existing_access = existing_accesses[0]
            print(f"DEBUG: Found existing access - id={existing_access.id}, permissions={existing_access.permissions}")
            return update_user_company_access(existing_access.id, {"permissions": data["permissions"]})
        
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow()
        
        access = user_company_access_db.create(obj_in=UserCompanyAccess(**data))
        print(f"DEBUG: Created new access - id={access.id}, permissions={access.permissions}")
        return access
    except Exception as e:
        print(f"Error creating user company access: {e}")
        return None


def get_user_company_access(access_id: int) -> Optional[UserCompanyAccess]:
    """Get a user company access by ID."""
    return user_company_access_db.get(access_id)


def get_user_company_accesses(
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[UserCompanyAccess]:
    """Get user company accesses with optional filtering."""
    all_accesses = user_company_access_db.get_multi(skip=skip, limit=limit)
    
    if filters:
        filtered_accesses = []
        for access in all_accesses:
            match = True
            for key, value in filters.items():
                if hasattr(access, key) and getattr(access, key) != value:
                    match = False
                    break
            if match:
                filtered_accesses.append(access)
        accesses = filtered_accesses
    else:
        accesses = all_accesses
    
    for access in accesses:
        users = users_db.get_multi(filters={"id": access.user_id})
        if users:
            user = users[0]
            access.user_email = user.email
            access.user_name = user.full_name
        
        company = get_company(access.company_id)
        if company:
            access.company_name = company.name
    
    return accesses


def update_user_company_access(
    access_id: int, 
    data: Dict[str, Any]
) -> Optional[UserCompanyAccess]:
    """Update a user company access."""
    access = user_company_access_db.get(access_id)
    if not access:
        return None
    
    existing_data = {
        "user_id": access.user_id,
        "company_id": access.company_id,
        "permissions": access.permissions,
        "created_at": access.created_at
    }
    existing_data.update(data)
    
    updated_access = user_company_access_db.update(id=access_id, obj_in=UserCompanyAccess(**existing_data))
    return updated_access


def delete_user_company_access(access_id: int) -> bool:
    """Delete a user company access."""
    access = user_company_access_db.get(access_id)
    if not access:
        return False
    
    result = user_company_access_db.remove(access_id)
    return result


def user_can_access_company(
    user_id: int,
    company_id: int,
    required_permission: str = "read"
) -> bool:
    """Check if a user has access to a company with the required permission level."""
    # If permission bypass is enabled, always return True
    if settings.BYPASS_ACCOUNTING_PERMISSIONS:
        print(f"DEBUG: Bypassing permission check for user_id={user_id}, company_id={company_id}")
        return True
        
    users = users_db.get_multi(filters={"id": user_id})
    if not users:
        return False
    
    user = users[0]
    
    if user.is_superuser or getattr(user, "role", None) == UserRole.ADMIN:
        return True
    
    print(f"DEBUG: Filtering accesses for user_id={user_id}, company_id={company_id}")
    accesses = get_user_company_accesses(filters={
        "user_id": user_id,
        "company_id": company_id
    })
    print(f"DEBUG: Found {len(accesses)} accesses")
    
    if not accesses:
        return False
    
    access = accesses[0]
    print(f"DEBUG: Access found - user_id={user_id}, company_id={company_id}, access.permissions={access.permissions}")
    
    if required_permission == "read":
        return access.permissions in [AccessPermission.READ, AccessPermission.WRITE]
    
    if required_permission == "write":
        if getattr(user, "role", None) == UserRole.VIEWER:
            return False
            
        return access.permissions == AccessPermission.WRITE
    
    return False


# Notification services
def create_notification(notification_data: Dict[str, Any]) -> Notification:
    """Create a new notification."""
    if "created_at" not in notification_data:
        notification_data["created_at"] = datetime.utcnow()
    
    notification = notifications_db.create(obj_in=Notification(**notification_data))
    return notification

def get_notification(notification_id: uuid.UUID) -> Optional[Notification]:
    """Get a notification by ID."""
    all_notifications = notifications_db.get_multi()
    for notification in all_notifications:
        if str(notification.id) == str(notification_id):
            return notification
    return None

def get_notifications(
    skip: int = 0, 
    limit: int = 100, 
    filters: Dict[str, Any] = None
) -> List[Notification]:
    """Get notifications with optional filtering."""
    all_notifications = notifications_db.get_multi(skip=skip, limit=limit)
    
    if not filters:
        return all_notifications
    
    filtered_notifications = []
    for notification in all_notifications:
        match = True
        for key, value in filters.items():
            if hasattr(notification, key) and getattr(notification, key) != value:
                match = False
                break
        if match:
            filtered_notifications.append(notification)
    
    return filtered_notifications

def update_notification(notification_id: uuid.UUID, notification_data: Dict[str, Any]) -> Optional[Notification]:
    """Update a notification."""
    notification = get_notification(notification_id)
    if not notification:
        return None
    
    notification_dict = {
        "id": notification.id,
        "user_id": notification.user_id,
        "message": notification.message,
        "read": notification.read,
        "related_obligation_id": notification.related_obligation_id,
        "created_at": notification.created_at,
        "updated_at": datetime.utcnow()
    }
    notification_dict.update(notification_data)
    
    all_notifications = notifications_db.get_multi()
    for i, notif in enumerate(all_notifications):
        if str(notif.id) == str(notification_id):
            updated_notification = notifications_db.update(
                id=i+1,  # InMemoryDB uses 1-based indexing
                obj_in=Notification(**notification_dict)
            )
            return updated_notification
    
    return None

def mark_notification_read(notification_id: uuid.UUID) -> Optional[Notification]:
    """Mark a notification as read."""
    return update_notification(notification_id, {"read": True})

def notify_upcoming_obligation(obligation: Obligation, days_before: int) -> List[Notification]:
    """Create a notification for an upcoming obligation."""
    company = get_company(obligation.company_id)
    company_name = company.name if company else "Unknown Company"
    message = f"{obligation.name} for {company_name} due in {days_before} days"
    
    all_accesses = user_company_access_db.get_multi()
    user_accesses = [
        access for access in all_accesses 
        if access.company_id == obligation.company_id
    ]
    
    notifications = []
    for access in user_accesses:
        notification_data = {
            "user_id": access.user_id,
            "message": message,
            "related_obligation_id": obligation.id
        }
        notifications.append(create_notification(notification_data))
    
    return notifications

def notify_overdue_obligation(obligation: Obligation) -> List[Notification]:
    """Create a notification for an overdue obligation."""
    company = get_company(obligation.company_id)
    company_name = company.name if company else "Unknown Company"
    message = f"{obligation.name} for {company_name} is overdue"
    
    all_accesses = user_company_access_db.get_multi()
    user_accesses = [
        access for access in all_accesses 
        if access.company_id == obligation.company_id
    ]
    
    notifications = []
    for access in user_accesses:
        notification_data = {
            "user_id": access.user_id,
            "message": message,
            "related_obligation_id": obligation.id
        }
        notifications.append(create_notification(notification_data))
    
    return notifications

def notify_payment_registered(payment: Payment) -> List[Notification]:
    """Create a notification for a registered payment."""
    obligation = get_obligation(payment.obligation_id)
    if not obligation:
        return []
    
    company = get_company(obligation.company_id)
    company_name = company.name if company else "Unknown Company"
    message = f"Payment of ${payment.amount} registered for {obligation.name} ({company_name})"
    
    all_accesses = user_company_access_db.get_multi()
    user_accesses = [
        access for access in all_accesses 
        if access.company_id == obligation.company_id
    ]
    
    notifications = []
    for access in user_accesses:
        notification_data = {
            "user_id": access.user_id,
            "message": message,
            "related_obligation_id": obligation.id
        }
        notifications.append(create_notification(notification_data))
    
    return notifications

from app.accounting.audit import create_audit_log
from app.accounting.models import AuditAction

def create_obligation_with_audit(
    obligation_data: Dict[str, Any],
    user_id: int
) -> Optional[Obligation]:
    """Create a new obligation with audit logging."""
    obligation = create_obligation(obligation_data)
    
    if obligation:
        create_audit_log(
            user_id=user_id,
            action=AuditAction.CREATE,
            entity_type="obligation",
            entity_id=obligation.id,
            metadata={
                "name": obligation.name,
                "company_id": obligation.company_id,
                "tax_type_id": obligation.tax_type_id
            }
        )
    
    return obligation

def update_obligation_with_audit(
    obligation_id: int,
    obligation_data: Dict[str, Any],
    user_id: int
) -> Optional[Obligation]:
    """Update an obligation with audit logging."""
    original_obligation = get_obligation(obligation_id)
    if not original_obligation:
        return None
    
    updated_obligation = update_obligation(obligation_id, obligation_data)
    
    if updated_obligation:
        create_audit_log(
            user_id=user_id,
            action=AuditAction.UPDATE,
            entity_type="obligation",
            entity_id=updated_obligation.id,
            metadata={
                "name": updated_obligation.name,
                "status": updated_obligation.status,
                "changes": {k: v for k, v in obligation_data.items() if v is not None}
            }
        )
    
    return updated_obligation

def delete_obligation_with_audit(
    obligation_id: int,
    user_id: int
) -> bool:
    """Delete an obligation with audit logging."""
    obligation = get_obligation(obligation_id)
    if not obligation:
        return False
    
    result = delete_obligation(obligation_id)
    
    if result:
        create_audit_log(
            user_id=user_id,
            action=AuditAction.DELETE,
            entity_type="obligation",
            entity_id=obligation_id,
            metadata={
                "name": obligation.name,
                "company_id": obligation.company_id,
                "tax_type_id": obligation.tax_type_id
            }
        )
    
    return result

def create_payment_with_audit(
    payment_data: Dict[str, Any],
    user_id: int
) -> Optional[Payment]:
    """Create a new payment with audit logging."""
    payment = create_payment(payment_data)
    
    if payment:
        create_audit_log(
            user_id=user_id,
            action=AuditAction.CREATE,
            entity_type="payment",
            entity_id=payment.id,
            metadata={
                "amount": payment.amount,
                "obligation_id": payment.obligation_id,
                "payment_date": payment.payment_date.isoformat()
            }
        )
    
    return payment

def update_payment_with_audit(
    payment_id: int,
    payment_data: Dict[str, Any],
    user_id: int
) -> Optional[Payment]:
    """Update a payment with audit logging."""
    original_payment = get_payment(payment_id)
    if not original_payment:
        return None
    
    updated_payment = update_payment(payment_id, payment_data)
    
    if updated_payment:
        create_audit_log(
            user_id=user_id,
            action=AuditAction.UPDATE,
            entity_type="payment",
            entity_id=updated_payment.id,
            metadata={
                "amount": updated_payment.amount,
                "obligation_id": updated_payment.obligation_id,
                "changes": {k: v for k, v in payment_data.items() if v is not None}
            }
        )
    
    return updated_payment

def delete_payment_with_audit(
    payment_id: int,
    user_id: int
) -> bool:
    """Delete a payment with audit logging."""
    payment = get_payment(payment_id)
    if not payment:
        return False
    
    result = delete_payment(payment_id)
    
    if result:
        create_audit_log(
            user_id=user_id,
            action=AuditAction.DELETE,
            entity_type="payment",
            entity_id=payment_id,
            metadata={
                "amount": payment.amount,
                "obligation_id": payment.obligation_id
            }
        )
    
    return result

def get_company_audit_logs(
    company_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get audit logs for a specific company."""
    from app.accounting.audit import get_audit_logs, get_entity_audit_logs
    
    company_logs = get_entity_audit_logs("company", company_id, skip, limit)
    
    company_obligations = get_obligations(filters={"company_id": company_id})
    obligation_ids = [obligation.id for obligation in company_obligations]
    
    # Get logs for these obligations
    obligation_logs = []
    for obligation_id in obligation_ids:
        logs = get_entity_audit_logs("obligation", obligation_id, 0, 100)
        obligation_logs.extend(logs)
    
    # Get payments for these obligations
    payment_logs = []
    for obligation_id in obligation_ids:
        payments = get_payments(filters={"obligation_id": obligation_id})
        payment_ids = [payment.id for payment in payments]
        
        for payment_id in payment_ids:
            logs = get_entity_audit_logs("payment", payment_id, 0, 100)
            payment_logs.extend(logs)
    
    all_logs = company_logs + obligation_logs + payment_logs
    
    sorted_logs = sorted(all_logs, key=lambda x: x.timestamp, reverse=True)
    
    paginated_logs = sorted_logs[skip:skip+limit]
    
    return [log.dict() for log in paginated_logs]

def generate_email_draft(obligation_data: dict) -> str:
    """
    Generate a well-formatted email draft in Spanish for an obligation.
    
    Args:
        obligation_data: Dictionary containing obligation details
        
    Returns:
        A formatted email draft string in Spanish
    """
    company_name = obligation_data.get('company_name', 'cliente')
    obligation_name = obligation_data.get('name', 'obligación fiscal')
    due_date = obligation_data.get('next_due_date', '')
    amount = obligation_data.get('amount', '')
    description = obligation_data.get('description', '')
    
    due_date_str = ''
    if due_date:
        if isinstance(due_date, str):
            due_date_str = due_date
        else:
            try:
                due_date_str = due_date.strftime('%d/%m/%Y')
            except:
                due_date_str = str(due_date)
    
    amount_str = ''
    if amount:
        amount_str = f" por un monto de ${amount}"
    
    email_draft = f"""Estimado {company_name},

Nos comunicamos con usted para informarle que su obligación fiscal '{obligation_name}'{amount_str} está próxima a vencer.

Detalles de la obligación:
- Nombre: {obligation_name}
- Descripción: {description}
- Fecha de vencimiento: {due_date_str}

Por favor, asegúrese de realizar el pago correspondiente antes de la fecha de vencimiento para evitar recargos o sanciones.

Si necesita asistencia adicional o tiene alguna pregunta, no dude en contactarnos.

Atentamente,
Equipo de Contabilidad
Cortana
"""
    
    return email_draft
