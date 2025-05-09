from typing import List, Optional, Dict, Any

from app.db.base import InMemoryDB
from app.modules.automation.rules_engine.models import AutomationRule

automation_rules_db = InMemoryDB[AutomationRule](AutomationRule)

def create_automation_rule(rule_data: Dict[str, Any]) -> AutomationRule:
    """Create a new automation rule."""
    return automation_rules_db.create(obj_in=AutomationRule(**rule_data))

def get_automation_rule(rule_id: int) -> Optional[AutomationRule]:
    """Get an automation rule by ID."""
    return automation_rules_db.get(id=rule_id)

def get_automation_rules(
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[Dict[str, Any]] = None
) -> List[AutomationRule]:
    """Get automation rules with optional filtering."""
    return automation_rules_db.get_multi(skip=skip, limit=limit, filters=filters)

def get_automation_rules_by_department(department_id: int) -> List[AutomationRule]:
    """Get all automation rules for a department."""
    return automation_rules_db.get_multi(filters={"department_id": department_id})

def update_automation_rule(rule_id: int, rule_data: Dict[str, Any]) -> Optional[AutomationRule]:
    """Update an automation rule."""
    return automation_rules_db.update(id=rule_id, obj_in=AutomationRule(**rule_data))

def delete_automation_rule(rule_id: int) -> bool:
    """Delete an automation rule."""
    rule = automation_rules_db.remove(id=rule_id)
    return rule is not None

def execute_automation_rule(rule_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an automation rule with the given context."""
    rule = get_automation_rule(rule_id)
    if not rule or not rule.active:
        return {"success": False, "error": "Rule not found or inactive"}
    
    conditions_met = True
    for key, value in rule.conditions.items():
        if key not in context or context[key] != value:
            conditions_met = False
            break
    
    if not conditions_met:
        return {"success": False, "error": "Conditions not met"}
    
    results = []
    for action in rule.actions:
        action_type = action.get("type")
        action_params = action.get("params", {})
        
        results.append({
            "type": action_type,
            "params": action_params,
            "status": "executed"
        })
    
    return {
        "success": True,
        "rule_id": rule.id,
        "rule_name": rule.name,
        "actions_executed": len(results),
        "results": results
    }
