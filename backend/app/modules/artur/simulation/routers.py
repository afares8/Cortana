from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.modules.artur.simulation.schemas import (
    ArturSimulationOut, 
    ArturSimulationCreate, 
    ArturSimulationUpdate,
    RunSimulationRequest
)
from app.modules.artur.simulation.services import simulation_service

router = APIRouter()

@router.get("/simulations", response_model=List[ArturSimulationOut])
async def list_simulations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    result: Optional[str] = None,
    suggestion_id: Optional[int] = None
):
    """List Artur simulations with optional filtering."""
    return await simulation_service.get_simulations(
        skip=skip,
        limit=limit,
        status=status,
        result=result,
        suggestion_id=suggestion_id
    )

@router.get("/simulations/{simulation_id}", response_model=ArturSimulationOut)
async def get_simulation_by_id(simulation_id: int):
    """Get a specific Artur simulation by ID."""
    simulation = await simulation_service.get_simulation_by_id(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation

@router.post("/prepare", response_model=ArturSimulationOut)
async def prepare_simulation(request: RunSimulationRequest):
    """Prepare a simulation based on a suggestion."""
    simulation = await simulation_service.prepare_simulation(request.suggestion_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Failed to prepare simulation")
    return simulation

@router.post("/run/{simulation_id}")
async def run_simulation(simulation_id: int):
    """Run a prepared simulation."""
    success = await simulation_service.run_simulation(simulation_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to run simulation")
    return {"status": "success", "message": "Simulation completed successfully"}
