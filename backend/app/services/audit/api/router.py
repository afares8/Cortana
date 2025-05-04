from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from pydantic import EmailStr

from app.services.audit.models.audit import AuditLog
from app.services.audit.schemas.audit import AuditLogCreate
from app.services.audit.services.audit_service import audit_service

router = APIRouter()

@router.post("/", response_model=AuditLog, status_code=201)
async def create_audit_log_endpoint(audit_log: AuditLogCreate):
    """Create a new audit log entry."""
    return await audit_service.create_audit_log(audit_log)

@router.get("/", response_model=List[AuditLog])
async def get_audit_logs_endpoint(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
):
    """Get audit logs with optional filtering."""
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if user_email:
        filters["user_email"] = user_email
    if action:
        filters["action"] = action
    if entity_type:
        filters["entity_type"] = entity_type
    if entity_id:
        filters["entity_id"] = entity_id
    
    logs = await audit_service.get_audit_logs(skip=skip, limit=limit, filters=filters)
    
    if from_date or to_date:
        filtered_logs = []
        for log in logs:
            if from_date and log.created_at < from_date:
                continue
            if to_date and log.created_at > to_date:
                continue
            filtered_logs.append(log)
        return filtered_logs
    
    return logs

@router.get("/{log_id}", response_model=AuditLog)
async def get_audit_log_endpoint(log_id: int = Path(..., gt=0)):
    """Get an audit log by ID."""
    log = await audit_service.get_audit_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log

@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLog])
async def get_entity_audit_logs_endpoint(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    skip: int = 0,
    limit: int = 100
):
    """Get audit logs for a specific entity."""
    logs = await audit_service.get_entity_audit_logs(
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )
    return logs

@router.get("/user/{user_id}", response_model=List[AuditLog])
async def get_user_audit_logs_endpoint(
    user_id: int = Path(..., gt=0),
    skip: int = 0,
    limit: int = 100
):
    """Get audit logs for a specific user."""
    logs = await audit_service.get_user_audit_logs(
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    return logs
