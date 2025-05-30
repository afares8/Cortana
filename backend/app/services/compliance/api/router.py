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
import asyncio
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
    Get risk assessment for all countries for heatmap visualization,
    including client presence data.

    This endpoint returns a comprehensive risk assessment for all countries,
    including:
    - Risk level (High/Medium/Low)
    - FATF status (Blacklist/Greylist/Not listed)
    - EU High-Risk status
    - Basel AML Index score and rank
    - Last updated date
    - Client data (total clients, risk breakdown)

    The data is used to render the risk heatmap in the frontend, with
    color-coding applied only to countries with registered clients.
    """
    try:
        from app.services.compliance.services.risk_matrix import RiskMatrix
        from app.legal.services import get_clients
        
        risk_matrix = RiskMatrix()
        await risk_matrix.initialize()
        
        country_risk_data = await risk_matrix.get_all_countries_risk()
        
        from app.legal.services import get_clients
        
        clients = get_clients(skip=0, limit=1000)
        client_countries = {}
        
        logger.info(f"Retrieved {len(clients)} clients")
        for client in clients:
            logger.info(f"Client: {client.id} - {client.name} - Country: {getattr(client, 'country', 'None')}")
            
            country = getattr(client, 'country', None)
            if country and isinstance(country, str) and country.strip():
                country_code = country.upper()
                if country_code not in client_countries:
                    client_countries[country_code] = {
                        "total_clients": 0,
                        "high_risk_clients": 0,
                        "medium_risk_clients": 0,
                        "low_risk_clients": 0,
                        "clients": []
                    }
                
                client_risk_score = getattr(client, "risk_score", 0)
                client_countries[country_code]["total_clients"] += 1
                client_countries[country_code]["clients"].append({
                    "id": client.id,
                    "name": client.name,
                    "risk_score": client_risk_score
                })
                
                country_data = country_risk_data.get("countries", {}).get(country_code, {})
                country_risk_score = country_data.get("basel_score", 0)
                country_risk_level = country_data.get("risk_level", "").upper()
                
                if country_risk_score >= 8.0 or country_risk_level == "HIGH":
                    client_countries[country_code]["high_risk_clients"] += 1
                elif country_risk_score >= 5.0 or country_risk_level == "MEDIUM":
                    client_countries[country_code]["medium_risk_clients"] += 1
                else:
                    client_countries[country_code]["low_risk_clients"] += 1
        
        for country_code, country_data in country_risk_data.get("countries", {}).items():
            country_data["client_data"] = client_countries.get(country_code, {
                "total_clients": 0,
                "high_risk_clients": 0,
                "medium_risk_clients": 0,
                "low_risk_clients": 0,
                "clients": []
            })
        
        return country_risk_data
        
    except Exception as e:
        logger.error(f"Error retrieving country risk data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve country risk data. Please try again later.")


@router.post("/country-risk/analysis", response_model=Dict[str, Any])
async def get_country_risk_analysis_endpoint(
    user_id: Optional[int] = Body(None, embed=True),
    user_email: Optional[str] = Body(None, embed=True),
):
    """
    Generate an AI-powered analysis of country risk data and client distribution.
    
    This endpoint:
    1. Retrieves country risk data from the compliance service
    2. Retrieves client data to identify countries with clients
    3. Uses the AI service to generate an analysis based on this data
    4. Logs the analysis in the audit system
    5. Returns the analysis with metadata
    """
    try:
        from app.services.compliance.services.risk_matrix import RiskMatrix
        from app.services.ai.services.ai_service import ai_service
        from app.services.audit.services.audit_service import audit_service
        from app.legal.services import get_clients
        from datetime import datetime, timezone
        from pydantic import BaseModel
        
        class RiskAnalysisResponse(BaseModel):
            """Response model for risk analysis."""
            analysis: str
            global_risk_score: float
            recommended_score: float
            high_risk_countries_with_clients: List[str]
            timestamp: str
            data_sources: List[str]
        
        risk_matrix = RiskMatrix()
        await risk_matrix.initialize()
        
        country_risk_data = await risk_matrix.get_all_countries_risk()
        
        clients = get_clients(skip=0, limit=1000)
        client_countries = {}
        
        for client in clients:
            if hasattr(client, 'country') and client.country and client.country.strip():
                country_code = client.country.upper()
                if country_code not in client_countries:
                    client_countries[country_code] = []
                client_countries[country_code].append({
                    "id": client.id,
                    "name": client.name,
                    "risk_score": getattr(client, "risk_score", None)
                })
        
        high_risk_countries = []
        high_risk_countries_with_clients = []
        medium_risk_countries_with_clients = []
        low_risk_countries_with_clients = []
        
        for country_code, country_data in country_risk_data.get("countries", {}).items():
            risk_score = country_data.get("risk_score", 0)
            country_name = country_data.get("country_name", "")
            
            if risk_score >= 8.0:
                high_risk_countries.append(country_name)
                if country_code in client_countries:
                    high_risk_countries_with_clients.append(country_name)
            elif risk_score >= 5.0 and country_code in client_countries:
                medium_risk_countries_with_clients.append(country_name)
            elif country_code in client_countries:
                low_risk_countries_with_clients.append(country_name)
        
        total_countries = len(country_risk_data.get("countries", {}))
        high_risk_count = len([c for c, data in country_risk_data.get("countries", {}).items() 
                              if data.get("risk_score", 0) >= 8.0])
        medium_risk_count = len([c for c, data in country_risk_data.get("countries", {}).items() 
                                if 5.0 <= data.get("risk_score", 0) < 8.0])
        low_risk_count = len([c for c, data in country_risk_data.get("countries", {}).items() 
                             if data.get("risk_score", 0) < 5.0])
        
        total_risk_score = sum(data.get("risk_score", 0) for data in country_risk_data.get("countries", {}).values())
        global_risk_score = total_risk_score / total_countries if total_countries > 0 else 0
        
        client_countries_risk = [
            country_risk_data.get("countries", {}).get(country_code, {}).get("risk_score", 0)
            for country_code in client_countries.keys()
            if country_code in country_risk_data.get("countries", {})
        ]
        
        client_weighted_risk = sum(client_countries_risk) / len(client_countries_risk) if client_countries_risk else 0
        
        context_data = {
            "risk_data": {
                "global_risk_score": round(global_risk_score, 2),
                "client_weighted_risk": round(client_weighted_risk, 2),
                "recommended_score": 3.0,
                "high_risk_count": high_risk_count,
                "medium_risk_count": medium_risk_count,
                "low_risk_count": low_risk_count,
                "total_countries": total_countries,
                "high_risk_countries_with_clients": high_risk_countries_with_clients,
                "medium_risk_countries_with_clients": medium_risk_countries_with_clients,
                "low_risk_countries_with_clients": low_risk_countries_with_clients,
                "fatf_blacklist": [
                    country_data.get("country_name", code) 
                    for code, country_data in country_risk_data.get("countries", {}).items()
                    if country_data.get("fatf_status", "") == "blacklist"
                ],
                "fatf_greylist": [
                    country_data.get("country_name", code) 
                    for code, country_data in country_risk_data.get("countries", {}).items()
                    if country_data.get("fatf_status", "") == "greylist"
                ],
                "basel_index_top10": sorted(
                    [(code, data.get("country_name", ""), data.get("risk_score", 0)) 
                     for code, data in country_risk_data.get("countries", {}).items()],
                    key=lambda x: x[2], reverse=True
                )[:10],
                "data_sources": country_risk_data.get("sources", ["Basel AML Index", "FATF Lists"])
            },
            "client_data": {
                "total_clients": len(clients),
                "clients_by_country": {
                    country: len(clients_list) for country, clients_list in client_countries.items()
                },
                "clients_by_country_names": {
                    country_risk_data.get("countries", {}).get(country, {}).get("country_name", country): len(clients_list) 
                    for country, clients_list in client_countries.items()
                    if country in country_risk_data.get("countries", {})
                },
                "high_risk_clients_count": sum(
                    len(clients_list) for country, clients_list in client_countries.items()
                    if country in country_risk_data.get("countries", {}) and 
                    country_risk_data.get("countries", {}).get(country, {}).get("risk_score", 0) >= 8.0
                ),
                "risk_summary_spanish": f"Panamá: {client_countries.get('PA', []).__len__()} cliente — Riesgo Bajo, Brasil: {client_countries.get('BR', []).__len__()} clientes — Riesgo Bajo, México: {client_countries.get('MX', []).__len__()} clientes — Riesgo Medio, Colombia: {client_countries.get('CO', []).__len__()} clientes — Riesgo Alto"
            }
        }
        
        query = """
        Eres un analista experto en cumplimiento normativo internacional. Basado en los siguientes datos de riesgo por país y distribución de clientes, genera un análisis de cumplimiento enfocado en identificar amenazas, oportunidades de mejora en la gestión de riesgo y recomendaciones claras. El análisis debe ser profesional, detallado y redactado completamente en español. No resumas la data, interprétala y emite juicio experto.

        Clientes por país:
        - Panamá: 1 cliente — Riesgo Bajo
        - Brasil: 10 clientes — Riesgo Bajo
        - México: 3 clientes — Riesgo Medio
        - Colombia: 2 clientes — Riesgo Alto

        Índices utilizados:
        - Basel AML Index
        - FATF Lists
        - EU High-Risk Third Countries

        Estructura esperada del análisis:
        1. Evaluación del riesgo actual de nuestros clientes según su país.
        2. Comparación con estándares FATF y Basel.
        3. Implicaciones para nuestra política de cumplimiento.
        4. Recomendaciones para mitigar riesgos y priorizar acciones.
        El análisis debe ser claro, sin lenguaje genérico, sin repetir que "el riesgo global es cambiante" y sin hablar de temas geopolíticos irrelevantes. Usa los datos entregados y genera conocimiento útil.

        ✅ ¿Qué debe hacer Mistral?
        🔍 Evaluar la exposición al riesgo de la empresa según sus clientes.

        📊 Comparar esa exposición con estándares de riesgo internacional.

        🧠 Ofrecer ideas concretas: por ejemplo, "se recomienda suspender onboarding en Colombia hasta nueva evaluación" o "establecer límites de exposición en México".

        ✍️ Usar un estilo profesional en español, como un informe ejecutivo de cumplimiento.
        """
        
        from app.services.ai.utils.prompt_builder import prompt_builder
        from app.services.ai.utils.intent_classifier import IntentType
        enhanced_prompt = prompt_builder.build_prompt(query, IntentType.COMPLIANCE, context_data, "es")
        
        ai_response = await ai_service.generate(
            inputs=enhanced_prompt,
            max_new_tokens=800,
            temperature=0.7,
            debug=True
        )
        
        analysis_text = ai_response.generated_text if hasattr(ai_response, 'generated_text') else str(ai_response)
        
        timestamp = datetime.now(timezone.utc).isoformat()
        response = {
            "analysis": analysis_text,
            "global_risk_score": round(client_weighted_risk, 2),
            "recommended_score": 3.0,
            "high_risk_countries_with_clients": high_risk_countries_with_clients,
            "timestamp": timestamp,
            "data_sources": country_risk_data.get("sources", ["Basel AML Index", "FATF Lists"])
        }
        
        from app.services.audit.schemas.audit import AuditLogCreate
        
        audit_log = AuditLogCreate(
            user_id=user_id,
            user_email=user_email,
            action="generate",
            entity_type="risk_analysis",
            entity_id=f"risk_analysis_{timestamp}",
            details={
                "analysis": analysis_text,
                "global_risk_score": round(client_weighted_risk, 2),
                "high_risk_countries_with_clients": high_risk_countries_with_clients,
                "data_sources": country_risk_data.get("sources", ["Basel AML Index", "FATF Lists"])
            },
            ip_address=None
        )
        
        await audit_service.create_audit_log(audit_log)
        
        return response
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating risk analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating risk analysis: {str(e)}"
        )


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
        
        dashboard_data = {
            "total_screenings": 120,
            "active_contracts": 42,
            "expiring_contracts": 3,
            "pep_matches": 5,
            "sanctions_matches": 1,
            "pending_reports": 5,
            "high_risk_clients": 3,
            "flagged_clients": 8,
            "last_update": datetime.now().isoformat(),
            "sanction_sources": ["OFAC", "UN", "EU"],
            "recent_verifications": [
                {
                    "id": "v1",
                    "client_name": "Acme Corp",
                    "verification_date": datetime.now().isoformat(),
                    "result": "no_match",
                    "risk_level": "Low",
                    "report_path": "/uploads/reports/acme_verification.pdf"
                },
                {
                    "id": "v2",
                    "client_name": "Global Industries",
                    "verification_date": (datetime.now() - timedelta(days=1)).isoformat(),
                    "result": "potential_match",
                    "risk_level": "Medium",
                    "report_path": "/uploads/reports/global_verification.pdf"
                },
                {
                    "id": "v3",
                    "client_name": "Oceanic Airlines",
                    "verification_date": (datetime.now() - timedelta(days=2)).isoformat(),
                    "result": "confirmed_match",
                    "risk_level": "High",
                    "report_path": "/uploads/reports/oceanic_verification.pdf"
                }
            ],
            "recent_list_updates": [
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
                    "list_name": "PEP Database",
                    "update_date": (datetime.now() - timedelta(days=3)).isoformat(),
                    "status": "Success"
                }
            ]
        }
        
        try:
            from app.services.websocket import broadcast_dashboard_update
            asyncio.create_task(broadcast_dashboard_update(dashboard_data))
            logger.info("Dashboard update broadcasted to WebSocket clients")
        except Exception as ws_error:
            logger.error(f"Error broadcasting dashboard update: {str(ws_error)}")
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        error_data = {
            "total_screenings": 0,
            "active_contracts": 0,
            "expiring_contracts": 0,
            "pep_matches": 0,
            "sanctions_matches": 0,
            "pending_reports": 0,
            "high_risk_clients": 0,
            "flagged_clients": 0,
            "last_update": datetime.now().isoformat(),
            "sanction_sources": [],
            "recent_verifications": [],
            "recent_list_updates": []
        }
        return error_data



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
