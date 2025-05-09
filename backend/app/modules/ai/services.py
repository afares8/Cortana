from typing import List, Optional, Dict, Any

from app.db.base import InMemoryDB
from app.modules.ai.models import AIProfile

ai_profiles_db = InMemoryDB[AIProfile](AIProfile)

def create_ai_profile(profile_data: Dict[str, Any]) -> AIProfile:
    """Create a new AI profile."""
    return ai_profiles_db.create(obj_in=AIProfile(**profile_data))

def get_ai_profile(profile_id: int) -> Optional[AIProfile]:
    """Get an AI profile by ID."""
    return ai_profiles_db.get(id=profile_id)

def get_ai_profile_by_department(department_id: int) -> Optional[AIProfile]:
    """Get an AI profile for a specific department."""
    profiles = ai_profiles_db.get_multi(filters={"department_id": department_id})
    return profiles[0] if profiles else None

def get_ai_profiles(
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[Dict[str, Any]] = None
) -> List[AIProfile]:
    """Get AI profiles with optional filtering."""
    return ai_profiles_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_ai_profile(profile_id: int, profile_data: Dict[str, Any]) -> Optional[AIProfile]:
    """Update an AI profile."""
    return ai_profiles_db.update(id=profile_id, obj_in=AIProfile(**profile_data))

def delete_ai_profile(profile_id: int) -> bool:
    """Delete an AI profile."""
    profile = ai_profiles_db.remove(id=profile_id)
    return profile is not None
