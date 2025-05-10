from fastapi import APIRouter

from app.modules.artur.observation.routers import router as observation_router
from app.modules.artur.evaluation.routers import router as evaluation_router
from app.modules.artur.intervention.routers import router as intervention_router
from app.modules.artur.simulation.routers import router as simulation_router
from app.modules.artur.dashboard.routers import router as dashboard_router

router = APIRouter()

router.include_router(observation_router, prefix="/observation", tags=["artur-observation"])
router.include_router(evaluation_router, prefix="/evaluation", tags=["artur-evaluation"])
router.include_router(intervention_router, prefix="/intervention", tags=["artur-intervention"])
router.include_router(simulation_router, prefix="/simulation", tags=["artur-simulation"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["artur-dashboard"])
