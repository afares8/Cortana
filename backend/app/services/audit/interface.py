from typing import List, Optional, Dict, Any
from app.services.audit.models.audit import AuditLog
from app.services.audit.schemas.audit import AuditLogCreate

class AuditServiceInterface:
    """
    Interface for audit log operations.
    """
    
    async def create_audit_log(self, audit_log_data: AuditLogCreate) -> AuditLog:
        """
        Create a new audit log entry.
        """
        pass
    
    async def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[AuditLog]:
        """
        Get audit logs with optional filtering.
        """
        pass
    
    async def get_audit_log(self, log_id: int) -> Optional[AuditLog]:
        """
        Get an audit log by ID.
        """
        pass
    
    async def get_entity_audit_logs(
        self,
        entity_type: str,
        entity_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific entity.
        """
        pass
    
    async def get_user_audit_logs(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific user.
        """
        pass
