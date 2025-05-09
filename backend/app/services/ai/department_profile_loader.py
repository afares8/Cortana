import logging
from typing import Optional, Dict, Any

from app.modules.ai.services import get_ai_profile_by_department

logger = logging.getLogger(__name__)

async def get_department_ai_profile(department_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Get the AI profile for a specific department.
    
    Args:
        department_id: The ID of the department to get the AI profile for
        
    Returns:
        A dictionary containing the AI profile parameters, or None if no profile is found
    """
    if not department_id:
        logger.info("No department_id provided, using default AI parameters")
        return None
    
    try:
        profile = get_ai_profile_by_department(department_id)
        if not profile:
            logger.warning(f"No AI profile found for department_id {department_id}, using default parameters")
            return None
        
        logger.info(f"Using AI profile '{profile.name}' for department_id {department_id}")
        return {
            "model": profile.model,
            "embedding_id": profile.embedding_id,
            "temperature": profile.temperature,
            "top_p": profile.top_p,
            "context_type": profile.context_type
        }
    except Exception as e:
        logger.error(f"Error loading AI profile for department_id {department_id}: {e}")
        return None
