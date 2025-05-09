from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.db.base import InMemoryDB
from app.modules.admin.audit.models import AuditLog, ActionType, TargetType

audit_logs_db = InMemoryDB[AuditLog](AuditLog)

def create_audit_log(log_data: Dict[str, Any]) -> AuditLog:
    """Create a new audit log entry."""
    return audit_logs_db.create(obj_in=AuditLog(**log_data))

def get_audit_log(log_id: int) -> Optional[AuditLog]:
    """Get an audit log by ID."""
    return audit_logs_db.get(id=log_id)

def get_audit_logs(
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[Dict[str, Any]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[AuditLog]:
    """Get audit logs with optional filtering."""
    filters = filters or {}
    
    if start_date or end_date:
        all_logs = audit_logs_db.get_multi()
        filtered_logs = []
        
        for log in all_logs:
            if start_date and log.created_at < start_date:
                continue
            if end_date and log.created_at > end_date:
                continue
            
            match = True
            for key, value in filters.items():
                if hasattr(log, key) and getattr(log, key) != value:
                    match = False
                    break
            
            if match:
                filtered_logs.append(log)
        
        return filtered_logs[skip:skip+limit]
    else:
        return audit_logs_db.get_multi(skip=skip, limit=limit, filters=filters)

def log_function_execution(
    user_id: int,
    function_id: int,
    function_name: str,
    input_data: Dict[str, Any],
    output_data: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None
) -> AuditLog:
    """Log a function execution."""
    return create_audit_log({
        "user_id": user_id,
        "action_type": ActionType.FUNCTION_EXECUTION,
        "target_type": TargetType.FUNCTION,
        "target_id": function_id,
        "payload": {
            "function_name": function_name,
            "input": input_data,
            "output": output_data or {}
        },
        "success": success,
        "error_message": error_message
    })

def log_automation_trigger(
    rule_id: int,
    rule_name: str,
    trigger_event: str,
    context: Dict[str, Any],
    actions_executed: List[Dict[str, Any]],
    success: bool = True,
    error_message: Optional[str] = None
) -> AuditLog:
    """Log an automation rule trigger."""
    return create_audit_log({
        "action_type": ActionType.AUTOMATION_TRIGGER,
        "target_type": TargetType.AUTOMATION_RULE,
        "target_id": rule_id,
        "payload": {
            "rule_name": rule_name,
            "trigger_event": trigger_event,
            "context": context,
            "actions_executed": actions_executed
        },
        "success": success,
        "error_message": error_message
    })

def log_ai_interaction(
    user_id: Optional[int],
    prompt: str,
    response: str,
    department_id: Optional[int] = None,
    model: Optional[str] = None,
    is_fallback: bool = False,
    success: bool = True,
    error_message: Optional[str] = None
) -> List[AuditLog]:
    """Log an AI prompt and response."""
    logs = []
    
    prompt_log = create_audit_log({
        "user_id": user_id,
        "action_type": ActionType.AI_PROMPT,
        "target_type": TargetType.AI_PROFILE if department_id else TargetType.SYSTEM,
        "target_id": department_id,
        "payload": {
            "prompt": prompt,
            "model": model,
            "department_id": department_id
        },
        "success": success,
        "error_message": error_message
    })
    logs.append(prompt_log)
    
    response_log = create_audit_log({
        "user_id": user_id,
        "action_type": ActionType.AI_RESPONSE,
        "target_type": TargetType.AI_PROFILE if department_id else TargetType.SYSTEM,
        "target_id": department_id,
        "payload": {
            "response": response,
            "model": model,
            "is_fallback": is_fallback,
            "department_id": department_id
        },
        "success": success,
        "error_message": error_message
    })
    logs.append(response_log)
    
    return logs

def log_entity_change(
    user_id: int,
    action_type: str,
    target_type: str,
    target_id: int,
    entity_name: str,
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None
) -> AuditLog:
    """Log a change to an entity (department, role, template, etc.)."""
    return create_audit_log({
        "user_id": user_id,
        "action_type": action_type,
        "target_type": target_type,
        "target_id": target_id,
        "payload": {
            "entity_name": entity_name,
            "before": before or {},
            "after": after or {}
        },
        "success": success,
        "error_message": error_message
    })

def get_audit_summary(days: int = 7) -> Dict[str, Any]:
    """Get a summary of audit logs for the specified number of days."""
    start_date = datetime.utcnow() - timedelta(days=days)
    logs = get_audit_logs(
        limit=1000,  # Get a large number of logs for the summary
        start_date=start_date
    )
    
    total_logs = len(logs)
    success_count = sum(1 for log in logs if log.success)
    error_count = total_logs - success_count
    
    action_type_counts = {}
    target_type_counts = {}
    
    for log in logs:
        if log.action_type in action_type_counts:
            action_type_counts[log.action_type] += 1
        else:
            action_type_counts[log.action_type] = 1
        
        if log.target_type in target_type_counts:
            target_type_counts[log.target_type] += 1
        else:
            target_type_counts[log.target_type] = 1
    
    recent_errors = [log for log in logs if not log.success]
    recent_errors.sort(key=lambda x: x.created_at, reverse=True)
    recent_errors = recent_errors[:10]  # Get the 10 most recent errors
    
    return {
        "total_logs": total_logs,
        "success_count": success_count,
        "error_count": error_count,
        "action_type_counts": action_type_counts,
        "target_type_counts": target_type_counts,
        "recent_errors": recent_errors
    }

def get_failure_alerts(hours: int = 24) -> List[AuditLog]:
    """Get failure alerts for the specified number of hours."""
    start_date = datetime.utcnow() - timedelta(hours=hours)
    logs = get_audit_logs(
        limit=100,
        filters={"success": False},
        start_date=start_date
    )
    
    return logs
