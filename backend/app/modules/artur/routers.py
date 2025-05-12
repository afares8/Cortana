from fastapi import APIRouter, Query, Body
from typing import List, Optional, Dict, Any
from datetime import date

from app.modules.artur.observation.routers import router as observation_router
from app.modules.artur.evaluation.routers import router as evaluation_router
from app.modules.artur.intervention.routers import router as intervention_router
from app.modules.artur.simulation.routers import router as simulation_router
from app.modules.artur.dashboard.routers import router as dashboard_router

from app.modules.artur.dashboard.services import dashboard_service
from app.modules.artur.intervention.services import intervention_service
from app.modules.artur.simulation.services import simulation_service
from app.modules.artur.evaluation.services import evaluation_service

from app.modules.artur.dashboard.schemas import DepartmentHealthOut, HeatmapDataOut, PredictionsOut
from app.modules.artur.intervention.schemas import InterventionLogOut
from app.modules.artur.simulation.schemas import SimulationResultOut
from app.modules.artur.evaluation.schemas import ArturSuggestionOut

router = APIRouter()

router.include_router(observation_router, prefix="/observation", tags=["artur-observation"])
router.include_router(evaluation_router, prefix="/evaluation", tags=["artur-evaluation"])
router.include_router(intervention_router, prefix="/intervention", tags=["artur-intervention"])
router.include_router(simulation_router, prefix="/simulation", tags=["artur-simulation"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["artur-dashboard"])

@router.get("/department-health", response_model=List[DepartmentHealthOut], tags=["artur-dashboard"])
async def get_department_health(
    department_id: Optional[int] = Query(None, description="Filter by department ID")
):
    """
    Get health metrics for departments monitored by Artur.
    """
    return await dashboard_service.get_department_health(department_id)

@router.get("/interventions/logs", response_model=List[InterventionLogOut], tags=["artur-intervention"])
async def get_intervention_logs(
    from_date: Optional[date] = Query(None, description="Filter by start date"),
    to_date: Optional[date] = Query(None, description="Filter by end date"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type")
):
    """
    Get intervention logs with filtering options.
    
    This endpoint returns a chronological list of Artur's actions and interventions
    with detailed explanations and context.
    """
    return await intervention_service.get_intervention_logs(
        from_date=from_date,
        to_date=to_date,
        department_id=department_id,
        action_type=action_type
    )

@router.get("/insights/heatmap", response_model=HeatmapDataOut, tags=["artur-dashboard"])
async def get_heatmap_data():
    """
    Get heatmap data showing IA usage, rule overlaps, and automation health across departments.
    """
    return await dashboard_service.get_heatmap_data()

@router.get("/insights/predictions", response_model=PredictionsOut, tags=["artur-dashboard"])
async def get_predictions():
    """
    Get intelligent predictions and proactive insights to prevent future issues.
    """
    return await dashboard_service.get_predictions()

@router.get("/suggestions", response_model=List[ArturSuggestionOut], tags=["artur-evaluation"])
async def get_suggestions(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by suggestion status"),
    source: Optional[str] = Query(None, description="Filter by suggestion source"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    min_confidence: Optional[float] = Query(None, description="Filter by minimum confidence score")
):
    """
    Get actionable intelligence suggestions with clear justifications.
    
    This endpoint returns real-time suggestions from Artur with confidence scores
    and detailed explanations.
    """
    return await evaluation_service.get_suggestions(
        skip=skip,
        limit=limit,
        status=status,
        source=source,
        department_id=department_id,
        min_confidence=min_confidence
    )

@router.post("/simulate", response_model=SimulationResultOut, tags=["artur-simulation"])
async def simulate_intervention(
    simulation_data: Dict[str, Any] = Body(...)
):
    """
    Simulate an intervention before execution.
    
    This endpoint allows for safe preview (sandbox) of system changes suggested by Artur.
    """
    return await simulation_service.simulate_intervention(simulation_data)
