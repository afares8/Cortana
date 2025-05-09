from typing import Optional, Dict, Any, List
from pydantic import Field
from enum import Enum
from app.models.base import TimestampModel

class TriggerEvent(str, Enum):
    CONTRACT_CREATED = "contract_created"
    INVOICE_APPROVED = "invoice_approved"
    CLIENT_ADDED = "client_added"
    RISK_DETECTED = "risk_detected"

class ActionType(str, Enum):
    SEND_EMAIL = "send_email"
    RUN_FUNCTION = "run_function"
    TRIGGER_IA = "trigger_ia"
    NOTIFY_USER = "notify_user"
    CREATE_TASK = "create_task"
    CALL_RPA = "call_rpa"

class AutomationRule(TimestampModel):
    id: int = 0
    name: str
    trigger_event: str
    conditions: Dict[str, Any] = {}
    actions: List[Dict[str, Any]] = []
    department_id: int
    active: bool = True
