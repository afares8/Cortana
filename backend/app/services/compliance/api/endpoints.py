from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, File, UploadFile
from enum import Enum

from app.services.compliance.models.compliance import (
    ComplianceReport, PEPScreeningResult, 
    SanctionsScreeningResult, DocumentRetentionPolicy
)
from app.services.compliance.services.compliance_service import compliance_service
from app.services.compliance.services.manual_integration_service import (
    DueDiligenceLevel, RiskLevel, RiskCategory
)

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

@router.post("/ros-reports", response_model=ComplianceReport, status_code=201)
async def generate_ros_report_endpoint(
    transaction_id: int = Body(..., embed=True),
    client_id: int = Body(..., embed=True)
):
    """
    Generate a Suspicious Activity Report (ROS) for a suspicious transaction.
    """
    return await compliance_service.generate_ros_report(transaction_id, client_id)

@router.post("/suspicious-activity", response_model=Dict[str, Any])
async def detect_suspicious_activity_endpoint(
    transaction_id: int = Body(..., embed=True),
    transaction_data: Optional[Dict[str, Any]] = Body(None, embed=True),
    client_id: Optional[int] = Body(None, embed=True)
):
    """
    Detect suspicious activity in a transaction based on the compliance manual.
    """
    return await compliance_service.detect_suspicious_activity(
        transaction_id=transaction_id,
        transaction_data=transaction_data,
        client_id=client_id
    )

@router.get("/due-diligence", response_model=Dict[str, Any])
async def get_due_diligence_requirements_endpoint(
    client_id: int,
    due_diligence_level: Optional[str] = None,
    client_type: str = "individual"
):
    """
    Get due diligence requirements for a client based on the compliance manual.
    """
    return await compliance_service.get_due_diligence_requirements(
        client_id=client_id,
        due_diligence_level=due_diligence_level,
        client_type=client_type
    )

@router.post("/risk-assessment", response_model=Dict[str, Any])
async def calculate_client_risk_endpoint(
    client_id: int = Body(..., embed=True),
    client_data: Optional[Dict[str, Any]] = Body(None, embed=True)
):
    """
    Calculate risk score for a client based on the risk matrices in the compliance manual.
    """
    return await compliance_service.calculate_client_risk(
        client_id=client_id,
        client_data=client_data
    )

@router.post("/pep-screening", response_model=PEPScreeningResult, status_code=201)
async def create_pep_screening_endpoint(
    client_id: int = Body(..., embed=True),
    name: Optional[str] = Body(None, embed=True),
    country: Optional[str] = Body(None, embed=True)
):
    """
    Screen a client against PEP (Politically Exposed Person) lists.
    """
    from app.services.compliance.schemas.compliance import PEPScreeningResultCreate
    
    screening_data = PEPScreeningResultCreate(
        client_id=client_id,
        match_status="pending",
        match_details={"name": name, "country": country} if name else None,
        screened_by="system",
        screened_at=datetime.utcnow(),
        risk_level="unknown",
        notes="Automated PEP screening"
    )
    
    return await compliance_service.create_pep_screening(screening_data)

@router.post("/sanctions-screening", response_model=SanctionsScreeningResult, status_code=201)
async def create_sanctions_screening_endpoint(
    client_id: int = Body(..., embed=True),
    name: Optional[str] = Body(None, embed=True),
    entity_type: Optional[str] = Body("Person", embed=True),
    country: Optional[str] = Body(None, embed=True)
):
    """
    Screen a client against sanctions lists.
    """
    from app.services.compliance.schemas.compliance import SanctionsScreeningResultCreate
    
    screening_data = SanctionsScreeningResultCreate(
        client_id=client_id,
        match_status="pending",
        match_details={
            "name": name, 
            "entity_type": entity_type,
            "country": country
        } if name else None,
        screened_by="system",
        screened_at=datetime.utcnow(),
        risk_level="unknown",
        notes="Automated sanctions screening"
    )
    
    return await compliance_service.create_sanctions_screening(screening_data)

@router.post("/retention-policies", response_model=DocumentRetentionPolicy, status_code=201)
async def create_retention_policy_endpoint(
    document_type: str = Body(..., embed=True),
    retention_period_days: Optional[int] = Body(None, embed=True),
    legal_basis: Optional[str] = Body(None, embed=True),
    is_active: bool = Body(True, embed=True)
):
    """
    Create a new document retention policy based on compliance manual requirements.
    """
    from app.services.compliance.schemas.compliance import DocumentRetentionPolicyCreate
    
    policy_data = DocumentRetentionPolicyCreate(
        document_type=document_type,
        retention_period_days=retention_period_days,
        legal_basis=legal_basis,
        is_active=is_active,
        created_by="system"
    )
    
    return await compliance_service.create_retention_policy(policy_data)

@router.get("/retention-policies", response_model=List[DocumentRetentionPolicy])
async def get_retention_policies_endpoint():
    """
    Get all document retention policies.
    """
    return await compliance_service.get_retention_policies()

@router.post("/manual/upload", response_model=Dict[str, Any])
async def upload_compliance_manual_endpoint(
    file: UploadFile = File(...),
    document_type: str = "compliance_manual",
    document_metadata: Optional[Dict[str, Any]] = Body(None)
):
    """
    Upload and process a compliance manual PDF for embedding.
    """
    import tempfile
    import os
    from app.services.compliance.utils.document_embeddings import document_embeddings
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name
    
    try:
        if not document_metadata:
            document_metadata = {
                "document_type": document_type,
                "filename": file.filename,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        
        success = document_embeddings.embed_document(
            pdf_path=temp_file_path,
            document_metadata=document_metadata
        )
        
        if success:
            return {
                "status": "success",
                "message": "Compliance manual uploaded and processed successfully",
                "document_metadata": document_metadata
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to process the compliance manual"
            )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/manual/query", response_model=Dict[str, Any])
async def query_compliance_manual_endpoint(
    query: str = Body(..., embed=True),
    max_results: int = Body(5, embed=True)
):
    """
    Query the compliance manual using natural language.
    """
    from app.services.compliance.services.manual_integration_service import compliance_manual_integration
    
    result = await compliance_manual_integration.query_compliance_manual(
        query=query,
        max_results=max_results
    )
    
    return result

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_compliance_dashboard_endpoint():
    """
    Get data for the compliance dashboard.
    """
    return await compliance_service.get_compliance_dashboard_data()
