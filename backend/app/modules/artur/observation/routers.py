from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.modules.artur.observation.schemas import ArturInsightOut, ArturInsightCreate
from app.modules.artur.observation.services import observation_service
from app.modules.artur.observation.scheduler import observation_scheduler

router = APIRouter()

@router.get("/insights", response_model=List[ArturInsightOut])
async def list_insights(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    entity_type: Optional[str] = None,
    department_id: Optional[int] = None
):
    """List Artur insights with optional filtering."""
    return await observation_service.get_insights(
        skip=skip,
        limit=limit,
        category=category,
        entity_type=entity_type,
        department_id=department_id
    )

@router.get("/insights/{insight_id}", response_model=ArturInsightOut)
async def get_insight_by_id(insight_id: int):
    """Get a specific Artur insight by ID."""
    insight = await observation_service.get_insight_by_id(insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight

@router.post("/insights", response_model=ArturInsightOut)
async def create_insight(insight: ArturInsightCreate):
    """Manually create an Artur insight."""
    return await observation_service.create_insight(insight.dict())

@router.post("/run-observation-cycle")
async def run_observation_cycle():
    """Manually trigger an observation cycle."""
    await observation_scheduler.run_manual_observation_cycle()
    return {"status": "success", "message": "Observation cycle triggered"}
