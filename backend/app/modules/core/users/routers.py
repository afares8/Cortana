from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from uuid import UUID

from app.core.config import settings
from app.modules.core.users.schemas import (
    UserDepartmentAssignment, UserDepartmentAssignmentResponse,
    UserDepartmentRoleResponse
)
from app.modules.core.users.services import (
    assign_user_to_department, get_user_department_assignments,
    get_department_user_assignments, get_user_department_role_assignment,
    remove_user_department_assignment, get_user_department_roles_with_details
)

router = APIRouter()

@router.post("/{user_id}/assign-to-department", response_model=UserDepartmentAssignmentResponse)
async def assign_user_to_department_endpoint(
    assignment: UserDepartmentAssignment,
    user_id: int = Path(...)
):
    """Assign a user to a department with a specific role."""
    if assignment.user_id != user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID in path must match user ID in request body"
        )
    
    return assign_user_to_department(
        user_id=assignment.user_id,
        department_id=assignment.department_id,
        role_id=assignment.role_id
    )

@router.get("/{user_id}/departments", response_model=List[UserDepartmentRoleResponse])
async def get_user_departments_endpoint(user_id: int = Path(...)):
    """Get all departments and roles assigned to a user."""
    assignments = get_user_department_roles_with_details(user_id)
    return assignments

@router.get("/departments/{department_id}/users", response_model=List[UserDepartmentAssignmentResponse])
async def get_department_users_endpoint(department_id: int = Path(...)):
    """Get all users assigned to a department."""
    return get_department_user_assignments(department_id)

@router.delete("/{user_id}/departments/{department_id}", response_model=dict)
async def remove_user_from_department_endpoint(
    user_id: int = Path(...),
    department_id: int = Path(...)
):
    """Remove a user from a department."""
    success = remove_user_department_assignment(user_id, department_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="User-department assignment not found"
        )
    return {"success": True}
