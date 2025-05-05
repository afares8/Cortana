import pytest
from datetime import datetime, timedelta
from app.accounting.services import (
    create_company, create_tax_type, create_obligation,
    companies_db, tax_types_db, obligations_db
)

def setup_function():
    """Setup test data before each test."""
    companies_db.data = {}
    tax_types_db.data = {}
    obligations_db.data = {}
    
    companies_db.counter = 1
    tax_types_db.counter = 1
    obligations_db.counter = 1
    
    create_company({
        "id": 1,
        "name": "Test Company",
        "location": "Test Location",
        "contact_email": "test@example.com",
        "is_zona_libre": False,
        "created_at": datetime.utcnow()
    })
    
    create_tax_type({
        "id": 1,
        "name": "Test Tax",
        "authority": "Test Authority",
        "description": "Test Description",
        "created_at": datetime.utcnow()
    })

def test_create_obligation_success():
    """Test successful creation of an obligation."""
    setup_function()
    
    next_due_date = datetime.utcnow() + timedelta(days=30)
    obligation_data = {
        "id": 1,
        "company_id": 1,
        "tax_type_id": 1,
        "name": "Test Obligation",
        "description": "Test Description",
        "frequency": "monthly",
        "due_day": 15,
        "reminder_days": 7,
        "status": "pending",
        "next_due_date": next_due_date,
        "created_at": datetime.utcnow()
    }
    
    obligation = create_obligation(obligation_data)
    
    assert obligation is not None
    assert obligation.id == 1
    assert obligation.company_id == 1
    assert obligation.tax_type_id == 1
    assert obligation.name == "Test Obligation"
    assert obligation.frequency == "monthly"
    assert obligation.due_day == 15
    assert obligation.status == "pending"
    assert obligation.next_due_date == next_due_date

def test_create_obligation_invalid_company():
    """Test creation of an obligation with invalid company_id."""
    setup_function()
    
    obligation_data = {
        "id": 1,
        "company_id": 999,  # Non-existent company
        "tax_type_id": 1,
        "name": "Test Obligation",
        "description": "Test Description",
        "frequency": "monthly",
        "due_day": 15,
        "reminder_days": 7,
        "status": "pending",
        "next_due_date": datetime.utcnow() + timedelta(days=30),
        "created_at": datetime.utcnow()
    }
    
    obligation = create_obligation(obligation_data)
    
    assert obligation is None

def test_create_obligation_invalid_tax_type():
    """Test creation of an obligation with invalid tax_type_id."""
    setup_function()
    
    obligation_data = {
        "id": 1,
        "company_id": 1,
        "tax_type_id": 999,  # Non-existent tax type
        "name": "Test Obligation",
        "description": "Test Description",
        "frequency": "monthly",
        "due_day": 15,
        "reminder_days": 7,
        "status": "pending",
        "next_due_date": datetime.utcnow() + timedelta(days=30),
        "created_at": datetime.utcnow()
    }
    
    obligation = create_obligation(obligation_data)
    
    assert obligation is None

def test_create_obligation_with_different_frequencies():
    """Test creation of obligations with different frequencies."""
    setup_function()
    
    monthly_obligation = create_obligation({
        "id": 1,
        "company_id": 1,
        "tax_type_id": 1,
        "name": "Monthly Obligation",
        "frequency": "monthly",
        "due_day": 15,
        "next_due_date": datetime.utcnow().replace(day=15) + timedelta(days=30),
        "created_at": datetime.utcnow()
    })
    
    quarterly_obligation = create_obligation({
        "id": 2,
        "company_id": 1,
        "tax_type_id": 1,
        "name": "Quarterly Obligation",
        "frequency": "quarterly",
        "due_day": 20,
        "next_due_date": datetime.utcnow().replace(day=20) + timedelta(days=90),
        "created_at": datetime.utcnow()
    })
    
    annual_obligation = create_obligation({
        "id": 3,
        "company_id": 1,
        "tax_type_id": 1,
        "name": "Annual Obligation",
        "frequency": "annual",
        "due_day": 31,
        "next_due_date": datetime(datetime.utcnow().year + 1, 3, 31),
        "created_at": datetime.utcnow()
    })
    
    assert monthly_obligation is not None
    assert monthly_obligation.frequency == "monthly"
    
    assert quarterly_obligation is not None
    assert quarterly_obligation.frequency == "quarterly"
    
    assert annual_obligation is not None
    assert annual_obligation.frequency == "annual"

def test_create_obligation_for_zona_libre_company():
    """Test creation of obligations for a Zona Libre company."""
    setup_function()
    
    create_company({
        "id": 2,
        "name": "Zona Libre Company",
        "location": "Zona Libre de Colón",
        "is_zona_libre": True,
        "created_at": datetime.utcnow()
    })
    
    create_tax_type({
        "id": 2,
        "name": "ANIP/ZLC",
        "authority": "ANIP/ZLC",
        "description": "Aviso de Operaciones (0.5% annual tax)",
        "created_at": datetime.utcnow()
    })
    
    obligation_data = {
        "id": 1,
        "company_id": 2,
        "tax_type_id": 2,
        "name": "Annual Aviso de Operaciones",
        "description": "Annual 0.5% tax on declared sales",
        "frequency": "annual",
        "due_day": 31,
        "reminder_days": 30,
        "status": "pending",
        "next_due_date": datetime(datetime.utcnow().year, 12, 31),
        "created_at": datetime.utcnow()
    }
    
    obligation = create_obligation(obligation_data)
    
    assert obligation is not None
    assert obligation.company_id == 2
    assert obligation.tax_type_id == 2
    assert obligation.frequency == "annual"
