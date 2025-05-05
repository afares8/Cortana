from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from pydantic import EmailStr

from app.services.workflows.models.workflow import WorkflowTemplate, WorkflowInstance
from app.services.workflows.services.workflow_service import workflow_service

router = APIRouter()

@router.post("/templates", response_model=WorkflowTemplate, status_code=201)
async def create_workflow_template_endpoint(template: Dict[str, Any] = Body(...)):
    """Create a new workflow template."""
    return await workflow_service.create_workflow_template(template)

@router.get("/templates", response_model=List[WorkflowTemplate])
async def get_workflow_templates_endpoint():
    """Get all workflow templates."""
    return await workflow_service.get_workflow_templates()

@router.get("/templates/{template_id}", response_model=WorkflowTemplate)
async def get_workflow_template_endpoint(template_id: str = Path(...)):
    """Get a workflow template by ID."""
    template = await workflow_service.get_workflow_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return template

@router.put("/templates/{template_id}", response_model=WorkflowTemplate)
async def update_workflow_template_endpoint(
    template_id: str = Path(...),
    template_update: Dict[str, Any] = Body(...)
):
    """Update a workflow template."""
    template = await workflow_service.update_workflow_template(template_id, template_update)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return template

@router.delete("/templates/{template_id}", response_model=Dict[str, bool])
async def delete_workflow_template_endpoint(template_id: str = Path(...)):
    """Delete a workflow template."""
    result = await workflow_service.delete_workflow_template(template_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow template not found or in use")
    return {"success": True}

@router.post("/instances", response_model=WorkflowInstance, status_code=201)
async def create_workflow_instance_endpoint(instance_data: Dict[str, Any] = Body(...)):
    """Create a new workflow instance from a template."""
    instance = await workflow_service.create_workflow_instance(instance_data)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return instance

@router.get("/instances", response_model=List[WorkflowInstance])
async def get_workflow_instances_endpoint(
    skip: int = 0,
    limit: int = 100,
    template_id: Optional[str] = None,
    contract_id: Optional[int] = None,
    status: Optional[str] = None
):
    """Get workflow instances with optional filtering."""
    filters = {}
    if template_id:
        filters["template_id"] = template_id
    if contract_id:
        filters["contract_id"] = contract_id
    if status:
        filters["status"] = status
    
    return await workflow_service.get_workflow_instances(skip=skip, limit=limit, filters=filters)

@router.get("/instances/{instance_id}", response_model=WorkflowInstance)
async def get_workflow_instance_endpoint(instance_id: int = Path(..., gt=0)):
    """Get a workflow instance by ID."""
    instance = await workflow_service.get_workflow_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    return instance

@router.put("/instances/{instance_id}/steps/{step_id}", response_model=WorkflowInstance)
async def update_workflow_step_endpoint(
    instance_id: int = Path(..., gt=0),
    step_id: str = Path(...),
    step_data: Dict[str, Any] = Body(...)
):
    """Update a step in a workflow instance."""
    instance = await workflow_service.update_workflow_step(instance_id, step_id, step_data)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance or step not found")
    return instance
