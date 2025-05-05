from functools import wraps
from typing import Callable, Any, Dict, Optional
from uuid import UUID

from app.services.audit.services.audit_service import audit_service
from app.services.audit.schemas.audit import AuditLogCreate

def audit_log_action(
    action: str, 
    entity_type: str,
    get_entity_id: Callable[[Any], str],
    get_details: Optional[Callable[[Any], Dict]] = None
):
    """
    Decorator to create audit logs for service actions.
    
    Args:
        action: The action performed (CREATE, UPDATE, DELETE)
        entity_type: The type of entity being modified
        get_entity_id: Function to extract entity ID from function result
        get_details: Optional function to extract additional details
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if result:
                user_id = kwargs.get("current_user_id")
                user_email = kwargs.get("current_user_email")
                
                entity_id = get_entity_id(result)
                
                details = {}
                if get_details:
                    details = get_details(result)
                
                audit_log_data = AuditLogCreate(
                    user_id=user_id,
                    user_email=user_email,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    details=details
                )
                
                await audit_service.create_audit_log(audit_log_data)
            
            return result
        return wrapper
    return decorator
