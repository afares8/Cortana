from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from uuid import UUID

from app.core.config import settings
from app.modules.admin.roles.schemas import (
    RoleCreate, RoleUpdate, RoleOut, 
    RoleAssignmentCreate, RoleAssignmentOut
)
from app.modules.admin.roles.services import (
    create_role, get_role, get_roles, update_role, delete_role,
    assign_role, get_user_roles, get_department_roles, get_user_department_roles,
    remove_role_assignment
)

router = APIRouter()

@router.post("", response_model=RoleOut, status_code=201)
async def create_role_endpoint(role: RoleCreate):
    """Create a new role."""
    return create_role(role.model_dump())

@router.get("", response_model=List[RoleOut])
async def get_roles_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    department_id: Optional[int] = None
):
    """Get all roles with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if department_id:
        filters["department_id"] = department_id
    
    return get_roles(skip=skip, limit=limit, filters=filters)

@router.get("/{role_id}", response_model=RoleOut)
async def get_role_endpoint(role_id: int = Path(...)):
    """Get a role by ID."""
    role = get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/{role_id}", response_model=RoleOut)
async def update_role_endpoint(
    role_update: RoleUpdate,
    role_id: int = Path(...)
):
    """Update a role."""
    role = update_role(role_id, role_update.model_dump(exclude_unset=True))
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.delete("/{role_id}", response_model=dict)
async def delete_role_endpoint(role_id: int = Path(...)):
    """Delete a role."""
    success = delete_role(role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"success": True}


@router.get("/by-department/{department_id}", response_model=List[RoleOut])
async def get_department_roles_endpoint(department_id: int = Path(...)):
    """Get all roles for a department."""
    return get_department_roles(department_id)


@router.get("/by-user-department", response_model=List[RoleAssignmentOut])
async def get_user_department_roles_endpoint(
    user_id: int = Query(...),
    department_id: int = Query(...)
):
    """Get all roles assigned to a user in a specific department."""
    return get_user_department_roles(user_id, department_id)

@router.delete("/assignment/{assignment_id}", response_model=dict)
async def remove_role_assignment_endpoint(assignment_id: int = Path(...)):
    """Remove a role assignment."""
    success = remove_role_assignment(assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    return {"success": True}
