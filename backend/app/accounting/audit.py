from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from app.accounting.models import AuditLog
from app.db.in_memory_db import InMemoryDB

audit_logs_db = InMemoryDB[AuditLog]()

def create_audit_log(
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: UUID,
    metadata: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Create a new audit log entry."""
    audit_log = AuditLog(
        id=UUID.uuid4(),
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        timestamp=datetime.utcnow(),
        metadata=metadata or {}
    )
    
    return audit_logs_db.create(obj_in=audit_log)

def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[AuditLog]:
    """Get audit logs with optional filtering."""
    return audit_logs_db.get_multi(skip=skip, limit=limit, filters=filters)

def get_entity_audit_logs(
    entity_type: str,
    entity_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    """Get audit logs for a specific entity."""
    filters = {
        "entity_type": entity_type,
        "entity_id": entity_id
    }
    return audit_logs_db.get_multi(skip=skip, limit=limit, filters=filters)

def get_company_audit_logs(
    company_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    """Get audit logs for a specific company."""
    company_logs = get_entity_audit_logs("company", company_id, skip, limit)
    
    return company_logs
