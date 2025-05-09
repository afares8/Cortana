from typing import List, Optional, Dict, Any
from uuid import UUID

from app.db.base import InMemoryDB
from app.modules.admin.roles.models import UserDepartmentRole
from app.modules.admin.departments.services import get_department
from app.modules.admin.roles.services import get_role

user_department_roles_db = InMemoryDB[UserDepartmentRole](UserDepartmentRole)

def assign_user_to_department(
    user_id: int,
    department_id: int,
    role_id: int
) -> UserDepartmentRole:
    """Assign a user to a department with a specific role."""
    assignment = UserDepartmentRole(
        user_id=user_id,
        department_id=department_id,
        role_id=role_id
    )
    return user_department_roles_db.create(obj_in=assignment)

def get_user_department_assignments(user_id: int) -> List[UserDepartmentRole]:
    """Get all department assignments for a user."""
    return user_department_roles_db.get_multi(filters={"user_id": user_id})

def get_department_user_assignments(department_id: int) -> List[UserDepartmentRole]:
    """Get all user assignments for a department."""
    return user_department_roles_db.get_multi(filters={"department_id": department_id})

def get_user_department_role_assignment(
    user_id: int,
    department_id: int
) -> Optional[UserDepartmentRole]:
    """Get a specific user-department-role assignment."""
    assignments = user_department_roles_db.get_multi(
        filters={"user_id": user_id, "department_id": department_id}
    )
    return assignments[0] if assignments else None

def remove_user_department_assignment(
    user_id: int,
    department_id: int
) -> bool:
    """Remove a user from a department."""
    assignment = get_user_department_role_assignment(user_id, department_id)
    if not assignment:
        return False
    
    user_department_roles_db.remove(id=assignment.id)
    return True

def get_user_department_roles_with_details(user_id: int) -> List[Dict[str, Any]]:
    """Get all department and role assignments for a user with details."""
    assignments = get_user_department_assignments(user_id)
    result = []
    
    for assignment in assignments:
        department = get_department(assignment.department_id)
        role = get_role(assignment.role_id)
        
        if department and role:
            result.append({
                "user_id": assignment.user_id,
                "department_id": assignment.department_id,
                "role_id": assignment.role_id,
                "department_name": department.name,
                "role_name": role.name
            })
    
    return result
