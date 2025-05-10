from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from app.db.base import InMemoryDB
from app.modules.admin.departments.models import Department

logger = logging.getLogger(__name__)

departments_db = InMemoryDB[Department](Department)

class DepartmentService:
    def __init__(self):
        self.db = departments_db
        
    def create_department(self, department_data: Dict[str, Any]) -> Department:
        """Create a new department."""
        return self.db.create(obj_in=Department(**department_data))

    def get_department(self, department_id: int) -> Optional[Department]:
        """Get a department by ID."""
        return self.db.get(id=department_id)

    def get_departments(
        self,
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Department]:
        """Get departments with optional filtering."""
        departments = list(self.db.data.values())
        logger.info(f"Retrieved {len(departments)} departments from database")
        
        if filters:
            for key, value in filters.items():
                departments = [d for d in departments if getattr(d, key, None) == value]
        
        if skip:
            departments = departments[skip:]
        
        if limit and limit < len(departments):
            departments = departments[:limit]
            
        return departments

    def update_department(self, department_id: int, department_data: Dict[str, Any]) -> Optional[Department]:
        """Update a department."""
        return self.db.update(id=department_id, obj_in=Department(**department_data))

    def delete_department(self, department_id: int) -> bool:
        """Delete a department."""
        department = self.db.remove(id=department_id)
        return department is not None
    
    def sync_with_global_db(self, global_db):
        """Sync with the global database instance after initialization"""
        self.db.data = global_db.data

department_service = DepartmentService()

create_department = department_service.create_department
get_department = department_service.get_department
get_departments = department_service.get_departments
update_department = department_service.update_department
delete_department = department_service.delete_department
