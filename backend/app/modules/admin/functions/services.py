from typing import List, Optional, Dict, Any

from app.db.base import InMemoryDB
from app.modules.admin.functions.models import Function

functions_db = InMemoryDB[Function](Function)

def create_function(function_data: Dict[str, Any]) -> Function:
    """Create a new function."""
    return functions_db.create(obj_in=Function(**function_data))

def get_function(function_id: int) -> Optional[Function]:
    """Get a function by ID."""
    return functions_db.get(id=function_id)

def get_functions(
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[Dict[str, Any]] = None
) -> List[Function]:
    """Get functions with optional filtering."""
    return functions_db.get_multi(skip=skip, limit=limit, filters=filters)

def get_functions_by_department(department_id: int) -> List[Function]:
    """Get all functions for a department."""
    return functions_db.get_multi(filters={"department_id": department_id})

def update_function(function_id: int, function_data: Dict[str, Any]) -> Optional[Function]:
    """Update a function."""
    return functions_db.update(id=function_id, obj_in=Function(**function_data))

def delete_function(function_id: int) -> bool:
    """Delete a function."""
    function = functions_db.remove(id=function_id)
    return function is not None
