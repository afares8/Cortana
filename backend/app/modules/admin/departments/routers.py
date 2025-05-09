from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from uuid import UUID

from app.core.config import settings
from app.modules.admin.departments.schemas import DepartmentCreate, DepartmentUpdate, DepartmentOut
from app.modules.admin.departments.services import create_department, get_department, get_departments, update_department, delete_department

router = APIRouter()

@router.post("", response_model=DepartmentOut, status_code=201)
async def create_department_endpoint(department: DepartmentCreate):
    """Create a new department."""
    return create_department(department.model_dump())

@router.get("", response_model=List[DepartmentOut])
async def get_departments_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    type: Optional[str] = None,
    company_id: Optional[UUID] = None
):
    """Get all departments with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if type:
        filters["type"] = type
    if company_id:
        filters["company_id"] = company_id
    
    return get_departments(skip=skip, limit=limit, filters=filters)

@router.get("/{department_id}", response_model=DepartmentOut)
async def get_department_endpoint(department_id: int = Path(...)):
    """Get a department by ID."""
    department = get_department(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.put("/{department_id}", response_model=DepartmentOut)
async def update_department_endpoint(
    department_update: DepartmentUpdate,
    department_id: int = Path(...)
):
    """Update a department."""
    department = update_department(department_id, department_update.model_dump(exclude_unset=True))
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.delete("/{department_id}", response_model=dict)
async def delete_department_endpoint(department_id: int = Path(...)):
    """Delete a department."""
    success = delete_department(department_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"success": True}
