from typing import List, Optional, Dict, Any
from uuid import UUID

from app.db.base import InMemoryDB
from app.modules.admin.roles.models import Role, UserDepartmentRole

roles_db = InMemoryDB[Role](Role)
user_department_roles_db = InMemoryDB[UserDepartmentRole](UserDepartmentRole)

def create_role(role_data: Dict[str, Any]) -> Role:
    """Create a new role."""
    return roles_db.create(obj_in=Role(**role_data))

def get_role(role_id: int) -> Optional[Role]:
    """Get a role by ID."""
    return roles_db.get(id=role_id)

def get_roles(
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[Dict[str, Any]] = None
) -> List[Role]:
    """Get roles with optional filtering."""
    return roles_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_role(role_id: int, role_data: Dict[str, Any]) -> Optional[Role]:
    """Update a role."""
    return roles_db.update(id=role_id, obj_in=Role(**role_data))

def delete_role(role_id: int) -> bool:
    """Delete a role."""
    role = roles_db.remove(id=role_id)
    return role is not None

def assign_role(assignment_data: Dict[str, Any]) -> UserDepartmentRole:
    """Assign a role to a user in a department."""
    return user_department_roles_db.create(obj_in=UserDepartmentRole(**assignment_data))

def get_user_roles(user_id: int) -> List[UserDepartmentRole]:
    """Get all roles assigned to a user."""
    return user_department_roles_db.get_multi(filters={"user_id": user_id})

def get_department_roles(department_id: int) -> List[Role]:
    """Get all roles for a department."""
    return roles_db.get_multi(filters={"department_id": department_id})

def get_user_department_roles(user_id: int, department_id: int) -> List[UserDepartmentRole]:
    """Get all roles assigned to a user in a specific department."""
    return user_department_roles_db.get_multi(
        filters={"user_id": user_id, "department_id": department_id}
    )

def remove_role_assignment(assignment_id: int) -> bool:
    """Remove a role assignment."""
    assignment = user_department_roles_db.remove(id=assignment_id)
    return assignment is not None
