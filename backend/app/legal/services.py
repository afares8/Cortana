from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import os
import uuid
import json
import base64
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from app.db.init_db import users_db
from app.core.config import settings
from app.legal.models import (
    Client,
    Contract,
    ContractVersion,
    WorkflowTemplate,
    WorkflowInstance,
    Task,
    AuditLog,
)
from app.legal.schemas import ClientCreate
from app.db.base import InMemoryDB

clients_db = InMemoryDB[Client](Client)
contracts_db = InMemoryDB[Contract](Contract)
contract_versions_db = InMemoryDB[ContractVersion](ContractVersion)
workflow_templates_db = InMemoryDB[WorkflowTemplate](WorkflowTemplate)
workflow_instances_db = InMemoryDB[WorkflowInstance](WorkflowInstance)
tasks_db = InMemoryDB[Task](Task)
audit_logs_db = InMemoryDB[AuditLog](AuditLog)

LEGAL_UPLOADS_DIR = Path("uploads/legal")
LEGAL_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def create_client(client_data: Dict[str, Any]) -> Client:
    """Create a new client with automatic risk evaluation and compliance checks."""
    from app.services.compliance.services.excel_risk_evaluator import (
        excel_risk_evaluator,
    )
    from app.services.compliance.services.compliance_service import compliance_service
    from app.services.compliance.schemas.compliance import PEPScreeningResultCreate, SanctionsScreeningResultCreate
    import asyncio

    client_create = ClientCreate(**client_data)
    next_id = clients_db.counter
    client_dict = client_create.model_dump()
    client_dict["id"] = next_id
    client_dict["created_at"] = datetime.now()
    client = Client(**client_dict)
    clients_db.data[next_id] = client
    clients_db.counter += 1

    try:
        risk_evaluation = excel_risk_evaluator.calculate_risk(
            {
                "client_type": client_data.get("client_type", "individual"),
                "country": client_data.get("country", "PA"),  # Default to Panama
                "industry": client_data.get("industry", "other"),
                "channel": client_data.get("channel", "presencial"),
            }
        )

        client.risk_score = risk_evaluation.get("total_score", 2.0)
        client.risk_level = risk_evaluation.get("risk_level", "MEDIUM")
        client.risk_details = risk_evaluation

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        pep_result = loop.run_until_complete(
            compliance_service.create_pep_screening(
                PEPScreeningResultCreate(
                    client_id=client.id,
                    match_status="pending",
                    screened_by="system",
                    risk_level="unknown",
                    notes="Automatic screening during client creation"
                )
            )
        )

        sanctions_result = loop.run_until_complete(
            compliance_service.create_sanctions_screening(
                SanctionsScreeningResultCreate(
                    client_id=client.id,
                    match_status="pending",
                    screened_by="system",
                    risk_level="unknown",
                    notes="Automatic screening during client creation"
                )
            )
        )

        client.pep_screening_id = pep_result.id if pep_result else None
        client.sanctions_screening_id = (
            sanctions_result.id if sanctions_result else None
        )

        clients_db.data[client.id] = client

        loop.close()

    except Exception as e:
        logger.error(f"Error during client risk evaluation: {str(e)}")

    create_audit_log(
        entity_type="client",
        entity_id=client.id,
        action="created",
        user_email=client_data.get("created_by", "system"),
        details={
            "client_name": client.name,
            "risk_level": getattr(client, "risk_level", "UNKNOWN"),
        },
    )

    return client


def get_client(client_id: int) -> Optional[Client]:
    """Get a client by ID."""
    return clients_db.get(client_id)


def get_clients(
    skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
) -> List[Client]:
    """Get a list of clients with optional filtering."""
    return clients_db.get_multi(skip=skip, limit=limit, filters=filters or {})


def update_client(client_id: int, client_data: Dict[str, Any]) -> Optional[Client]:
    """Update a client."""
    client = clients_db.get(client_id)
    if not client:
        return None

    updated_client = clients_db.update(id=client_id, obj_in=client_data)

    create_audit_log(
        entity_type="client",
        entity_id=client_id,
        action="updated",
        user_email=client_data.get("updated_by", "system"),
        details={"fields_updated": list(client_data.keys())},
    )

    return updated_client


def delete_client(client_id: int) -> bool:
    """Delete a client."""
    client = clients_db.get(client_id)
    if not client:
        return False

    client_contracts = contracts_db.get_multi(filters={"client_id": client_id})
    if client_contracts:
        return False

    result = clients_db.delete(client_id)

    create_audit_log(
        entity_type="client",
        entity_id=client_id,
        action="deleted",
        user_email="system",
        details={"client_name": client.name},
    )

    return result


def save_contract_file(file_content: str, file_extension: str = ".pdf") -> str:
    """Save a contract file to disk and return the file path."""
    if not file_content:
        return ""

    try:
        file_data = base64.b64decode(file_content)
    except Exception:
        return ""

    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = LEGAL_UPLOADS_DIR / filename

    with open(file_path, "wb") as f:
        f.write(file_data)

    return str(file_path)


def create_contract(contract_data: Dict[str, Any]) -> Contract:
    """Create a new contract with initial version."""
    file_content = contract_data.pop("file_content", None)
    file_extension = ".pdf"  # Default extension

    file_path = ""
    if file_content:
        file_path = save_contract_file(file_content, file_extension)

    contract_dict = {**contract_data, "file_path": file_path}
    contract = contracts_db.create(obj_in=Contract(**contract_dict))

    version = contract_versions_db.create(
        obj_in=ContractVersion(
            id=1,  # First version
            contract_id=contract.id,
            version=1,
            file_path=file_path,
            changes_description="Initial version",
            created_by=contract_data.get("created_by", "system"),
        )
    )

    create_audit_log(
        entity_type="contract",
        entity_id=contract.id,
        action="created",
        user_email=contract_data.get("created_by", "system"),
        details={"contract_title": contract.title, "client_id": contract.client_id},
    )

    return contract


def get_contract(contract_id: int) -> Optional[Contract]:
    """Get a contract by ID with its versions."""
    contract = contracts_db.get(contract_id)
    if not contract:
        return None

    client = clients_db.get(contract.client_id)
    if client:
        contract.client_name = client.name

    versions = contract_versions_db.get_multi(filters={"contract_id": contract_id})
    contract.versions = sorted(versions, key=lambda v: v.version)

    return contract


def get_contracts(
    skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
) -> List[Contract]:
    """Get a list of contracts with optional filtering."""
    contracts = contracts_db.get_multi(skip=skip, limit=limit, filters=filters or {})

    for contract in contracts:
        client = clients_db.get(contract.client_id)
        if client:
            contract.client_name = client.name

    return contracts


def update_contract(
    contract_id: int, contract_data: Dict[str, Any]
) -> Optional[Contract]:
    """Update a contract and create a new version if file content is provided."""
    contract = contracts_db.get(contract_id)
    if not contract:
        return None

    file_content = contract_data.pop("file_content", None)
    changes_description = contract_data.pop("changes_description", "Updated contract")

    updated_contract = contracts_db.update(id=contract_id, obj_in=contract_data)

    if file_content:
        versions = contract_versions_db.get_multi(filters={"contract_id": contract_id})
        latest_version = max([v.version for v in versions]) if versions else 0

        file_path = save_contract_file(file_content)
        if file_path:
            contracts_db.update(id=contract_id, obj_in={"file_path": file_path})

            contract_versions_db.create(
                obj_in=ContractVersion(
                    id=len(versions) + 1,
                    contract_id=contract_id,
                    version=latest_version + 1,
                    file_path=file_path,
                    changes_description=changes_description,
                    created_by=contract_data.get("updated_by", "system"),
                )
            )

    create_audit_log(
        entity_type="contract",
        entity_id=contract_id,
        action="updated",
        user_email=contract_data.get("updated_by", "system"),
        details={
            "fields_updated": list(contract_data.keys()),
            "new_version_created": bool(file_content),
        },
    )

    return get_contract(contract_id)  # Return with versions


def delete_contract(contract_id: int) -> bool:
    """Delete a contract and its versions."""
    contract = contracts_db.get(contract_id)
    if not contract:
        return False

    versions = contract_versions_db.get_multi(filters={"contract_id": contract_id})
    for version in versions:
        contract_versions_db.delete(version.id)

        if version.file_path and os.path.exists(version.file_path):
            try:
                os.remove(version.file_path)
            except Exception:
                pass

    result = contracts_db.delete(contract_id)

    create_audit_log(
        entity_type="contract",
        entity_id=contract_id,
        action="deleted",
        user_email="system",
        details={"contract_title": contract.title, "client_id": contract.client_id},
    )

    return result


def get_contract_version(contract_id: int, version: int) -> Optional[ContractVersion]:
    """Get a specific version of a contract."""
    versions = contract_versions_db.get_multi(
        filters={"contract_id": contract_id, "version": version}
    )
    return versions[0] if versions else None


def get_contract_versions(contract_id: int) -> List[ContractVersion]:
    """Get all versions of a contract."""
    versions = contract_versions_db.get_multi(filters={"contract_id": contract_id})
    return sorted(versions, key=lambda v: v.version)


def create_workflow_template(template_data: Dict[str, Any]) -> WorkflowTemplate:
    """Create a new workflow template."""
    if "id" not in template_data:
        template_data["id"] = str(uuid.uuid4())

    template = workflow_templates_db.create(obj_in=WorkflowTemplate(**template_data))

    create_audit_log(
        entity_type="workflow_template",
        entity_id=0,  # No numeric ID
        action="created",
        user_email=template_data.get("created_by", "system"),
        details={"template_id": template.id, "template_name": template.name},
    )

    return template


def get_workflow_template(template_id: str) -> Optional[WorkflowTemplate]:
    """Get a workflow template by ID."""
    templates = workflow_templates_db.get_multi(filters={"id": template_id})
    return templates[0] if templates else None


def get_workflow_templates() -> List[WorkflowTemplate]:
    """Get all workflow templates."""
    return workflow_templates_db.get_multi()


def update_workflow_template(
    template_id: str, template_data: Dict[str, Any]
) -> Optional[WorkflowTemplate]:
    """Update a workflow template."""
    template = get_workflow_template(template_id)
    if not template:
        return None

    templates = workflow_templates_db.get_multi(filters={"id": template_id})
    if not templates:
        return None

    template_idx = templates[0].id
    updated_template = workflow_templates_db.update(
        id=template_idx, obj_in=template_data
    )

    create_audit_log(
        entity_type="workflow_template",
        entity_id=0,  # No numeric ID
        action="updated",
        user_email=template_data.get("updated_by", "system"),
        details={
            "template_id": template_id,
            "fields_updated": list(template_data.keys()),
        },
    )

    return updated_template


def delete_workflow_template(template_id: str) -> bool:
    """Delete a workflow template."""
    template = get_workflow_template(template_id)
    if not template:
        return False

    instances = workflow_instances_db.get_multi(filters={"template_id": template_id})
    if instances:
        return False

    templates = workflow_templates_db.get_multi(filters={"id": template_id})
    if not templates:
        return False

    template_idx = templates[0].id
    result = workflow_templates_db.delete(template_idx)

    create_audit_log(
        entity_type="workflow_template",
        entity_id=0,  # No numeric ID
        action="deleted",
        user_email="system",
        details={"template_id": template_id, "template_name": template.name},
    )

    return result


def create_workflow_instance(
    instance_data: Dict[str, Any],
) -> Optional[WorkflowInstance]:
    """Create a new workflow instance from a template."""
    template_id = instance_data.get("template_id")
    if not template_id:
        return None

    template = get_workflow_template(template_id)
    if not template:
        return None

    instance_data["steps"] = template.steps
    instance_data["current_step_id"] = (
        template.steps[0].step_id if template.steps else ""
    )
    instance_data["status"] = "pending"

    instance = workflow_instances_db.create(obj_in=WorkflowInstance(**instance_data))

    create_audit_log(
        entity_type="workflow_instance",
        entity_id=instance.id,
        action="created",
        user_email=instance_data.get("created_by", "system"),
        details={
            "template_id": template_id,
            "contract_id": instance_data.get("contract_id"),
        },
    )

    return instance


def get_workflow_instance(instance_id: int) -> Optional[WorkflowInstance]:
    """Get a workflow instance by ID."""
    return workflow_instances_db.get(instance_id)


def get_workflow_instances(
    skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
) -> List[WorkflowInstance]:
    """Get workflow instances with optional filtering."""
    return workflow_instances_db.get_multi(skip=skip, limit=limit, filters=filters or {})


def update_workflow_step(
    instance_id: int, step_id: str, step_data: Dict[str, Any]
) -> Optional[WorkflowInstance]:
    """Update a step in a workflow instance."""
    instance = workflow_instances_db.get(instance_id)
    if not instance:
        return None

    for i, step in enumerate(instance.steps):
        if step.step_id == step_id:
            for key, value in step_data.items():
                setattr(instance.steps[i], key, value)

            if step_data.get("is_approved") and instance.current_step_id == step_id:
                step_ids = [s.step_id for s in instance.steps]
                current_idx = step_ids.index(step_id)

                if current_idx < len(step_ids) - 1:
                    instance.current_step_id = step_ids[current_idx + 1]
                else:
                    instance.status = "approved"

            if (
                step_data.get("is_approved") is False
                and instance.current_step_id == step_id
            ):
                instance.status = "rejected"

            updated_instance = workflow_instances_db.update(
                id=instance_id,
                obj_in={
                    "steps": instance.steps,
                    "current_step_id": instance.current_step_id,
                    "status": instance.status,
                },
            )

            create_audit_log(
                entity_type="workflow_step",
                entity_id=instance_id,
                action="updated",
                user_email=step_data.get("approver_email", "system"),
                details={
                    "step_id": step_id,
                    "is_approved": step_data.get("is_approved"),
                    "comments": step_data.get("comments"),
                },
            )

            return updated_instance

    return None


def create_task(task_data: Dict[str, Any]) -> Task:
    """Create a new task."""
    task = tasks_db.create(obj_in=Task(**task_data))

    create_audit_log(
        entity_type="task",
        entity_id=task.id,
        action="created",
        user_email=task_data.get("created_by", "system"),
        details={
            "task_title": task.title,
            "assigned_to": task.assigned_to,
            "ai_generated": task.ai_generated,
        },
    )

    return task


def get_task(task_id: int) -> Optional[Task]:
    """Get a task by ID."""
    task = tasks_db.get(task_id)
    if not task:
        return None

    if task.related_contract_id:
        contract = contracts_db.get(task.related_contract_id)
        if contract:
            task.contract_title = contract.title

    if task.related_client_id:
        client = clients_db.get(task.related_client_id)
        if client:
            task.client_name = client.name

    return task


def get_tasks(
    skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
) -> List[Task]:
    """Get tasks with optional filtering."""
    tasks = tasks_db.get_multi(skip=skip, limit=limit, filters=filters or {})

    for task in tasks:
        if task.related_contract_id:
            contract = contracts_db.get(task.related_contract_id)
            if contract:
                task.contract_title = contract.title

        if task.related_client_id:
            client = clients_db.get(task.related_client_id)
            if client:
                task.client_name = client.name

    return tasks


def update_task(task_id: int, task_data: Dict[str, Any]) -> Optional[Task]:
    """Update a task."""
    task = tasks_db.get(task_id)
    if not task:
        return None

    updated_task = tasks_db.update(id=task_id, obj_in=task_data)

    create_audit_log(
        entity_type="task",
        entity_id=task_id,
        action="updated",
        user_email=task_data.get("updated_by", "system"),
        details={
            "fields_updated": list(task_data.keys()),
            "status_changed": "status" in task_data,
        },
    )

    return get_task(task_id)  # Return enriched task


def delete_task(task_id: int) -> bool:
    """Delete a task."""
    task = tasks_db.get(task_id)
    if not task:
        return False

    result = tasks_db.delete(task_id)

    create_audit_log(
        entity_type="task",
        entity_id=task_id,
        action="deleted",
        user_email="system",
        details={"task_title": task.title},
    )

    return result


def create_audit_log(
    entity_type: str,
    entity_id: int,
    action: str,
    user_email: Optional[str] = None,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """Create a new audit log entry."""
    audit_log = audit_logs_db.create(
        obj_in=AuditLog(
            id=len(audit_logs_db.get_multi()) + 1,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            user_email=user_email,
            details=details or {},
            timestamp=datetime.utcnow(),
        )
    )

    return audit_log


def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    action: Optional[str] = None,
    user_email: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[AuditLog]:
    """Get audit logs with filtering options."""
    filters = {}

    if entity_type:
        filters["entity_type"] = entity_type

    if entity_id is not None:
        filters["entity_id"] = entity_id

    if action:
        filters["action"] = action

    if user_email:
        filters["user_email"] = user_email

    logs = audit_logs_db.get_multi(skip=skip, limit=limit, filters=filters)

    if start_date or end_date:
        filtered_logs = []
        for log in logs:
            if start_date and log.timestamp < start_date:
                continue
            if end_date and log.timestamp > end_date:
                continue
            filtered_logs.append(log)
        return filtered_logs

    return logs


def init_legal_db():
    """Initialize the legal database with sample data."""
    if not workflow_templates_db.get_multi():
        create_workflow_template(
            {
                "id": "contract-approval",
                "name": "Contract Approval Workflow",
                "description": "Standard approval process for new contracts",
                "steps": [
                    {
                        "step_id": "legal-review",
                        "role": "Legal Lead",
                        "approver_email": "legal@example.com",
                        "is_approved": False,
                    },
                    {
                        "step_id": "finance-review",
                        "role": "CFO",
                        "approver_email": "cfo@example.com",
                        "is_approved": False,
                    },
                    {
                        "step_id": "executive-approval",
                        "role": "CEO",
                        "approver_email": "ceo@example.com",
                        "is_approved": False,
                    },
                ],
                "created_at": datetime.utcnow(),
            }
        )

        create_workflow_template(
            {
                "id": "nda-approval",
                "name": "NDA Approval Workflow",
                "description": "Streamlined approval process for NDAs",
                "steps": [
                    {
                        "step_id": "legal-review",
                        "role": "Legal Lead",
                        "approver_email": "legal@example.com",
                        "is_approved": False,
                    },
                    {
                        "step_id": "executive-approval",
                        "role": "CEO",
                        "approver_email": "ceo@example.com",
                        "is_approved": False,
                    },
                ],
                "created_at": datetime.utcnow(),
            }
        )
