from fastapi import APIRouter, Query
from typing import List, Optional

from app.modules.artur.dashboard.schemas import DepartmentHealthOut, HeatmapDataOut, PredictionsOut
from app.modules.artur.dashboard.services import dashboard_service

router = APIRouter()

@router.get("/department-health", response_model=List[DepartmentHealthOut])
async def get_department_health(
    department_id: Optional[int] = Query(None, description="Filter by department ID")
):
    """
    Get health metrics for departments monitored by Artur.
    """
    return await dashboard_service.get_department_health(department_id)

@router.get("/insights/heatmap", response_model=HeatmapDataOut)
async def get_heatmap_data():
    """
    Get heatmap data showing IA usage, rule overlaps, and automation health across departments.
    """
    return await dashboard_service.get_heatmap_data()

@router.get("/insights/predictions", response_model=PredictionsOut)
async def get_predictions():
    """
    Get intelligent predictions and proactive insights to prevent future issues.
    """
    return await dashboard_service.get_predictions()
