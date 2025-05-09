from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from uuid import UUID

from app.core.config import settings
from app.modules.ai.schemas import AIProfileCreate, AIProfileUpdate, AIProfileOut
from app.modules.ai.services import (
    create_ai_profile, get_ai_profile, get_ai_profiles, 
    get_ai_profile_by_department, update_ai_profile, delete_ai_profile
)

router = APIRouter()

@router.post("", response_model=AIProfileOut, status_code=201)
async def create_ai_profile_endpoint(profile: AIProfileCreate):
    """Create a new AI profile."""
    return create_ai_profile(profile.model_dump())

@router.get("", response_model=List[AIProfileOut])
async def get_ai_profiles_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    model: Optional[str] = None,
    department_id: Optional[int] = None
):
    """Get all AI profiles with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    if model:
        filters["model"] = model
    if department_id:
        filters["department_id"] = department_id
    
    return get_ai_profiles(skip=skip, limit=limit, filters=filters)

@router.get("/by-department/{department_id}", response_model=AIProfileOut)
async def get_ai_profile_by_department_endpoint(department_id: int = Path(...)):
    """Get an AI profile for a specific department."""
    profile = get_ai_profile_by_department(department_id)
    if not profile:
        raise HTTPException(status_code=404, detail="AI profile not found for this department")
    return profile

@router.get("/{profile_id}", response_model=AIProfileOut)
async def get_ai_profile_endpoint(profile_id: int = Path(...)):
    """Get an AI profile by ID."""
    profile = get_ai_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="AI profile not found")
    return profile

@router.put("/{profile_id}", response_model=AIProfileOut)
async def update_ai_profile_endpoint(
    profile_update: AIProfileUpdate,
    profile_id: int = Path(...)
):
    """Update an AI profile."""
    profile = update_ai_profile(profile_id, profile_update.model_dump(exclude_unset=True))
    if not profile:
        raise HTTPException(status_code=404, detail="AI profile not found")
    return profile

@router.delete("/{profile_id}", response_model=dict)
async def delete_ai_profile_endpoint(profile_id: int = Path(...)):
    """Delete an AI profile."""
    success = delete_ai_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="AI profile not found")
    return {"success": True}
