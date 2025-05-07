from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, File, UploadFile
from pydantic import EmailStr

from app.services.compliance.models.compliance import ComplianceReport, PEPScreeningResult, SanctionsScreeningResult, DocumentRetentionPolicy
from app.services.compliance.schemas.compliance import (
    ComplianceReportCreate, ComplianceReportUpdate,
    PEPScreeningResultCreate, PEPScreeningResultUpdate,
    SanctionsScreeningResultCreate, SanctionsScreeningResultUpdate,
    DocumentRetentionPolicyCreate, DocumentRetentionPolicyUpdate
)
from app.services.compliance.schemas.verify import CustomerVerifyRequest, CustomerVerificationResponse
from app.services.compliance.services.compliance_service import compliance_service
from app.services.compliance.services.verification_service import verification_service
from app.services.compliance.api.endpoints import router as endpoints_router

router = APIRouter()
router.include_router(endpoints_router, tags=["compliance-advanced"])

@router.post("/reports", response_model=ComplianceReport, status_code=201)
async def create_compliance_report_endpoint(report: ComplianceReportCreate):
    """Create a new compliance report."""
    return await compliance_service.create_compliance_report(report)

@router.get("/reports", response_model=List[ComplianceReport])
async def get_compliance_reports_endpoint(
    skip: int = 0,
    limit: int = 100,
    report_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
):
    """Get compliance reports with optional filtering."""
    filters = {}
    if report_type:
        filters["report_type"] = report_type
    if entity_type:
        filters["entity_type"] = entity_type
    if entity_id:
        filters["entity_id"] = entity_id
    if status:
        filters["status"] = status
    
    reports = await compliance_service.get_compliance_reports(skip=skip, limit=limit, filters=filters)
    
    if from_date or to_date:
        filtered_reports = []
        for report in reports:
            if from_date and report.created_at < from_date:
                continue
            if to_date and report.created_at > to_date:
                continue
            filtered_reports.append(report)
        return filtered_reports
    
    return reports

@router.get("/reports/{report_id}", response_model=ComplianceReport)
async def get_compliance_report_endpoint(report_id: int = Path(..., gt=0)):
    """Get a compliance report by ID."""
    report = await compliance_service.get_compliance_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")
    return report

@router.put("/reports/{report_id}", response_model=ComplianceReport)
async def update_compliance_report_endpoint(
    report_id: int = Path(..., gt=0),
    report_update: ComplianceReportUpdate = Body(...)
):
    """Update a compliance report."""
    report = await compliance_service.update_compliance_report(report_id, report_update)
    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")
    return report

@router.delete("/reports/{report_id}", response_model=Dict[str, bool])
async def delete_compliance_report_endpoint(report_id: int = Path(..., gt=0)):
    """Delete a compliance report."""
    result = await compliance_service.delete_compliance_report(report_id)
    if not result:
        raise HTTPException(status_code=404, detail="Compliance report not found")
    return {"success": True}

@router.post("/screening/pep", response_model=PEPScreeningResult, status_code=201)
async def create_pep_screening_endpoint(screening: PEPScreeningResultCreate):
    """Create a new PEP screening result."""
    return await compliance_service.create_pep_screening(screening)

@router.get("/screening/pep", response_model=List[PEPScreeningResult])
async def get_pep_screenings_endpoint(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    match_status: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """Get PEP screening results with optional filtering."""
    filters = {}
    if client_id:
        filters["client_id"] = client_id
    if match_status:
        filters["match_status"] = match_status
    if risk_level:
        filters["risk_level"] = risk_level
    
    return await compliance_service.get_pep_screenings(skip=skip, limit=limit, filters=filters)

@router.get("/screening/pep/{screening_id}", response_model=PEPScreeningResult)
async def get_pep_screening_endpoint(screening_id: int = Path(..., gt=0)):
    """Get a PEP screening result by ID."""
    screening = await compliance_service.get_pep_screening(screening_id)
    if not screening:
        raise HTTPException(status_code=404, detail="PEP screening result not found")
    return screening

@router.put("/screening/pep/{screening_id}", response_model=PEPScreeningResult)
async def update_pep_screening_endpoint(
    screening_id: int = Path(..., gt=0),
    screening_update: PEPScreeningResultUpdate = Body(...)
):
    """Update a PEP screening result."""
    screening = await compliance_service.update_pep_screening(screening_id, screening_update)
    if not screening:
        raise HTTPException(status_code=404, detail="PEP screening result not found")
    return screening

@router.post("/screening/sanctions", response_model=SanctionsScreeningResult, status_code=201)
async def create_sanctions_screening_endpoint(screening: SanctionsScreeningResultCreate):
    """Create a new sanctions screening result."""
    return await compliance_service.create_sanctions_screening(screening)

@router.get("/screening/sanctions", response_model=List[SanctionsScreeningResult])
async def get_sanctions_screenings_endpoint(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    match_status: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """Get sanctions screening results with optional filtering."""
    filters = {}
    if client_id:
        filters["client_id"] = client_id
    if match_status:
        filters["match_status"] = match_status
    if risk_level:
        filters["risk_level"] = risk_level
    
    return await compliance_service.get_sanctions_screenings(skip=skip, limit=limit, filters=filters)

@router.get("/screening/sanctions/{screening_id}", response_model=SanctionsScreeningResult)
async def get_sanctions_screening_endpoint(screening_id: int = Path(..., gt=0)):
    """Get a sanctions screening result by ID."""
    screening = await compliance_service.get_sanctions_screening(screening_id)
    if not screening:
        raise HTTPException(status_code=404, detail="Sanctions screening result not found")
    return screening

@router.put("/screening/sanctions/{screening_id}", response_model=SanctionsScreeningResult)
async def update_sanctions_screening_endpoint(
    screening_id: int = Path(..., gt=0),
    screening_update: SanctionsScreeningResultUpdate = Body(...)
):
    """Update a sanctions screening result."""
    screening = await compliance_service.update_sanctions_screening(screening_id, screening_update)
    if not screening:
        raise HTTPException(status_code=404, detail="Sanctions screening result not found")
    return screening

@router.post("/retention-policies", response_model=DocumentRetentionPolicy, status_code=201)
async def create_retention_policy_endpoint(policy: DocumentRetentionPolicyCreate):
    """Create a new document retention policy."""
    return await compliance_service.create_retention_policy(policy)

@router.get("/retention-policies", response_model=List[DocumentRetentionPolicy])
async def get_retention_policies_endpoint(
    skip: int = 0,
    limit: int = 100,
    document_type: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """Get document retention policies with optional filtering."""
    filters = {}
    if document_type:
        filters["document_type"] = document_type
    if is_active is not None:
        filters["is_active"] = is_active
    
    return await compliance_service.get_retention_policies(skip=skip, limit=limit, filters=filters)

@router.get("/retention-policies/{policy_id}", response_model=DocumentRetentionPolicy)
async def get_retention_policy_endpoint(policy_id: int = Path(..., gt=0)):
    """Get a document retention policy by ID."""
    policy = await compliance_service.get_retention_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Document retention policy not found")
    return policy

@router.put("/retention-policies/{policy_id}", response_model=DocumentRetentionPolicy)
async def update_retention_policy_endpoint(
    policy_id: int = Path(..., gt=0),
    policy_update: DocumentRetentionPolicyUpdate = Body(...)
):
    """Update a document retention policy."""
    policy = await compliance_service.update_retention_policy(policy_id, policy_update)
    if not policy:
        raise HTTPException(status_code=404, detail="Document retention policy not found")
    return policy

@router.delete("/retention-policies/{policy_id}", response_model=Dict[str, bool])
async def delete_retention_policy_endpoint(policy_id: int = Path(..., gt=0)):
    """Delete a document retention policy."""
    result = await compliance_service.delete_retention_policy(policy_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document retention policy not found")
    return {"success": True}

@router.post("/verify-customer", response_model=CustomerVerificationResponse, status_code=201)
async def verify_customer_endpoint(request: CustomerVerifyRequest = Body(...)):
    """
    Verify a customer against PEP and sanctions lists.
    
    This endpoint performs comprehensive verification of a customer (natural person or legal entity)
    against multiple data sources including:
    - PEP (Politically Exposed Person) databases
    - Sanctions lists (UN, OFAC, EU)
    - Other relevant compliance databases
    
    For legal entities, it also verifies directors and ultimate beneficial owners (UBOs).
    
    The verification process includes:
    1. Entity enrichment with aliases, IDs & metadata
    2. Verification against PEP databases
    3. Screening against all relevant sanctions lists
    4. Structured results reporting
    
    Returns a comprehensive verification response with results from all data sources.
    """
    return await verification_service.verify_customer(request)
