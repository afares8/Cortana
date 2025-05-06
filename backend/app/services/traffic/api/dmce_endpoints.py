"""
DMCE API Endpoints

This module provides API endpoints for DMCE portal integration,
including manual login functionality using Firefox in Private Browsing mode.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.services.traffic.utils.dmce_manual_login import (
    start_manual_login,
    complete_manual_login,
    cleanup_session,
    cleanup_old_sessions
)

router = APIRouter()

class ManualLoginRequest(BaseModel):
    """Request model for starting a manual login session."""
    company: Optional[str] = None

class ManualLoginCompleteRequest(BaseModel):
    """Request model for completing a manual login session."""
    sessionId: str

class DMCEResponse(BaseModel):
    """Response model for DMCE API endpoints."""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    sessionId: Optional[str] = None
    loginUrl: Optional[str] = None
    company: Optional[str] = None

@router.post("/dmce/manual-login/start", response_model=DMCEResponse)
async def api_start_manual_login(
    request: ManualLoginRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Start a manual login session by opening Firefox in Private Browsing mode.
    
    Args:
        request: Request containing company name
        background_tasks: FastAPI background tasks
        
    Returns:
        DMCEResponse: Response with session ID and status information
    """
    background_tasks.add_task(cleanup_old_sessions)
    
    try:
        result = await start_manual_login(company=request.company)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Error starting manual login session: {str(e)}"
        }

@router.post("/dmce/manual-login/complete", response_model=DMCEResponse)
async def api_complete_manual_login(
    request: ManualLoginCompleteRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Complete a manual login session by checking if login was successful.
    
    Args:
        request: Request containing session ID
        background_tasks: FastAPI background tasks
        
    Returns:
        DMCEResponse: Response with status information
    """
    try:
        result = await complete_manual_login(session_id=request.sessionId)
        
        if result.get("success", False):
            background_tasks.add_task(cleanup_session, request.sessionId)
        
        return result
    except HTTPException as e:
        return {
            "success": False,
            "error": str(e.detail)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error completing manual login session: {str(e)}"
        }
