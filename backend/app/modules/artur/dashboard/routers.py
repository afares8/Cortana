from fastapi import APIRouter, Query
from typing import List, Optional

from app.modules.artur.dashboard.schemas import DepartmentHealthOut
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
