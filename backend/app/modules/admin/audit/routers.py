from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from datetime import datetime, timedelta

from app.core.config import settings
from app.modules.admin.audit.schemas import (
    AuditLogCreate, AuditLogOut, AuditLogFilter, AuditSummary
)
from app.modules.admin.audit.services import (
    create_audit_log, get_audit_log, get_audit_logs,
    get_audit_summary, get_failure_alerts
)

router = APIRouter()

@router.post("", response_model=AuditLogOut, status_code=201)
async def create_audit_log_endpoint(log: AuditLogCreate):
    """Create a new audit log entry."""
    return create_audit_log(log.model_dump())

@router.get("", response_model=List[AuditLogOut])
async def get_audit_logs_endpoint(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    success: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get audit logs with optional filtering."""
    filters = {}
    if user_id is not None:
        filters["user_id"] = user_id
    if action_type:
        filters["action_type"] = action_type
    if target_type:
        filters["target_type"] = target_type
    if target_id is not None:
        filters["target_id"] = target_id
    if success is not None:
        filters["success"] = success
    
    return get_audit_logs(
        skip=skip,
        limit=limit,
        filters=filters,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/summary", response_model=AuditSummary)
async def get_audit_summary_endpoint(days: int = Query(7, ge=1, le=30)):
    """Get a summary of audit logs for the specified number of days."""
    return get_audit_summary(days=days)

@router.get("/alerts", response_model=List[AuditLogOut])
async def get_failure_alerts_endpoint(hours: int = Query(24, ge=1, le=72)):
    """Get failure alerts for the specified number of hours."""
    return get_failure_alerts(hours=hours)

@router.get("/{log_id}", response_model=AuditLogOut)
async def get_audit_log_endpoint(log_id: int = Path(...)):
    """Get an audit log by ID."""
    log = get_audit_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log
