import pytest
from datetime import datetime
from app.accounting.services import (
    create_company, create_tax_type, create_obligation,
    user_can_access_company, create_user_company_access,
    companies_db, tax_types_db, obligations_db, user_company_access_db
)
from app.accounting.models import AccessPermission
from app.models.user import UserRole

@pytest.fixture(autouse=True)
def setup_test_data():
    """Set up test data for each test."""
    companies_db.data.clear()
    tax_types_db.data.clear()
    obligations_db.data.clear()
    user_company_access_db.data.clear()
    
    company = create_company({
        "name": "Test Company",
        "location": "Test Location",
        "is_zona_libre": False,
        "created_at": datetime.utcnow()
    })
    
    company2 = create_company({
        "name": "Another Company",
        "location": "Another Location",
        "is_zona_libre": True,
        "created_at": datetime.utcnow()
    })
    
    yield
    
    companies_db.data.clear()
    tax_types_db.data.clear()
    obligations_db.data.clear()
    user_company_access_db.data.clear()

def test_user_company_access_creation():
    """Test creating user company access."""
    from app.db.init_db import users_db
    
    class MockUser:
        def __init__(self, id, role):
            self.id = id
            self.role = role
            self.is_superuser = False
            self.email = f"user{id}@example.com"
            self.full_name = f"User {id}"
    
    admin_user = MockUser(1, UserRole.ADMIN)
    accountant_user = MockUser(2, UserRole.ACCOUNTANT)
    viewer_user = MockUser(3, UserRole.VIEWER)
    
    original_get_multi = users_db.get_multi
    
    def mock_get_multi(skip=0, limit=100, filters=None):
        if filters and "id" in filters:
            user_id = filters["id"]
            if user_id == 1:
                return [admin_user]
            elif user_id == 2:
                return [accountant_user]
            elif user_id == 3:
                return [viewer_user]
        return []
    
    users_db.get_multi = mock_get_multi
    
    try:
        companies = companies_db.get_multi()
        company = companies[0]
        
        admin_access = create_user_company_access({
            "user_id": 1,
            "company_id": company.id,
            "permissions": AccessPermission.WRITE
        })
        
        assert admin_access is not None
        assert admin_access.user_id == 1
        assert admin_access.company_id == company.id
        assert admin_access.permissions == AccessPermission.WRITE
        
        assert user_can_access_company(1, company.id, "read") is True
        assert user_can_access_company(1, company.id, "write") is True
        
        accountant_access = create_user_company_access({
            "user_id": 2,
            "company_id": company.id,
            "permissions": AccessPermission.READ
        })
        
        assert accountant_access is not None
        assert user_can_access_company(2, company.id, "read") is True
        assert user_can_access_company(2, company.id, "write") is False
        
        viewer_access = create_user_company_access({
            "user_id": 3,
            "company_id": company.id,
            "permissions": AccessPermission.READ
        })
        
        assert viewer_access is not None
        assert user_can_access_company(3, company.id, "read") is True
        assert user_can_access_company(3, company.id, "write") is False
    finally:
        users_db.get_multi = original_get_multi

def test_admin_role_access():
    """Test that admin users have full access to all companies."""
    from app.db.init_db import users_db
    
    class MockUser:
        def __init__(self, id, role):
            self.id = id
            self.role = role
            self.is_superuser = False
            self.email = f"user{id}@example.com"
            self.full_name = f"User {id}"
    
    admin_user = MockUser(1, UserRole.ADMIN)
    
    original_get_multi = users_db.get_multi
    
    def mock_get_multi(skip=0, limit=100, filters=None):
        if filters and "id" in filters:
            user_id = filters["id"]
            if user_id == 1:
                return [admin_user]
        return []
    
    users_db.get_multi = mock_get_multi
    
    try:
        companies = companies_db.get_multi()
        
        for company in companies:
            assert user_can_access_company(1, company.id, "read") is True
            assert user_can_access_company(1, company.id, "write") is True
    finally:
        users_db.get_multi = original_get_multi

def test_accountant_role_access():
    """Test that accountants have access only to assigned companies."""
    from app.db.init_db import users_db
    
    class MockUser:
        def __init__(self, id, role):
            self.id = id
            self.role = role
            self.is_superuser = False
            self.email = f"user{id}@example.com"
            self.full_name = f"User {id}"
    
    accountant_user = MockUser(2, UserRole.ACCOUNTANT)
    
    original_get_multi = users_db.get_multi
    
    def mock_get_multi(skip=0, limit=100, filters=None):
        if filters and "id" in filters:
            user_id = filters["id"]
            if user_id == 2:
                return [accountant_user]
        return []
    
    users_db.get_multi = mock_get_multi
    
    try:
        companies = companies_db.get_multi()
        
        for company in companies:
            assert user_can_access_company(2, company.id, "read") is False
            assert user_can_access_company(2, company.id, "write") is False
        
        first_company = companies[0]
        create_user_company_access({
            "user_id": 2,
            "company_id": first_company.id,
            "permissions": AccessPermission.READ
        })
        
        second_company = companies[1]
        create_user_company_access({
            "user_id": 2,
            "company_id": second_company.id,
            "permissions": AccessPermission.WRITE
        })
        
        assert user_can_access_company(2, first_company.id, "read") is True
        assert user_can_access_company(2, first_company.id, "write") is False
        
        assert user_can_access_company(2, second_company.id, "read") is True
        assert user_can_access_company(2, second_company.id, "write") is True
    finally:
        users_db.get_multi = original_get_multi

def test_viewer_role_access():
    """Test that viewers have read-only access to assigned companies."""
    from app.db.init_db import users_db
    
    class MockUser:
        def __init__(self, id, role):
            self.id = id
            self.role = role
            self.is_superuser = False
            self.email = f"user{id}@example.com"
            self.full_name = f"User {id}"
    
    viewer_user = MockUser(3, UserRole.VIEWER)
    
    original_get_multi = users_db.get_multi
    
    def mock_get_multi(skip=0, limit=100, filters=None):
        if filters and "id" in filters:
            user_id = filters["id"]
            if user_id == 3:
                return [viewer_user]
        return []
    
    users_db.get_multi = mock_get_multi
    
    try:
        companies = companies_db.get_multi()
        
        for company in companies:
            assert user_can_access_company(3, company.id, "read") is False
            assert user_can_access_company(3, company.id, "write") is False
        
        first_company = companies[0]
        create_user_company_access({
            "user_id": 3,
            "company_id": first_company.id,
            "permissions": AccessPermission.READ
        })
        
        second_company = companies[1]
        create_user_company_access({
            "user_id": 3,
            "company_id": second_company.id,
            "permissions": AccessPermission.WRITE
        })
        
        assert user_can_access_company(3, first_company.id, "read") is True
        assert user_can_access_company(3, first_company.id, "write") is False
        
        assert user_can_access_company(3, second_company.id, "read") is True
        assert user_can_access_company(3, second_company.id, "write") is False
    finally:
        users_db.get_multi = original_get_multi
