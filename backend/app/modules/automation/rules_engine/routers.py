from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from uuid import UUID

from app.core.config import settings
from app.modules.automation.rules_engine.schemas import (
    AutomationRuleCreate, AutomationRuleUpdate, AutomationRuleOut,
    TriggerEvent, ActionType
)
from app.modules.automation.rules_engine.services import (
    create_automation_rule, get_automation_rule, get_automation_rules,
    get_automation_rules_by_department, update_automation_rule, 
    delete_automation_rule, execute_automation_rule
)

router = APIRouter()

@router.post("", response_model=AutomationRuleOut, status_code=201)
async def create_automation_rule_endpoint(rule: AutomationRuleCreate):
    """Create a new automation rule."""
    return create_automation_rule(rule.model_dump())

@router.get("", response_model=List[AutomationRuleOut])
async def get_automation_rules_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    trigger_event: Optional[str] = None,
    department_id: Optional[int] = None,
    active: Optional[bool] = None
):
    """Get all automation rules with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if trigger_event:
        filters["trigger_event"] = trigger_event
    if department_id:
        filters["department_id"] = department_id
    if active is not None:
        filters["active"] = active
    
    return get_automation_rules(skip=skip, limit=limit, filters=filters)

@router.get("/by-department/{department_id}", response_model=List[AutomationRuleOut])
async def get_automation_rules_by_department_endpoint(department_id: int = Path(...)):
    """Get all automation rules for a department."""
    return get_automation_rules_by_department(department_id)

@router.get("/trigger-events", response_model=List[str])
async def get_trigger_events_endpoint():
    """Get all available trigger events."""
    return [event.value for event in TriggerEvent]

@router.get("/action-types", response_model=List[str])
async def get_action_types_endpoint():
    """Get all available action types."""
    return [action.value for action in ActionType]

@router.get("/{rule_id}", response_model=AutomationRuleOut)
async def get_automation_rule_endpoint(rule_id: int = Path(...)):
    """Get an automation rule by ID."""
    rule = get_automation_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return rule

@router.put("/{rule_id}", response_model=AutomationRuleOut)
async def update_automation_rule_endpoint(
    rule_update: AutomationRuleUpdate,
    rule_id: int = Path(...)
):
    """Update an automation rule."""
    rule = update_automation_rule(rule_id, rule_update.model_dump(exclude_unset=True))
    if not rule:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return rule

@router.delete("/{rule_id}", response_model=dict)
async def delete_automation_rule_endpoint(rule_id: int = Path(...)):
    """Delete an automation rule."""
    success = delete_automation_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return {"success": True}

@router.post("/{rule_id}/execute", response_model=Dict[str, Any])
async def execute_automation_rule_endpoint(
    context: Dict[str, Any],
    rule_id: int = Path(...)
):
    """Execute an automation rule with the given context."""
    result = execute_automation_rule(rule_id, context)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Execution failed"))
    return result
