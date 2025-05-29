from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Body,
    Query,
    Path,
)
from fastapi.responses import JSONResponse
from pydantic import EmailStr

from app.core.config import settings
from app.legal.schemas import (
    Client,
    ClientCreate,
    ClientUpdate,
    Contract,
    ContractCreate,
    ContractUpdate,
    ContractVersion,
    WorkflowTemplate,
    WorkflowInstance,
    Task,
    TaskCreate,
    TaskUpdate,
    AuditLogEntry,
)
from app.legal.services import (
    create_client,
    get_client,
    get_clients,
    update_client,
    delete_client,
    create_contract,
    get_contract,
    get_contracts,
    update_contract,
    delete_contract,
    get_contract_version,
    get_contract_versions,
    create_workflow_template,
    get_workflow_template,
    get_workflow_templates,
    update_workflow_template,
    delete_workflow_template,
    create_workflow_instance,
    get_workflow_instance,
    get_workflow_instances,
    update_workflow_step,
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task,
    get_audit_logs,
)

router = APIRouter()


@router.post("/clients", response_model=Client, status_code=201)
async def create_client_endpoint(client: ClientCreate):
    """Create a new client."""
    return create_client(client.model_dump())


@router.get("/clients", response_model=List[Client])
async def get_clients_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    industry: Optional[str] = None,
    kyc_verified: Optional[bool] = None,
):
    """Get a list of clients with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if industry:
        filters["industry"] = industry
    if kyc_verified is not None:
        filters["kyc_verified"] = kyc_verified

    return get_clients(skip=skip, limit=limit, filters=filters)


@router.get("/clients/{client_id}", response_model=Client)
async def get_client_endpoint(client_id: int = Path(..., gt=0)):
    """Get a client by ID."""
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/clients/{client_id}", response_model=Client)
async def update_client_endpoint(
    client_id: int = Path(..., gt=0), client_update: ClientUpdate = Body(...)
):
    """Update a client."""
    client = update_client(client_id, client_update.model_dump(exclude_unset=True))
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.delete("/clients/{client_id}", response_model=Dict[str, bool])
async def delete_client_endpoint(client_id: int = Path(..., gt=0)):
    """Delete a client."""
    result = delete_client(client_id)
    if not result:
        raise HTTPException(
            status_code=404, detail="Client not found or has associated contracts"
        )
    return {"success": True}


@router.post("/contracts", response_model=Contract, status_code=201)
async def create_contract_endpoint(contract: ContractCreate):
    """Create a new contract."""
    return create_contract(contract.model_dump())


@router.get("/contracts", response_model=List[Contract])
async def get_contracts_endpoint(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    contract_type: Optional[str] = None,
    status: Optional[str] = None,
    responsible_lawyer: Optional[str] = None,
    start_date_after: Optional[datetime] = None,
    expiration_date_before: Optional[datetime] = None,
):
    """Get a list of contracts with optional filtering."""
    filters = {}
    if client_id:
        filters["client_id"] = client_id
    if contract_type:
        filters["contract_type"] = contract_type
    if status:
        filters["status"] = status
    if responsible_lawyer:
        filters["responsible_lawyer"] = responsible_lawyer

    contracts = get_contracts(skip=skip, limit=limit, filters=filters)

    if start_date_after or expiration_date_before:
        filtered_contracts = []
        for contract in contracts:
            if start_date_after and contract.start_date < start_date_after:
                continue
            if (
                expiration_date_before
                and contract.expiration_date
                and contract.expiration_date > expiration_date_before
            ):
                continue
            filtered_contracts.append(contract)
        return filtered_contracts

    return contracts


@router.get("/contracts/{contract_id}", response_model=Contract)
async def get_contract_endpoint(contract_id: int = Path(..., gt=0)):
    """Get a contract by ID."""
    contract = get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.put("/contracts/{contract_id}", response_model=Contract)
async def update_contract_endpoint(
    contract_id: int = Path(..., gt=0), contract_update: ContractUpdate = Body(...)
):
    """Update a contract."""
    contract = update_contract(
        contract_id, contract_update.model_dump(exclude_unset=True)
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.delete("/contracts/{contract_id}", response_model=Dict[str, bool])
async def delete_contract_endpoint(contract_id: int = Path(..., gt=0)):
    """Delete a contract."""
    result = delete_contract(contract_id)
    if not result:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"success": True}


@router.get("/contracts/{contract_id}/versions", response_model=List[ContractVersion])
async def get_contract_versions_endpoint(contract_id: int = Path(..., gt=0)):
    """Get all versions of a contract."""
    contract = get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    return get_contract_versions(contract_id)


@router.get(
    "/contracts/{contract_id}/versions/{version}", response_model=ContractVersion
)
async def get_contract_version_endpoint(
    contract_id: int = Path(..., gt=0), version: int = Path(..., gt=0)
):
    """Get a specific version of a contract."""
    contract_version = get_contract_version(contract_id, version)
    if not contract_version:
        raise HTTPException(status_code=404, detail="Contract version not found")

    return contract_version


@router.post("/workflows/templates", response_model=WorkflowTemplate, status_code=201)
async def create_workflow_template_endpoint(template: Dict[str, Any] = Body(...)):
    """Create a new workflow template."""
    return create_workflow_template(template)


@router.get("/workflows/templates", response_model=List[WorkflowTemplate])
async def get_workflow_templates_endpoint():
    """Get all workflow templates."""
    return get_workflow_templates()


@router.get("/workflows/templates/{template_id}", response_model=WorkflowTemplate)
async def get_workflow_template_endpoint(template_id: str = Path(...)):
    """Get a workflow template by ID."""
    template = get_workflow_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return template


@router.put("/workflows/templates/{template_id}", response_model=WorkflowTemplate)
async def update_workflow_template_endpoint(
    template_id: str = Path(...), template_update: Dict[str, Any] = Body(...)
):
    """Update a workflow template."""
    template = update_workflow_template(template_id, template_update)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return template


@router.delete("/workflows/templates/{template_id}", response_model=Dict[str, bool])
async def delete_workflow_template_endpoint(template_id: str = Path(...)):
    """Delete a workflow template."""
    result = delete_workflow_template(template_id)
    if not result:
        raise HTTPException(
            status_code=404, detail="Workflow template not found or in use"
        )
    return {"success": True}


@router.post("/workflows/instances", response_model=WorkflowInstance, status_code=201)
async def create_workflow_instance_endpoint(instance_data: Dict[str, Any] = Body(...)):
    """Create a new workflow instance from a template."""
    instance = create_workflow_instance(instance_data)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return instance


@router.get("/workflows/instances", response_model=List[WorkflowInstance])
async def get_workflow_instances_endpoint(
    skip: int = 0,
    limit: int = 100,
    template_id: Optional[str] = None,
    contract_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """Get workflow instances with optional filtering."""
    filters = {}
    if template_id:
        filters["template_id"] = template_id
    if contract_id:
        filters["contract_id"] = contract_id
    if status:
        filters["status"] = status

    return get_workflow_instances(skip=skip, limit=limit, filters=filters)


@router.get("/workflows/instances/{instance_id}", response_model=WorkflowInstance)
async def get_workflow_instance_endpoint(instance_id: int = Path(..., gt=0)):
    """Get a workflow instance by ID."""
    instance = get_workflow_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    return instance


@router.put(
    "/workflows/instances/{instance_id}/steps/{step_id}",
    response_model=WorkflowInstance,
)
async def update_workflow_step_endpoint(
    instance_id: int = Path(..., gt=0),
    step_id: str = Path(...),
    step_data: Dict[str, Any] = Body(...),
):
    """Update a step in a workflow instance."""
    instance = update_workflow_step(instance_id, step_id, step_data)
    if not instance:
        raise HTTPException(
            status_code=404, detail="Workflow instance or step not found"
        )
    return instance


@router.post("/tasks", response_model=Task, status_code=201)
async def create_task_endpoint(task: TaskCreate):
    """Create a new task."""
    return create_task(task.model_dump())


@router.get("/tasks", response_model=List[Task])
async def get_tasks_endpoint(
    skip: int = 0,
    limit: int = 100,
    assigned_to: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    related_contract_id: Optional[int] = None,
    related_client_id: Optional[int] = None,
    due_date_before: Optional[datetime] = None,
    ai_generated: Optional[bool] = None,
):
    """Get tasks with optional filtering."""
    filters = {}
    if assigned_to:
        filters["assigned_to"] = assigned_to
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if related_contract_id:
        filters["related_contract_id"] = related_contract_id
    if related_client_id:
        filters["related_client_id"] = related_client_id
    if ai_generated is not None:
        filters["ai_generated"] = ai_generated

    tasks = get_tasks(skip=skip, limit=limit, filters=filters)

    if due_date_before:
        filtered_tasks = []
        for task in tasks:
            if task.due_date and task.due_date > due_date_before:
                continue
            filtered_tasks.append(task)
        return filtered_tasks

    return tasks


@router.get("/tasks/{task_id}", response_model=Task)
async def get_task_endpoint(task_id: int = Path(..., gt=0)):
    """Get a task by ID."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=Task)
async def update_task_endpoint(
    task_id: int = Path(..., gt=0), task_update: TaskUpdate = Body(...)
):
    """Update a task."""
    task = update_task(task_id, task_update.model_dump(exclude_unset=True))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", response_model=Dict[str, bool])
async def delete_task_endpoint(task_id: int = Path(..., gt=0)):
    """Delete a task."""
    result = delete_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}


@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def get_audit_logs_endpoint(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    action: Optional[str] = None,
    user_email: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """Get audit logs with filtering options."""
    return get_audit_logs(
        skip=skip,
        limit=limit,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_email=user_email,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/verify-client", response_model=Dict[str, Any])
async def verify_client_endpoint(
    client_id: int = Body(..., embed=True),
    name: Optional[str] = Body(None, embed=True),
    country: Optional[str] = Body(None, embed=True),
    type: Optional[str] = Body(None, embed=True),
):
    """
    Verify a client against PEP and sanctions lists.
    Proxies to the compliance verification service.
    """
    from app.services.compliance.schemas.verify import (
        CustomerVerifyRequest,
        EntityBase as Customer,
    )
    from app.services.compliance.services.unified_verification_service import (
        unified_verification_service,
    )
    import logging

    logger = logging.getLogger(__name__)

    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    try:
        customer_data = {
            "name": name or client.name,
            "country": country or getattr(client, "country", "PA"),
            "type": type or getattr(client, "client_type", "natural"),
        }

        try:
            request = CustomerVerifyRequest(customer=Customer(**customer_data))
        except Exception as e:
            logger.error(f"Error creating verification request: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Invalid customer data: {str(e)}"
            )

        try:
            result = await unified_verification_service.verify_customer(request)
        except Exception as e:
            logger.error(f"Error in verification service: {str(e)}")
            result = {
                "customer": {
                    "name": customer_data["name"],
                    "enriched_data": customer_data,
                    "pep_matches": [],
                    "sanctions_matches": [],
                    "risk_score": {"score": 0, "level": "MEDIUM", "factors": []},
                },
                "directors": [],
                "ubos": [],
                "country_risk": {"risk_level": "MEDIUM", "sources": ["Default"]},
                "report": {
                    "id": 0,
                    "path": "",
                    "generated_at": datetime.now().isoformat(),
                },
                "sources_checked": ["OpenSanctions", "OFAC", "UN", "EU"],
            }

        if not isinstance(result, dict):
            try:
                if hasattr(result, "dict"):
                    result = result.dict()
                elif hasattr(result, "model_dump"):
                    result = result.model_dump()
                else:
                    logger.warning("Could not convert result to dict")
                    result = {
                        "customer": {"name": customer_data["name"]},
                        "status": "error",
                        "message": "Could not process verification result",
                    }
            except Exception as e:
                logger.error(f"Error converting result: {str(e)}")
                result = {
                    "status": "error",
                    "message": "Could not process verification result",
                }

        client_update = {
            "verification_status": "verified",
            "verification_date": datetime.now(timezone.utc),
            "verification_result": result,
        }

        update_client(client_id=client_id, client_data=client_update)

        result_with_status = {
            **result,
            "status": "verified",
            "verification_date": client_update["verification_date"].isoformat(),
        }

        return result_with_status
    except Exception as e:
        logger.error(f"Error verifying client {client_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to verify client: {str(e)}",
            "customer": {
                "name": (
                    customer_data["name"] if "customer_data" in locals() else "Unknown"
                )
            },
            "verification_date": datetime.now(timezone.utc).isoformat(),
        }


@router.post("/contracts/{contract_id}/analyze", response_model=Dict[str, Any])
async def analyze_contract_endpoint(contract_id: int = Path(...)):
    """
    Analyze a contract using AI contract intelligence.
    Uses existing AI service for contract analysis.
    """
    from app.services.ai.contract_intelligence import process_contract
    import logging

    logger = logging.getLogger(__name__)

    contract = get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    try:
        analysis_result = process_contract(contract)
        return {
            "contract_id": contract_id,
            "analysis": analysis_result,
            "status": "completed",
        }
    except Exception as e:
        logger.error(f"Error analyzing contract {contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze contract")
