from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import admin_required
from app.schemas.system_settings import SystemSettingsSchema
from app.services.system_settings import SystemSettingsService

router = APIRouter()

@router.get("/", response_model=SystemSettingsSchema)
def get_system_settings(current_user = Depends(admin_required)):
    """
    Get system settings.
    Requires admin access.
    """
    try:
        settings = SystemSettingsService.get_settings()
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system settings: {str(e)}"
        )

@router.put("/", response_model=SystemSettingsSchema)
def update_system_settings(
    settings: SystemSettingsSchema, 
    current_user = Depends(admin_required)
):
    """
    Update system settings.
    Requires admin access.
    """
    try:
        updated_settings = SystemSettingsService.update_settings(
            settings, 
            user_id=current_user.get("id")
        )
        return updated_settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update system settings: {str(e)}"
        )
