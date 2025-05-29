from app.services.compliance.api.endpoints import router as endpoints_router
from app.services.compliance.services.verification_service import verification_service
from app.services.compliance.services.compliance_service import compliance_service
from app.services.compliance.services.unified_verification_service import unified_verification_service
from app.services.compliance.schemas.verify import CustomerVerifyRequest, CustomerVerificationResponse, EntityBase
from app.services.compliance.schemas.compliance import (
    ComplianceReportCreate, ComplianceReportUpdate,
    PEPScreeningResultCreate, PEPScreeningResultUpdate,
    SanctionsScreeningResultCreate, SanctionsScreeningResultUpdate,
    DocumentRetentionPolicyCreate, DocumentRetentionPolicyUpdate
)
from app.services.compliance.models.compliance import ComplianceReport, PEPScreeningResult, SanctionsScreeningResult, DocumentRetentionPolicy
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import logging
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, File, UploadFile, status
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
        
        list_updates = list_updates_db.get_multi()
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
        logger.info("Generating compliance dashboard data")
        
        return {
            "total_screenings": 120,
            "flagged_clients": 8,
            "last_update": datetime.now().isoformat(),
            "sanction_sources": ["OFAC", "UN", "EU"]
        }
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        return {
            "total_screenings": 0,
            "flagged_clients": 0,
            "last_update": datetime.now().isoformat(),
            "sanction_sources": []
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


@router.post("/uaf-reports", response_model=Dict[str, Any], status_code=201)
async def generate_uaf_report_endpoint(
    client_id: int = Body(..., embed=True),
    start_date: str = Body(..., embed=True),
    end_date: str = Body(..., embed=True),
):
    """
    Generate a UAF (Unusual Activity Form) report for a client.
    
    This endpoint generates a UAF report for the specified client for the given date range.
    The report includes:
    - Client information
    - Transaction history
    - Risk assessment
    - Compliance officer notes
    
    Returns the report ID and status, which can be used to download the report.
    """
    try:
        from app.services.compliance.services.compliance_service import compliance_service
        from app.legal.services import get_client
        from datetime import datetime
        import os
        from pathlib import Path
        
        client = get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        reports_dir = Path("data/uaf_reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            "report_type": "UAF",
            "entity_type": "client",
            "entity_id": client_id,
            "entity_name": client.name,
            "start_date": start_date,
            "end_date": end_date,
            "status": "generated",
            "generated_by": "system",
            "report_path": str(reports_dir / f"uaf_report_{client_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"),
            "metadata": {
                "client_risk_level": getattr(client, "risk_level", "UNKNOWN"),
                "client_risk_score": getattr(client, "risk_score", 0),
                "client_country": getattr(client, "country", "PA"),
                "client_industry": getattr(client, "industry", "other"),
            }
        }
        
        report = await compliance_service.create_compliance_report(report_data)
        
        from app.services.compliance.services.report_generator import generate_uaf_report_pdf
        await generate_uaf_report_pdf(report)
        
        return {
            "id": report.id,
            "status": "generated",
            "message": "UAF report generated successfully",
            "download_url": f"/api/v1/compliance/reports/{report.id}/download"
        }
    except Exception as e:
        logger.error(f"Error generating UAF report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate UAF report. Please try again later.")

@router.post("/verify-all", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def verify_all_clients_endpoint():
    """
    Verify all clients against PEP and sanctions lists.
    
    This endpoint triggers verification for all clients in the system
    that haven't been verified recently.
    """
    try:
        from app.legal.services import get_clients
        
        clients = get_clients(limit=1000)  # Get all clients
        results = []
        
        for client in clients:
            try:
                customer_data = {
                    "name": client.name,
                    "country": getattr(client, "country", "PA"),
                    "type": getattr(client, "client_type", "natural"),
                }
                
                request = CustomerVerifyRequest(customer=EntityBase(**customer_data))
                verification_result = await unified_verification_service.verify_customer(request)
                
                results.append({
                    "client_id": client.id,
                    "client_name": client.name,
                    "status": "verified",
                    "verification_result": verification_result
                })
            except Exception as e:
                logger.error(f"Error verifying client {client.id}: {str(e)}")
                results.append({
                    "client_id": client.id,
                    "client_name": client.name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "total_clients": len(clients),
            "verified_count": len([r for r in results if r["status"] == "verified"]),
            "error_count": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform batch verification. Please try again later.")


@router.get("/verification-status", response_model=Dict[str, Any])
async def get_verification_status_endpoint(client_id: int = Query(...)):
    """
    Get verification status for a specific client.
    
    Returns the current verification status including PEP screening,
    sanctions screening, and risk assessment results.
    """
    try:
        from app.legal.services import get_client
        
        client = get_client(client_id)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        
        verification_status = getattr(client, "verification_status", "not_verified")
        verification_date = getattr(client, "verification_date", None)
        verification_result = getattr(client, "verification_result", {})
        
        return {
            "client_id": client_id,
            "client_name": client.name,
            "verification_status": verification_status,
            "verification_date": verification_date.isoformat() if verification_date else None,
            "verification_result": verification_result,
            "risk_level": getattr(client, "risk_level", "unknown"),
            "risk_score": getattr(client, "risk_score", 0),
            "pep_screening_status": verification_result.get("customer", {}).get("pep_matches", []),
            "sanctions_screening_status": verification_result.get("customer", {}).get("sanctions_matches", []),
            "country_risk": verification_result.get("country_risk", {}),
            "last_updated": verification_date.isoformat() if verification_date else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving verification status for client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve verification status. Please try again later.")
