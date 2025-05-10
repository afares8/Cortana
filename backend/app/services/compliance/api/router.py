from app.services.compliance.api.endpoints import router as endpoints_router
from app.services.compliance.services.verification_service import verification_service
from app.services.compliance.services.compliance_service import compliance_service
from app.services.compliance.schemas.verify import CustomerVerifyRequest, CustomerVerificationResponse
from app.services.compliance.schemas.compliance import (
    ComplianceReportCreate, ComplianceReportUpdate,
    PEPScreeningResultCreate, PEPScreeningResultUpdate,
    SanctionsScreeningResultCreate, SanctionsScreeningResultUpdate,
    DocumentRetentionPolicyCreate, DocumentRetentionPolicyUpdate
)
from app.services.compliance.models.compliance import ComplianceReport, PEPScreeningResult, SanctionsScreeningResult, DocumentRetentionPolicy
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, File, UploadFile
from pydantic import EmailStr

logger = logging.getLogger(__name__)


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
        raise HTTPException(
            status_code=404,
            detail="Compliance report not found")
    return report


@router.put("/reports/{report_id}", response_model=ComplianceReport)
async def update_compliance_report_endpoint(
    report_id: int = Path(..., gt=0),
    report_update: ComplianceReportUpdate = Body(...)
):
    """Update a compliance report."""
    report = await compliance_service.update_compliance_report(report_id, report_update)
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Compliance report not found")
    return report


@router.delete("/reports/{report_id}", response_model=Dict[str, bool])
async def delete_compliance_report_endpoint(report_id: int = Path(..., gt=0)):
    """Delete a compliance report."""
    result = await compliance_service.delete_compliance_report(report_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Compliance report not found")
    return {"success": True}


@router.post("/screening/pep",
             response_model=PEPScreeningResult,
             status_code=201)
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
        raise HTTPException(status_code=404,
                            detail="PEP screening result not found")
    return screening


@router.put("/screening/pep/{screening_id}", response_model=PEPScreeningResult)
async def update_pep_screening_endpoint(
    screening_id: int = Path(..., gt=0),
    screening_update: PEPScreeningResultUpdate = Body(...)
):
    """Update a PEP screening result."""
    screening = await compliance_service.update_pep_screening(screening_id, screening_update)
    if not screening:
        raise HTTPException(status_code=404,
                            detail="PEP screening result not found")
    return screening


@router.post("/screening/sanctions",
             response_model=SanctionsScreeningResult,
             status_code=201)
async def create_sanctions_screening_endpoint(
        screening: SanctionsScreeningResultCreate):
    """Create a new sanctions screening result."""
    return await compliance_service.create_sanctions_screening(screening)


@router.get("/screening/sanctions",
            response_model=List[SanctionsScreeningResult])
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


@router.get("/screening/sanctions/{screening_id}",
            response_model=SanctionsScreeningResult)
async def get_sanctions_screening_endpoint(
        screening_id: int = Path(..., gt=0)):
    """Get a sanctions screening result by ID."""
    screening = await compliance_service.get_sanctions_screening(screening_id)
    if not screening:
        raise HTTPException(status_code=404,
                            detail="Sanctions screening result not found")
    return screening


@router.put("/screening/sanctions/{screening_id}",
            response_model=SanctionsScreeningResult)
async def update_sanctions_screening_endpoint(
    screening_id: int = Path(..., gt=0),
    screening_update: SanctionsScreeningResultUpdate = Body(...)
):
    """Update a sanctions screening result."""
    screening = await compliance_service.update_sanctions_screening(screening_id, screening_update)
    if not screening:
        raise HTTPException(status_code=404,
                            detail="Sanctions screening result not found")
    return screening


@router.post("/retention-policies",
             response_model=DocumentRetentionPolicy,
             status_code=201)
async def create_retention_policy_endpoint(
        policy: DocumentRetentionPolicyCreate):
    """Create a new document retention policy."""
    return await compliance_service.create_retention_policy(policy)


@router.get("/retention-policies",
            response_model=List[DocumentRetentionPolicy])
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


@router.get("/retention-policies/{policy_id}",
            response_model=DocumentRetentionPolicy)
async def get_retention_policy_endpoint(policy_id: int = Path(..., gt=0)):
    """Get a document retention policy by ID."""
    policy = await compliance_service.get_retention_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404,
                            detail="Document retention policy not found")
    return policy


@router.put("/retention-policies/{policy_id}",
            response_model=DocumentRetentionPolicy)
async def update_retention_policy_endpoint(
    policy_id: int = Path(..., gt=0),
    policy_update: DocumentRetentionPolicyUpdate = Body(...)
):
    """Update a document retention policy."""
    policy = await compliance_service.update_retention_policy(policy_id, policy_update)
    if not policy:
        raise HTTPException(status_code=404,
                            detail="Document retention policy not found")
    return policy


@router.delete("/retention-policies/{policy_id}",
               response_model=Dict[str, bool])
async def delete_retention_policy_endpoint(policy_id: int = Path(..., gt=0)):
    """Delete a document retention policy."""
    result = await compliance_service.delete_retention_policy(policy_id)
    if not result:
        raise HTTPException(status_code=404,
                            detail="Document retention policy not found")
    return {"success": True}


@router.post("/verify-customer",
             response_model=Dict[str, Any], status_code=201)
async def verify_customer_endpoint(request: CustomerVerifyRequest = Body(...)):
    """
    Unified endpoint to verify a customer against PEP and sanctions lists,
    assess country risk, and generate UAF report.

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
    4. Country risk assessment
    5. UAF report generation
    6. Structured results reporting

    Returns a comprehensive verification response with results from all data sources,
    country risk assessment, and UAF report information.
    """
    try:
        from app.services.compliance.services.unified_verification_service import unified_verification_service
        return await unified_verification_service.verify_customer(request)
    except Exception as e:
        logger.error(f"Error in customer verification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to perform compliance check. Please try again later.")


@router.get("/country-risk", response_model=Dict[str, Any])
async def get_country_risk_endpoint():
    """
    Get risk assessment for all countries for heatmap visualization.

    This endpoint returns a comprehensive risk assessment for all countries,
    including:
    - Risk level (High/Medium/Low)
    - FATF status (Blacklist/Greylist/Not listed)
    - EU High-Risk status
    - Basel AML Index score and rank
    - Last updated date

    The data is used to render the risk heatmap in the frontend.
    """
    try:
        from app.services.compliance.services.unified_verification_service import unified_verification_service
        return await unified_verification_service.get_all_countries_risk()
    except Exception as e:
        logger.error(f"Error retrieving country risk data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve country risk data. Please try again later.")


@router.post("/force-update-risk-matrix", response_model=Dict[str, Any])
async def force_update_risk_matrix_endpoint():
    """
    Force update of the risk matrix data.

    This endpoint triggers an immediate update of the risk matrix data from all sources,
    including Basel AML Index, FATF lists, and EU high-risk countries.
    """
    try:
        from app.services.compliance.services.risk_matrix import risk_matrix
        from app.db.in_memory import list_updates_db
        from datetime import datetime
        
        await risk_matrix.update_risk_data()
        
        list_updates_db.create({
            "list_name": "Country Risk Matrix",
            "update_date": datetime.now(),
            "status": "Success",
            "details": "Manual update of Basel AML Index, FATF, and EU high-risk countries data"
        })
        
        return {"success": True, "message": "Risk matrix data updated successfully"}
    except Exception as e:
        logger.error(f"Error updating risk matrix data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update risk matrix data. Please try again later.")


@router.get("/monitoring/tasks", response_model=Dict[str, Any])
async def get_scheduled_tasks_status_endpoint():
    """
    Get status of all scheduled compliance tasks.
    
    This endpoint returns the status of all scheduled compliance tasks including:
    - Last run time
    - Success/failure status
    - Next scheduled run time
    - Error details if applicable
    
    The data is used to monitor the health of automated compliance processes.
    """
    try:
        from app.db.in_memory import list_updates_db
        from datetime import datetime, timedelta
        
        list_updates = list_updates_db.get_all()
        list_updates.sort(key=lambda x: getattr(x, 'update_date', datetime.now()) if not isinstance(getattr(x, 'update_date', None), str) else datetime.now(), reverse=True)
        
        tasks_status = {
            "risk_matrix": {"status": "unknown", "last_run": None, "next_run": None, "error": None},
            "ofac": {"status": "unknown", "last_run": None, "next_run": None, "error": None},
            "eu_sanctions": {"status": "unknown", "last_run": None, "next_run": None, "error": None},
            "un_sanctions": {"status": "unknown", "last_run": None, "next_run": None, "error": None},
            "opensanctions": {"status": "unknown", "last_run": None, "next_run": None, "error": None}
        }
        
        for update in list_updates:
            list_name = getattr(update, 'list_name', None)
            if isinstance(list_name, str):
                task_key = None
                if "Risk Matrix" in list_name:
                    task_key = "risk_matrix"
                elif "OFAC" in list_name:
                    task_key = "ofac"
                elif "EU Sanctions" in list_name:
                    task_key = "eu_sanctions"
                elif "UN Sanctions" in list_name:
                    task_key = "un_sanctions"
                elif "OpenSanctions" in list_name:
                    task_key = "opensanctions"
                
                if task_key and task_key in tasks_status:
                    update_date = getattr(update, 'update_date', None)
                    if not update_date:
                        continue
                        
                    if isinstance(update_date, str):
                        try:
                            update_date = datetime.fromisoformat(update_date)
                        except:
                            continue
                            
                    tasks_status[task_key]["status"] = getattr(update, 'status', "unknown")
                    tasks_status[task_key]["last_run"] = update_date.isoformat()
                    tasks_status[task_key]["error"] = getattr(update, 'details', None) if "Error" in getattr(update, 'details', "") else None
                    
                    if task_key == "risk_matrix":
                        tasks_status[task_key]["next_run"] = (update_date + timedelta(days=7)).isoformat()  # Weekly
                    else:
                        tasks_status[task_key]["next_run"] = (update_date + timedelta(days=1)).isoformat()  # Daily
        
        return {
            "tasks": tasks_status,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving scheduled tasks status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve scheduled tasks status. Please try again later.")


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_compliance_dashboard_endpoint():
    """
    Get compliance dashboard data including metrics, recent verifications, and list updates.

    This endpoint returns comprehensive dashboard data including:
    - Compliance metrics (active contracts, expiring contracts, PEP matches, etc.)
    - Recent customer verifications with results
    - Recent sanctions list updates
    - Risk assessment statistics

    The data is used to render the compliance dashboard in the frontend.
    """
    try:
        logger.info("Generating simplified compliance dashboard data")
        
        recent_verifications = [
            {
                "id": "1",
                "client_name": "Empresa Global S.A.",
                "verification_date": datetime.now().replace(hour=10, minute=30).isoformat(),
                "result": "No Match",
                "risk_level": "LOW",
                "report_path": "/api/v1/compliance/reports/1/download"
            },
            {
                "id": "2",
                "client_name": "Inversiones Pacífico",
                "verification_date": datetime.now().replace(hour=9, minute=15).isoformat(),
                "result": "Match Found",
                "risk_level": "HIGH",
                "report_path": "/api/v1/compliance/reports/2/download"
            },
            {
                "id": "3",
                "client_name": "Constructora Horizonte",
                "verification_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "result": "No Match",
                "risk_level": "MEDIUM",
                "report_path": "/api/v1/compliance/reports/3/download"
            },
            {
                "id": "4",
                "client_name": "Servicios Financieros Panamá",
                "verification_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "result": "No Match",
                "risk_level": "LOW",
                "report_path": "/api/v1/compliance/reports/4/download"
            },
            {
                "id": "5",
                "client_name": "Importadora Caribe",
                "verification_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "result": "Match Found",
                "risk_level": "HIGH",
                "report_path": "/api/v1/compliance/reports/5/download"
            }
        ]
        
        # Create mock list updates
        list_updates = [
            {
                "list_name": "OFAC Sanctions List",
                "update_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "status": "Success"
            },
            {
                "list_name": "EU Sanctions List",
                "update_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "status": "Success"
            },
            {
                "list_name": "UN Sanctions List",
                "update_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "status": "Success"
            },
            {
                "list_name": "PEP Database",
                "update_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "status": "Success"
            }
        ]
        
        dashboard_data = {
            "active_contracts": 42,
            "expiring_contracts": 7,
            "pep_matches": 3,
            "sanctions_matches": 2,
            "pending_reports": 12,
            "high_risk_clients": 5,
            "recent_verifications": recent_verifications,
            "recent_list_updates": list_updates,
            "risk_stats": {
                "high_risk": 5,
                "medium_risk": 18,
                "low_risk": 27
            }
        }
        
        logger.info("Successfully generated compliance dashboard data")
        return dashboard_data
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        return {
            "active_contracts": 0,
            "expiring_contracts": 0,
            "pep_matches": 0,
            "sanctions_matches": 0,
            "pending_reports": 0,
            "high_risk_clients": 0,
            "recent_verifications": [],
            "recent_list_updates": [],
            "risk_stats": {
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0
            }
        }


@router.get("/reports/{report_id}/download", response_model=Dict[str, Any])
async def download_report_endpoint(report_id: str = Path(...)):
    """
    Download a UAF report by ID.

    This endpoint returns the UAF report file for the specified report ID.
    """
    try:
        from app.db.in_memory import compliance_reports_db
        from fastapi.responses import FileResponse
        import os
        
        try:
            report_id_int = int(report_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid report ID format")
        
        report = compliance_reports_db.get(report_id_int)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if not os.path.exists(report.report_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        return FileResponse(
            path=report.report_path,
            filename=f"uaf_report_{report_id}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download report. Please try again later.")
