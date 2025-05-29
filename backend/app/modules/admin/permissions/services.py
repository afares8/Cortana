from typing import Dict, List, Optional, Any
from app.db.base import InMemoryDB
from app.modules.admin.permissions.models import Permission, PermissionGroup

permissions_db = InMemoryDB[Permission](Permission)
permission_groups_db = InMemoryDB[PermissionGroup](PermissionGroup)

def create_permission(permission_data: Dict[str, Any]) -> Permission:
    """Create a new permission."""
    permission = Permission(**permission_data)
    permission.id = permissions_db.get_next_id()
    permissions_db.create(permission)
    return permission

def get_permission(permission_id: int) -> Optional[Permission]:
    """Get a permission by ID."""
    return permissions_db.get(permission_id)

def get_permissions(
    skip: int = 0, 
    limit: int = 100, 
    filters: Dict[str, Any] = None
) -> List[Permission]:
    """Get all permissions with optional filtering."""
    return permissions_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_permission(
    permission_id: int, 
    permission_data: Dict[str, Any]
) -> Optional[Permission]:
    """Update a permission."""
    permission = permissions_db.get(permission_id)
    if not permission:
        return None
    
    for key, value in permission_data.items():
        setattr(permission, key, value)
    
    permissions_db.update(permission)
    return permission

def delete_permission(permission_id: int) -> bool:
    """Delete a permission."""
    permission = permissions_db.get(permission_id)
    if not permission:
        return False
    
    permissions_db.delete(permission_id)
    return True

def create_permission_group(group_data: Dict[str, Any]) -> PermissionGroup:
    """Create a new permission group."""
    group = PermissionGroup(**group_data)
    group.id = permission_groups_db.get_next_id()
    permission_groups_db.create(group)
    return group

def get_permission_group(group_id: int) -> Optional[PermissionGroup]:
    """Get a permission group by ID."""
    return permission_groups_db.get(group_id)

def get_permission_groups(
    skip: int = 0, 
    limit: int = 100, 
    filters: Dict[str, Any] = None
) -> List[PermissionGroup]:
    """Get all permission groups with optional filtering."""
    return permission_groups_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_permission_group(
    group_id: int, 
    group_data: Dict[str, Any]
) -> Optional[PermissionGroup]:
    """Update a permission group."""
    group = permission_groups_db.get(group_id)
    if not group:
        return None
    
    for key, value in group_data.items():
        setattr(group, key, value)
    
    permission_groups_db.update(group)
    return group

def delete_permission_group(group_id: int) -> bool:
    """Delete a permission group."""
    group = permission_groups_db.get(group_id)
    if not group:
        return False
    
    permission_groups_db.delete(group_id)
    return True

def sync_with_global_db(global_db):
    """Sync the local database with the global database."""
    permissions_db.data = global_db.data
