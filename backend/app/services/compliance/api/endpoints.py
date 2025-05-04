from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query

from app.services.compliance.models.compliance import ComplianceReport
from app.services.compliance.services.compliance_service import compliance_service

router = APIRouter()

@router.post("/uaf-reports", response_model=ComplianceReport, status_code=201)
async def generate_uaf_report_endpoint(
    client_id: int = Body(..., embed=True),
    start_date: datetime = Body(..., embed=True),
    end_date: datetime = Body(..., embed=True)
):
    """
    Generate a UAF (Unidad de Análisis Financiero) report for a client.
    This report is required by Panamanian regulations for certain transactions.
    """
    return await compliance_service.generate_uaf_report(client_id, start_date, end_date)

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_compliance_dashboard_endpoint():
    """
    Get data for the compliance dashboard.
    """
    return await compliance_service.get_compliance_dashboard_data()
