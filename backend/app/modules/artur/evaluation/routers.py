from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.modules.artur.evaluation.schemas import ArturSuggestionOut, ArturSuggestionCreate, ArturSuggestionUpdate
from app.modules.artur.evaluation.services import evaluation_service
from app.modules.artur.observation.scheduler import observation_scheduler

router = APIRouter()

@router.get("/suggestions", response_model=List[ArturSuggestionOut])
async def list_suggestions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    source: Optional[str] = None,
    department_id: Optional[int] = None,
    min_confidence: Optional[float] = None
):
    """List Artur suggestions with optional filtering."""
    return await evaluation_service.get_suggestions(
        skip=skip,
        limit=limit,
        status=status,
        source=source,
        department_id=department_id,
        min_confidence=min_confidence
    )

@router.get("/suggestions/{suggestion_id}", response_model=ArturSuggestionOut)
async def get_suggestion_by_id(suggestion_id: int):
    """Get a specific Artur suggestion by ID."""
    suggestion = await evaluation_service.get_suggestion_by_id(suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return suggestion

@router.post("/suggestions", response_model=ArturSuggestionOut)
async def create_suggestion(suggestion: ArturSuggestionCreate):
    """Manually create an Artur suggestion."""
    return await evaluation_service.create_suggestion(suggestion.dict())

@router.patch("/suggestions/{suggestion_id}", response_model=ArturSuggestionOut)
async def update_suggestion_status(suggestion_id: int, update: ArturSuggestionUpdate):
    """Update the status of an Artur suggestion."""
    suggestion = await evaluation_service.update_suggestion_status(suggestion_id, update.status)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return suggestion

@router.post("/run-evaluation-cycle")
async def run_evaluation_cycle():
    """Manually trigger an evaluation cycle."""
    await observation_scheduler.run_manual_evaluation_cycle()
    return {"status": "success", "message": "Evaluation cycle triggered"}
