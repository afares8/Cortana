"""
DMCE API Schemas

This module defines the Pydantic models for DMCE API requests and responses.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

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
