import pytest
from datetime import datetime, timedelta
from app.accounting.services import (
    create_company, create_tax_type, create_obligation,
    get_upcoming_obligations, get_overdue_obligations,
    get_companies, get_tax_types,
    companies_db, tax_types_db, obligations_db
)

@pytest.fixture(autouse=True)
def setup_test_data():
    """Set up test data for each test."""
    companies_db.data.clear()
    tax_types_db.data.clear()
    obligations_db.data.clear()
    
    company = create_company({
        "name": "Test Company",
        "location": "Test Location",
        "is_zona_libre": False,
        "created_at": datetime.utcnow()
    })
    print(f"Created company: {company}")
    
    tax_type = create_tax_type({
        "name": "Test Tax",
        "authority": "Test Authority",
        "created_at": datetime.utcnow()
    })
    print(f"Created tax type: {tax_type}")
    
    yield
    
    companies_db.data.clear()
    tax_types_db.data.clear()
    obligations_db.data.clear()

def test_get_upcoming_obligations():
    """Test get_upcoming_obligations function."""
    today = datetime.utcnow().date()
    
    companies = get_companies()
    tax_types = get_tax_types()
    
    print(f"Available companies: {companies}")
    print(f"Available tax types: {tax_types}")
    
    if not companies or not tax_types:
        pytest.fail("Test setup failed: No companies or tax types available")
    
    company_id = companies[0].id
    tax_type_id = tax_types[0].id
    
    upcoming_obligation = create_obligation({
        "company_id": company_id,
        "tax_type_id": tax_type_id,
        "name": "Upcoming Obligation",
        "frequency": "monthly",
        "due_day": 15,
        "reminder_days": 7,
        "status": "pending",
        "next_due_date": today + timedelta(days=5),
        "created_at": datetime.utcnow()
    })
    
    print(f"Created upcoming obligation: {upcoming_obligation}")
    
    not_upcoming_obligation = create_obligation({
        "company_id": company_id,
        "tax_type_id": tax_type_id,
        "name": "Not Yet Upcoming",
        "frequency": "monthly",
        "due_day": 20,
        "reminder_days": 5,
        "status": "pending",
        "next_due_date": today + timedelta(days=10),
        "created_at": datetime.utcnow()
    })
    
    print(f"Created not upcoming obligation: {not_upcoming_obligation}")
    
    completed_obligation = create_obligation({
        "company_id": company_id,
        "tax_type_id": tax_type_id,
        "name": "Completed Obligation",
        "frequency": "monthly",
        "due_day": 10,
        "reminder_days": 7,
        "status": "completed",
        "next_due_date": today + timedelta(days=3),
        "created_at": datetime.utcnow()
    })
    
    print(f"Created completed obligation: {completed_obligation}")
    
    upcoming = get_upcoming_obligations()
    print(f"Upcoming obligations: {upcoming}")
    
    assert len(upcoming) == 1
    assert upcoming[0].name == "Upcoming Obligation"

def test_get_overdue_obligations():
    """Test get_overdue_obligations function."""
    today = datetime.utcnow().date()
    
    companies = get_companies()
    tax_types = get_tax_types()
    
    print(f"Available companies: {companies}")
    print(f"Available tax types: {tax_types}")
    
    if not companies or not tax_types:
        pytest.fail("Test setup failed: No companies or tax types available")
    
    company_id = companies[0].id
    tax_type_id = tax_types[0].id
    
    obligation = create_obligation({
        "company_id": company_id,
        "tax_type_id": tax_type_id,
        "name": "Overdue Obligation",
        "frequency": "monthly",
        "due_day": 15,
        "reminder_days": 7,
        "status": "overdue",  # Set directly to overdue
        "next_due_date": today - timedelta(days=5),
        "created_at": datetime.utcnow()
    })
    
    print(f"Created obligation: {obligation}")
    
    if not obligation:
        pytest.fail("Failed to create obligation")
    
    pending_obligation = create_obligation({
        "company_id": company_id,
        "tax_type_id": tax_type_id,
        "name": "Pending Obligation",
        "frequency": "monthly",
        "due_day": 20,
        "reminder_days": 5,
        "status": "pending",
        "next_due_date": today + timedelta(days=10),
        "created_at": datetime.utcnow()
    })
    
    print(f"Created pending obligation: {pending_obligation}")
    
    overdue = get_overdue_obligations()
    print(f"Overdue obligations: {overdue}")
    
    assert len(overdue) == 1
    assert overdue[0].name == "Overdue Obligation"
