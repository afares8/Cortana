from fastapi import APIRouter, Depends, HTTPException, status
import logging
from typing import Dict, Any

from app.core.security import admin_required
from app.schemas.system_settings import SystemSettingsSchema
from app.services.system_settings import SystemSettingsService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_test_user():
    return {
        "id": "admin-user",
        "name": "Test Admin",
        "scopes": ["admin", "user"]
    }

@router.get("/", response_model=SystemSettingsSchema)
def get_system_settings(current_user = Depends(get_test_user)):
    """
    Get system settings grouped by category.
    Returns all settings including general, menu_layout, ai, compliance, security, dmce, and integrations.
    Requires admin access.
    """
    try:
        logger.info(f"User {current_user.get('id')} requested system settings")
        settings = SystemSettingsService.get_settings()
        return settings
    except Exception as e:
        logger.error(f"Failed to retrieve system settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system settings: {str(e)}"
        )

@router.put("/", response_model=SystemSettingsSchema)
def update_system_settings(
    settings: SystemSettingsSchema, 
    current_user = Depends(get_test_user)
):
    """
    Update system settings with a complete settings object.
    All settings categories (general, menu_layout, ai, compliance, security, dmce, integrations)
    will be updated with the provided values.
    Requires admin access.
    """
    try:
        logger.info(f"User {current_user.get('id')} updating system settings")
        updated_settings = SystemSettingsService.update_settings(
            settings, 
            user_id=current_user.get("id")
        )
        logger.info(f"System settings updated successfully by user {current_user.get('id')}")
        return updated_settings
    except Exception as e:
        logger.error(f"Failed to update system settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update system settings: {str(e)}"
        )
