from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from uuid import UUID

from app.core.config import settings
from app.modules.admin.permissions.schemas import (
    PermissionCreate, PermissionUpdate, PermissionOut,
    PermissionGroupCreate, PermissionGroupUpdate, PermissionGroupOut
)
from app.modules.admin.permissions.services import (
    create_permission, get_permission, get_permissions, update_permission, delete_permission,
    create_permission_group, get_permission_group, get_permission_groups, update_permission_group, delete_permission_group
)

router = APIRouter()

@router.post("", response_model=PermissionOut, status_code=201)
async def create_permission_endpoint(permission: PermissionCreate):
    """Create a new permission."""
    return create_permission(permission.model_dump())

@router.get("", response_model=List[PermissionOut])
async def get_permissions_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all permissions with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if category:
        filters["category"] = category
    
    return get_permissions(skip=skip, limit=limit, filters=filters)

@router.get("/{permission_id}", response_model=PermissionOut)
async def get_permission_endpoint(permission_id: int = Path(...)):
    """Get a permission by ID."""
    permission = get_permission(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@router.put("/{permission_id}", response_model=PermissionOut)
async def update_permission_endpoint(
    permission_update: PermissionUpdate,
    permission_id: int = Path(...)
):
    """Update a permission."""
    permission = update_permission(permission_id, permission_update.model_dump(exclude_unset=True))
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@router.delete("/{permission_id}", response_model=dict)
async def delete_permission_endpoint(permission_id: int = Path(...)):
    """Delete a permission."""
    success = delete_permission(permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"success": True}

@router.post("/groups", response_model=PermissionGroupOut, status_code=201)
async def create_permission_group_endpoint(group: PermissionGroupCreate):
    """Create a new permission group."""
    return create_permission_group(group.model_dump())

@router.get("/groups", response_model=List[PermissionGroupOut])
async def get_permission_groups_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None
):
    """Get all permission groups with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    
    return get_permission_groups(skip=skip, limit=limit, filters=filters)

@router.get("/groups/{group_id}", response_model=PermissionGroupOut)
async def get_permission_group_endpoint(group_id: int = Path(...)):
    """Get a permission group by ID."""
    group = get_permission_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Permission group not found")
    return group

@router.put("/groups/{group_id}", response_model=PermissionGroupOut)
async def update_permission_group_endpoint(
    group_update: PermissionGroupUpdate,
    group_id: int = Path(...)
):
    """Update a permission group."""
    group = update_permission_group(group_id, group_update.model_dump(exclude_unset=True))
    if not group:
        raise HTTPException(status_code=404, detail="Permission group not found")
    return group

@router.delete("/groups/{group_id}", response_model=dict)
async def delete_permission_group_endpoint(group_id: int = Path(...)):
    """Delete a permission group."""
    success = delete_permission_group(group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission group not found")
    return {"success": True}
