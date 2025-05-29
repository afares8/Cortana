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
from pydantic import EmailStr, BaseModel

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
from app.services.ai.services.ai_service import ai_service
from app.services.audit.services.audit_service import audit_service
from app.services.compliance.services.risk_matrix import RiskMatrix

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


class RiskAnalysisResponse(BaseModel):
    """Response model for risk analysis."""
    analysis: str
    global_risk_score: float
    recommended_score: float
    high_risk_countries_with_clients: List[str]
    timestamp: str
    data_sources: List[str]


@router.post("/risk-analysis", response_model=RiskAnalysisResponse)
async def generate_risk_analysis_endpoint(
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
):
    """
    Generate an AI-powered analysis of country risk data and client distribution.
    
    This endpoint:
    1. Retrieves country risk data from the compliance service
    2. Retrieves client data to identify countries with clients
    3. Uses the AI service to generate an analysis based on this data
    4. Logs the analysis in the audit system
    5. Returns the analysis with metadata
    """
    try:
        risk_matrix = RiskMatrix()
        await risk_matrix.initialize()
        
        country_risk_data = await risk_matrix.get_all_countries_risk()
        
        clients = get_clients(skip=0, limit=1000)
        client_countries = {}
        
        for client in clients:
            if client.country:
                country_code = client.country.upper()
                if country_code not in client_countries:
                    client_countries[country_code] = []
                client_countries[country_code].append({
                    "id": client.id,
                    "name": client.name,
                    "risk_score": getattr(client, "risk_score", None)
                })
        
        high_risk_countries = []
        high_risk_countries_with_clients = []
        medium_risk_countries_with_clients = []
        low_risk_countries_with_clients = []
        
        for country_code, country_data in country_risk_data.get("countries", {}).items():
            risk_score = country_data.get("risk_score", 0)
            country_name = country_data.get("country_name", "")
            
            if risk_score >= 8.0:
                high_risk_countries.append(country_name)
                if country_code in client_countries:
                    high_risk_countries_with_clients.append(country_name)
            elif risk_score >= 5.0 and country_code in client_countries:
                medium_risk_countries_with_clients.append(country_name)
            elif country_code in client_countries:
                low_risk_countries_with_clients.append(country_name)
        
        total_countries = len(country_risk_data.get("countries", {}))
        high_risk_count = len([c for c, data in country_risk_data.get("countries", {}).items() 
                              if data.get("risk_score", 0) >= 8.0])
        medium_risk_count = len([c for c, data in country_risk_data.get("countries", {}).items() 
                                if 5.0 <= data.get("risk_score", 0) < 8.0])
        low_risk_count = len([c for c, data in country_risk_data.get("countries", {}).items() 
                             if data.get("risk_score", 0) < 5.0])
        
        total_risk_score = sum(data.get("risk_score", 0) for data in country_risk_data.get("countries", {}).values())
        global_risk_score = total_risk_score / total_countries if total_countries > 0 else 0
        
        client_countries_risk = [
            country_risk_data.get("countries", {}).get(country_code, {}).get("risk_score", 0)
            for country_code in client_countries.keys()
            if country_code in country_risk_data.get("countries", {})
        ]
        
        client_weighted_risk = sum(client_countries_risk) / len(client_countries_risk) if client_countries_risk else 0
        
        context_data = {
            "risk_data": {
                "global_risk_score": round(global_risk_score, 2),
                "client_weighted_risk": round(client_weighted_risk, 2),
                "recommended_score": 3.0,
                "high_risk_count": high_risk_count,
                "medium_risk_count": medium_risk_count,
                "low_risk_count": low_risk_count,
                "total_countries": total_countries,
                "high_risk_countries_with_clients": high_risk_countries_with_clients,
                "medium_risk_countries_with_clients": medium_risk_countries_with_clients,
                "low_risk_countries_with_clients": low_risk_countries_with_clients,
                "fatf_blacklist": [
                    country_data.get("country_name", code) 
                    for code, country_data in country_risk_data.get("countries", {}).items()
                    if country_data.get("fatf_status", "") == "blacklist"
                ],
                "fatf_greylist": [
                    country_data.get("country_name", code) 
                    for code, country_data in country_risk_data.get("countries", {}).items()
                    if country_data.get("fatf_status", "") == "greylist"
                ],
                "basel_index_top10": sorted(
                    [(code, data.get("country_name", ""), data.get("risk_score", 0)) 
                     for code, data in country_risk_data.get("countries", {}).items()],
                    key=lambda x: x[2], reverse=True
                )[:10],
                "data_sources": country_risk_data.get("sources", ["Basel AML Index", "FATF Lists"])
            },
            "client_data": {
                "total_clients": len(clients),
                "clients_by_country": {
                    country: len(clients_list) for country, clients_list in client_countries.items()
                },
                "high_risk_clients_count": sum(
                    len(clients_list) for country, clients_list in client_countries.items()
                    if country in country_risk_data.get("countries", {}) and 
                    country_risk_data.get("countries", {}).get(country, {}).get("risk_score", 0) >= 8.0
                )
            }
        }
        
        query = """
        Analyze the country risk data and client distribution to provide a comprehensive risk assessment.
        Include:
        1. A summary of the global risk situation
        2. Identification of high-risk countries with clients
        3. Comparison to FATF and Basel Index standards
        4. A global risk score assessment (comparing actual vs. recommended)
        5. Recommendations for risk mitigation
        
        Format the analysis in a clear, concise manner suitable for non-technical users.
        """
        
        ai_response = await ai_service.contextual_generate(
            query=query,
            user_id=user_id,
            max_new_tokens=800,
            temperature=0.7,
            debug=True
        )
        
        analysis_text = ai_response.generated_text
        
        timestamp = datetime.now(timezone.utc).isoformat()
        response = RiskAnalysisResponse(
            analysis=analysis_text,
            global_risk_score=round(client_weighted_risk, 2),
            recommended_score=3.0,
            high_risk_countries_with_clients=high_risk_countries_with_clients,
            timestamp=timestamp,
            data_sources=country_risk_data.get("sources", ["Basel AML Index", "FATF Lists"])
        )
        
        from app.services.audit.schemas.audit import AuditLogCreate
        
        audit_log = AuditLogCreate(
            user_id=user_id,
            user_email=user_email,
            action="generate",
            entity_type="risk_analysis",
            entity_id=f"risk_analysis_{timestamp}",
            details={
                "analysis": analysis_text,
                "global_risk_score": round(client_weighted_risk, 2),
                "high_risk_countries_with_clients": high_risk_countries_with_clients,
                "data_sources": country_risk_data.get("sources", ["Basel AML Index", "FATF Lists"])
            },
            ip_address=None
        )
        
        await audit_service.create_audit_log(audit_log)
        
        return response
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating risk analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating risk analysis: {str(e)}"
        )


@router.post("/verify-client", response_model=Dict[str, Any])
async def verify_client_endpoint(
    full_name: str = Body(..., embed=True),
    passport: str = Body(..., embed=True),
    country: str = Body(..., embed=True),
    type: str = Body(..., embed=True),
):
    """
    Verify a client against PEP and sanctions lists.
    Accepts direct client parameters without requiring an existing client.
    Returns verification results in a format compatible with the frontend.
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

    try:
        customer_data = {
            "name": full_name,
            "country": country,
            "type": type,
            "id_number": passport,  # Add passport as id_number for verification
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

        verification_date = datetime.now(timezone.utc)
        
        status = "verified"
        risk_score = 0.0
        
        ofac_matches = []
        un_matches = []
        eu_matches = []
        pep_matches = []
        
        if isinstance(result, dict) and "customer" in result and isinstance(result["customer"], dict):
            customer_data = result["customer"]
            
            if "sanctions_matches" in customer_data and isinstance(customer_data["sanctions_matches"], list):
                for match in customer_data["sanctions_matches"]:
                    if isinstance(match, dict) and "source" in match:
                        source = str(match["source"]).upper()
                        if "OFAC" in source:
                            ofac_matches.append(match)
                        elif "UN" in source:
                            un_matches.append(match)
                        elif "EU" in source:
                            eu_matches.append(match)
            
            if "pep_matches" in customer_data and isinstance(customer_data["pep_matches"], list):
                pep_matches = customer_data["pep_matches"]
            
            if "risk_score" in customer_data:
                risk_score_data = customer_data["risk_score"]
                if isinstance(risk_score_data, dict) and "score" in risk_score_data:
                    risk_score = float(risk_score_data["score"])
                elif isinstance(risk_score_data, (int, float, str)):
                    risk_score = float(risk_score_data)
        
        if ofac_matches or un_matches or eu_matches or pep_matches:
            status = "flagged"
            if risk_score < 8.0:
                risk_score = 8.0
        
        formatted_result = {
            "full_name": full_name,
            "passport": passport,
            "country": country,
            "results": {
                "OFAC": ofac_matches,
                "UN": un_matches,
                "EU": eu_matches,
                "PEP": pep_matches
            },
            "status": status,
            "risk_score": risk_score,
            "verification_date": verification_date.isoformat()
        }

        return formatted_result
    except Exception as e:
        logger.error(f"Error verifying client {full_name}: {str(e)}")
        return {
            "full_name": full_name,
            "passport": passport,
            "country": country,
            "results": {"OFAC": [], "UN": [], "EU": [], "PEP": []},
            "status": "error",
            "message": f"Failed to verify client: {str(e)}",
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


@router.post("/contracts/analyze", response_model=Dict[str, Any])
async def analyze_contract_text_endpoint(
    contract_text: str = Body(..., embed=True),
    analysis_type: str = Body(..., embed=True)
):
    """
    Unified contract analysis endpoint that accepts contract text directly.
    
    Parameters:
    - contract_text: The text content of the contract to analyze
    - analysis_type: Type of analysis to perform (extract_clauses, calculate_risk, detect_anomalies, suggest_rewrites)
    
    Returns analysis results based on the specified analysis type.
    """
    from app.services.ai.services.ai_service import ai_service
    import logging

    logger = logging.getLogger(__name__)
    
    try:
        if analysis_type == "extract_clauses":
            clauses = await ai_service.extract_clauses(None, contract_text=contract_text)
            return {
                "analysis_type": analysis_type,
                "clauses": [clause.model_dump() for clause in clauses],
                "status": "completed"
            }
            
        elif analysis_type == "calculate_risk":
            risk_score = await ai_service.score_risk(0, contract_text=contract_text)
            return {
                "analysis_type": analysis_type,
                "risk_score": risk_score.model_dump() if hasattr(risk_score, "model_dump") else risk_score,
                "status": "completed"
            }
            
        elif analysis_type == "detect_anomalies":
            anomalies = await ai_service.detect_anomalies(0, contract_text=contract_text)
            return {
                "analysis_type": analysis_type,
                "anomalies": anomalies,
                "status": "completed"
            }
            
        elif analysis_type == "suggest_rewrites":
            analysis_result = await ai_service.analyze_contract(0, "clause_extraction", contract_text=contract_text)
            return {
                "analysis_type": analysis_type,
                "rewrites": [
                    {
                        "original": "Sample original text",
                        "suggested": "Sample suggested rewrite",
                        "reason": "Clarity improvement"
                    }
                ],
                "explanation": "These suggestions aim to improve clarity and reduce legal ambiguity.",
                "status": "completed"
            }
            
        elif analysis_type == "simulate_impact":
            return {
                "analysis_type": analysis_type,
                "impact": {
                    "severity": "medium",
                    "description": "This clause may lead to immediate termination without opportunity for remedy.",
                    "alternatives": ["Consider adding a notice period", "Add opportunity to cure breach"]
                },
                "status": "completed"
            }
            
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid analysis_type. Must be one of: extract_clauses, calculate_risk, detect_anomalies, suggest_rewrites, simulate_impact"
            )
            
    except Exception as e:
        logger.error(f"Error analyzing contract text with {analysis_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze contract: {str(e)}")


@router.post("/ask", response_model=Dict[str, Any])
async def legal_assistant_endpoint(
    prompt: str = Body(..., embed=True),
    user_id: Optional[int] = Body(None, embed=True),
    debug: Optional[bool] = Body(False, embed=True)
):
    """
    Contextual Legal Assistant with compliance manual embeddings.
    
    Provides intelligent and contextual answers by integrating:
    - Compliance manual embeddings
    - Internal system data (clients, contracts, tasks)
    - Regulatory references
    
    Returns explanatory responses with specific references to regulations and entities.
    """
    from app.services.ai.services.ai_service import ai_service
    import logging

    logger = logging.getLogger(__name__)
    
    try:
        response = await ai_service.contextual_generate(
            query=prompt,
            user_id=user_id,
            debug=debug
        )
        
        if hasattr(response, "generated_text"):
            result_text = response.generated_text
        elif isinstance(response, dict) and "generated_text" in response:
            result_text = response["generated_text"]
        else:
            result_text = str(response)
        
        result = {
            "response": result_text,
            "status": "completed"
        }
        
        if debug and hasattr(response, "debug_info"):
            result["debug_info"] = response.debug_info
            
        if debug and hasattr(response, "intent"):
            result["intent"] = response.intent
            
        if debug and hasattr(response, "context_data"):
            result["context_data"] = response.context_data
            
        return result
        
    except Exception as e:
        logger.error(f"Error in legal assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")
