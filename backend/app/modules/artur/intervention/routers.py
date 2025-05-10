from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.modules.artur.intervention.schemas import (
    ArturInterventionOut, 
    ArturInterventionCreate, 
    ArturInterventionUpdate,
    ExecuteInterventionRequest
)
from app.modules.artur.intervention.services import intervention_service

router = APIRouter()

@router.get("/interventions", response_model=List[ArturInterventionOut])
async def list_interventions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    intervention_type: Optional[str] = None,
    department_id: Optional[int] = None
):
    """List Artur interventions with optional filtering."""
    return await intervention_service.get_interventions(
        skip=skip,
        limit=limit,
        status=status,
        intervention_type=intervention_type,
        department_id=department_id
    )

@router.get("/interventions/{intervention_id}", response_model=ArturInterventionOut)
async def get_intervention_by_id(intervention_id: int):
    """Get a specific Artur intervention by ID."""
    intervention = await intervention_service.get_intervention_by_id(intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    return intervention

@router.post("/prepare", response_model=ArturInterventionOut)
async def prepare_intervention(request: ExecuteInterventionRequest):
    """Prepare an intervention based on a suggestion."""
    intervention = await intervention_service.prepare_intervention(request.suggestion_id)
    if not intervention:
        raise HTTPException(status_code=404, detail="Failed to prepare intervention")
    return intervention

@router.post("/execute/{intervention_id}")
async def execute_intervention(intervention_id: int, user_id: Optional[int] = None):
    """Execute an approved intervention."""
    success = await intervention_service.execute_intervention(intervention_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to execute intervention")
    return {"status": "success", "message": "Intervention executed successfully"}

@router.post("/rollback/{intervention_id}")
async def rollback_intervention(intervention_id: int):
    """Rollback a completed intervention."""
    success = await intervention_service.rollback_intervention(intervention_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to rollback intervention")
    return {"status": "success", "message": "Intervention rolled back successfully"}
