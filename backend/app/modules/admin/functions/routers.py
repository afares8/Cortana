from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from uuid import UUID

from app.core.config import settings
from app.modules.admin.functions.schemas import FunctionCreate, FunctionUpdate, FunctionOut
from app.modules.admin.functions.services import (
    create_function, get_function, get_functions, 
    get_functions_by_department, update_function, delete_function
)

router = APIRouter()

@router.post("", response_model=FunctionOut, status_code=201)
async def create_function_endpoint(function: FunctionCreate):
    """Create a new function."""
    return create_function(function.model_dump())

@router.get("", response_model=List[FunctionOut])
async def get_functions_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    department_id: Optional[int] = None
):
    """Get all functions with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if department_id:
        filters["department_id"] = department_id
    
    return get_functions(skip=skip, limit=limit, filters=filters)

@router.get("/by-department/{department_id}", response_model=List[FunctionOut])
async def get_functions_by_department_endpoint(department_id: int = Path(...)):
    """Get all functions for a department."""
    return get_functions_by_department(department_id)

@router.get("/{function_id}", response_model=FunctionOut)
async def get_function_endpoint(function_id: int = Path(...)):
    """Get a function by ID."""
    function = get_function(function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    return function

@router.put("/{function_id}", response_model=FunctionOut)
async def update_function_endpoint(
    function_update: FunctionUpdate,
    function_id: int = Path(...)
):
    """Update a function."""
    function = update_function(function_id, function_update.model_dump(exclude_unset=True))
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    return function

@router.delete("/{function_id}", response_model=dict)
async def delete_function_endpoint(function_id: int = Path(...)):
    """Delete a function."""
    success = delete_function(function_id)
    if not success:
        raise HTTPException(status_code=404, detail="Function not found")
    return {"success": True}
