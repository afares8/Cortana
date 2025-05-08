"""
Script to simulate scraping of obligations for Magnate Spes company.
This is a simulation since we don't have access to actual government APIs.
"""
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.accounting.services import (
    get_company, 
    create_obligation_with_audit, 
    get_obligations,
    get_tax_type
)
from app.accounting.models import Obligation

logger = logging.getLogger(__name__)

async def simulate_obligation_scraping(
    company_id: int,
    user_id: int,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Simulate scraping obligations for a company.
    In a real scenario, this would connect to government websites.
    """
    company = get_company(company_id)
    if not company:
        return {"success": False, "error": "Company not found"}
        
    existing_obligations = get_obligations(filters={"company_id": company_id})
    if len(existing_obligations) >= 5 and not force_refresh:
        return {
            "success": True, 
            "message": "Company already has obligations",
            "obligations": existing_obligations
        }
        
    obligation_templates = [
        {
            "name": "ITBMS Declaration",
            "description": "Monthly value-added tax declaration",
            "tax_type_id": 1,  # Assuming this exists
            "frequency": "monthly",
            "due_day": 15,
            "reminder_days": 10,
            "amount": random.randint(500, 2000),
        },
        {
            "name": "Municipal Tax - Chitré",
            "description": "Quarterly municipal tax for business operation",
            "tax_type_id": 2,  # Assuming this exists
            "frequency": "quarterly",
            "due_day": 10,
            "reminder_days": 15,
            "amount": random.randint(300, 800),
        },
        {
            "name": "CSS Employee Contributions",
            "description": "Monthly social security payment for employees",
            "tax_type_id": 3,  # Assuming this exists
            "frequency": "monthly",
            "due_day": 20,
            "reminder_days": 7,
            "amount": random.randint(1000, 5000),
        },
        {
            "name": "Annual Corporate Tax",
            "description": "Annual income tax declaration",
            "tax_type_id": 1,  # Assuming this exists
            "frequency": "annual",
            "due_month": 3,
            "due_day": 31,
            "reminder_days": 30,
            "amount": random.randint(5000, 15000),
        },
        {
            "name": "Dividend Reporting",
            "description": "Biannual dividend tax reporting",
            "tax_type_id": 1,  # Assuming this exists
            "frequency": "biannual",
            "due_months": [6, 12],
            "due_day": 30,
            "reminder_days": 15,
            "amount": random.randint(1000, 3000),
        },
    ]
    
    today = datetime.utcnow().date()
    created_obligations = []
    
    for template in obligation_templates:
        tax_type = get_tax_type(template["tax_type_id"])
        if not tax_type:
            logger.warning(f"Tax type {template['tax_type_id']} not found, skipping obligation {template['name']}")
            continue
            
        if template["frequency"] == "monthly":
            next_month = today.replace(day=1) + timedelta(days=32)
            next_due = next_month.replace(day=min(template["due_day"], 28))
        elif template["frequency"] == "quarterly":
            month = ((today.month - 1) // 3 + 1) * 3 + 1
            next_quarter = today.replace(month=month if month <= 12 else month-12, day=1)
            if month > 12:
                next_quarter = next_quarter.replace(year=next_quarter.year + 1)
            next_due = next_quarter.replace(day=min(template["due_day"], 28))
        elif template["frequency"] == "annual":
            due_month = template.get("due_month", 3)
            if today.month > due_month or (today.month == due_month and today.day > template["due_day"]):
                next_due = today.replace(year=today.year + 1, month=due_month, day=template["due_day"])
            else:
                next_due = today.replace(month=due_month, day=template["due_day"])
        elif template["frequency"] == "biannual":
            due_months = template.get("due_months", [6, 12])
            next_due_month = None
            for month in sorted(due_months):
                if today.month < month or (today.month == month and today.day <= template["due_day"]):
                    next_due_month = month
                    break
            
            if next_due_month is None:
                next_due_month = due_months[0]
                next_due = today.replace(year=today.year + 1, month=next_due_month, day=template["due_day"])
            else:
                next_due = today.replace(month=next_due_month, day=template["due_day"])
        else:
            next_month = today.replace(day=1) + timedelta(days=32)
            next_due = next_month.replace(day=min(template["due_day"], 28))
            
        obligation_data = {
            "company_id": company_id,
            "tax_type_id": template["tax_type_id"],
            "name": template["name"],
            "description": template["description"],
            "frequency": template["frequency"],
            "due_day": template["due_day"],
            "reminder_days": template["reminder_days"],
            "amount": template["amount"],
            "status": "pending",
            "next_due_date": next_due.isoformat()
        }
        
        obligation = create_obligation_with_audit(obligation_data, user_id)
        if obligation:
            created_obligations.append(obligation)
            
    return {
        "success": True,
        "message": f"Created {len(created_obligations)} obligations for {company.name}",
        "obligations": created_obligations
    }

def get_magnate_spes_company_id() -> Optional[int]:
    """
    Helper function to find the Magnate Spes company ID.
    """
    from app.accounting.services import get_companies
    
    companies = get_companies(filters={"name": "Magnate Spes"})
    if companies and len(companies) > 0:
        return companies[0].id
    return None
