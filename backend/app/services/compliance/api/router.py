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
from datetime import datetime
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
        from app.services.compliance.services.unified_verification_service import unified_verification_service
        from app.db.in_memory import compliance_reports_db, list_updates_db, pep_screening_results_db, sanctions_screening_results_db
        import os
        from pathlib import Path
        from app.services.compliance.models.models import ComplianceReport
        
        reports_dir = Path.home() / "repos" / "Cortana" / "backend" / "data" / "uaf_reports"
        recent_verifications = []
        
        if reports_dir.exists():
            logger.info(f"Scanning directory for reports: {reports_dir}")
            report_files = list(reports_dir.glob("*.pdf"))
            
            if report_files:
                logger.info(f"Found {len(report_files)} PDF files in {reports_dir}")
                report_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                
                existing_reports = compliance_reports_db.get_all()
                existing_paths = [getattr(r, 'report_path', '') for r in existing_reports]
                logger.info(f"Found {len(existing_reports)} existing reports in database")
                
                for i, report_file in enumerate(report_files[:5]):
                    try:
                        report_path = str(report_file)
                        filename = report_file.name
                        
                        name_parts = filename.split('_')
                        if len(name_parts) >= 2:
                            client_name = f"{name_parts[0]} {name_parts[1]}"
                        else:
                            client_name = name_parts[0]
                        
                        existing_report = None
                        for report in existing_reports:
                            if getattr(report, 'report_path', '') == report_path:
                                existing_report = report
                                break
                        
                        if existing_report:
                            logger.info(f"Found existing report in database: {report_path}")
                            report_id = getattr(existing_report, 'id', 0)
                            
                            recent_verifications.append({
                                "id": str(report_id),
                                "client_name": getattr(existing_report, 'client_name', client_name),
                                "verification_date": datetime.fromtimestamp(os.path.getmtime(report_file)).isoformat(),
                                "result": "Match Found" if getattr(existing_report, 'risk_level', 'MEDIUM') == "HIGH" else "No Match",
                                "risk_level": getattr(existing_report, 'risk_level', 'MEDIUM'),
                                "report_path": f"/api/v1/compliance/reports/{report_id}/download"
                            })
                            logger.info(f"Added existing report to recent verifications: {client_name}")
                        else:
                            logger.info(f"Creating new report for file: {report_path}, client: {client_name}")
                            
                            report_obj = ComplianceReport(
                                client_name=client_name,
                                client_id=f"AUTO-{i+1}",
                                report_type="UAF",
                                report_path=report_path,
                                country="PA",  # Default to Panama
                                risk_level="MEDIUM",
                                created_at=datetime.fromtimestamp(os.path.getmtime(report_file)),
                                updated_at=datetime.now()
                            )
                            
                            report_id = compliance_reports_db.create(report_obj)
                            logger.info(f"Created new report with ID: {report_id}")
                            
                            recent_verifications.append({
                                "id": str(report_id),
                                "client_name": client_name,
                                "verification_date": datetime.fromtimestamp(os.path.getmtime(report_file)).isoformat(),
                                "result": "No Match",  # Default for new reports
                                "risk_level": "MEDIUM",
                                "report_path": f"/api/v1/compliance/reports/{report_id}/download"
                            })
                            logger.info(f"Added new report to recent verifications: {client_name}")
                    except Exception as e:
                        logger.error(f"Error processing report file {report_file}: {str(e)}")
            
            logger.info(f"Found {len(recent_verifications)} recent verifications from filesystem")
        
        if len(recent_verifications) < 5:
            logger.info("Not enough recent verifications from filesystem, checking database")
            reports = compliance_reports_db.get_all()
            logger.info(f"Retrieved {len(reports)} reports from compliance_reports_db")
            
            try:
                reports.sort(key=lambda r: getattr(r, 'created_at', datetime.now()) if hasattr(r, 'created_at') else datetime.now(), reverse=True)
            except Exception as e:
                logger.warning(f"Error sorting reports: {str(e)}")
            
            for report in reports[:5]:
                try:
                    report_id = getattr(report, 'id', 0) if not isinstance(report, dict) else report.get('id', 0)
                    if any(v.get('id') == str(report_id) for v in recent_verifications):
                        continue
                    
                    if isinstance(report, dict):
                        recent_verifications.append({
                            "id": str(report.get("id", "unknown")),
                            "client_name": report.get("client_name", "Unknown Client"),
                            "verification_date": report.get("created_at", datetime.now()).isoformat() if not isinstance(report.get("created_at"), str) else report.get("created_at"),
                            "result": "Match Found" if report.get("risk_level") == "HIGH" else "No Match",
                            "risk_level": report.get("risk_level", "MEDIUM"),
                            "report_path": f"/api/v1/compliance/reports/{report.get('id', 0)}/download"
                        })
                    else:
                        recent_verifications.append({
                            "id": str(getattr(report, "id", "unknown")),
                            "client_name": getattr(report, "client_name", "Unknown Client"),
                            "verification_date": getattr(report, "created_at", datetime.now()).isoformat() if not isinstance(getattr(report, "created_at", ""), str) else getattr(report, "created_at"),
                            "result": "Match Found" if getattr(report, "risk_level", "") == "HIGH" else "No Match",
                            "risk_level": getattr(report, "risk_level", "MEDIUM"),
                            "report_path": f"/api/v1/compliance/reports/{getattr(report, 'id', 0)}/download"
                        })
                    logger.info(f"Added report from database to recent verifications: {getattr(report, 'client_name', 'Unknown') if not isinstance(report, dict) else report.get('client_name', 'Unknown')}")
                except Exception as e:
                    logger.warning(f"Error processing report {report}: {str(e)}")
        
        recent_verifications = recent_verifications[:5]
        logger.info(f"Final recent verifications count: {len(recent_verifications)}")
        for v in recent_verifications:
            logger.info(f"Verification: {v.get('client_name')} - {v.get('verification_date')}")
        
        # Get list updates
        list_updates = []
        for update in list_updates_db.get_all():
            try:
                if isinstance(update, dict):
                    list_updates.append({
                        "list_name": update.get("list_name", "Unknown"),
                        "update_date": update.get("update_date", datetime.now()).isoformat() if not isinstance(update.get("update_date"), str) else update.get("update_date"),
                        "status": update.get("status", "Unknown")
                    })
                else:
                    list_updates.append({
                        "list_name": getattr(update, "list_name", "Unknown"),
                        "update_date": getattr(update, "update_date", datetime.now()).isoformat() if not isinstance(getattr(update, "update_date", ""), str) else getattr(update, "update_date"),
                        "status": getattr(update, "status", "Unknown")
                    })
            except Exception as e:
                logger.warning(f"Error processing list update {update}: {str(e)}")
        
        reports = compliance_reports_db.get_all()
        pep_matches = len(pep_screening_results_db.get_all())
        sanctions_matches = len(sanctions_screening_results_db.get_all())
        
        high_risk_clients = 0
        for report in reports:
            try:
                if hasattr(report, 'risk_level') and report.risk_level == "HIGH":
                    high_risk_clients += 1
            except Exception:
                pass
        
        dashboard_data = {
            "active_contracts": 42,  # Placeholder data
            "expiring_contracts": 7,
            "pep_matches": pep_matches,
            "sanctions_matches": sanctions_matches,
            "pending_reports": len(reports),
            "high_risk_clients": high_risk_clients,
            "recent_verifications": recent_verifications,
            "recent_list_updates": list_updates
        }
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve dashboard data. Please try again later.")


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
