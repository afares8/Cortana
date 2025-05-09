from typing import List, Optional, Dict, Any
from uuid import UUID

from app.db.base import InMemoryDB
from app.modules.admin.departments.models import Department

departments_db = InMemoryDB[Department](Department)

def create_department(department_data: Dict[str, Any]) -> Department:
    """Create a new department."""
    return departments_db.create(obj_in=Department(**department_data))

def get_department(department_id: int) -> Optional[Department]:
    """Get a department by ID."""
    return departments_db.get(id=department_id)

def get_departments(
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[Dict[str, Any]] = None
) -> List[Department]:
    """Get departments with optional filtering."""
    return departments_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_department(department_id: int, department_data: Dict[str, Any]) -> Optional[Department]:
    """Update a department."""
    return departments_db.update(id=department_id, obj_in=Department(**department_data))

def delete_department(department_id: int) -> bool:
    """Delete a department."""
    department = departments_db.remove(id=department_id)
    return department is not None
