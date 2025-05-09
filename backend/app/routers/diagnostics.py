from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any

from app.schemas.diagnostics import DiagnosticsRunRequest, DiagnosticsResponse, DiagnosticsStats
from app.services.diagnostics.api.router import router as diagnostics_router

router = APIRouter()

router.include_router(diagnostics_router)
