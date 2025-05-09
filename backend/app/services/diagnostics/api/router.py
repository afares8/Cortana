from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any

from app.services.diagnostics.interface import diagnostics_service
from app.schemas.diagnostics import DiagnosticsRunRequest, DiagnosticsResponse, DiagnosticsStats

router = APIRouter()

@router.post("/run", response_model=DiagnosticsResponse)
async def run_diagnostics(request: DiagnosticsRunRequest):
    """
    Run diagnostics on the system.
    
    This endpoint runs diagnostic checks on various system components and returns the results.
    It can optionally include explanations, suggestions, and predictions.
    """
    try:
        result = await diagnostics_service.run_diagnostics(
            components=request.components,
            include_explanations=request.include_explanations,
            include_suggestions=request.include_suggestions,
            include_predictions=request.include_predictions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running diagnostics: {str(e)}")

@router.get("/stats", response_model=DiagnosticsStats)
async def get_diagnostic_stats():
    """
    Get diagnostic statistics.
    
    This endpoint returns statistics about past diagnostic runs, including counts of healthy,
    warning, and error statuses, as well as historical data for trend analysis.
    """
    try:
        stats = await diagnostics_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting diagnostic stats: {str(e)}")
