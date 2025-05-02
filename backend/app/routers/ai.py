"""
Router for AI-related endpoints.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query, Body, BackgroundTasks
import logging

from app.models.contract import Contract
from app.models.ai_models import ExtractedClause, RiskScore, ComplianceCheck, AIQuery, ContractAnomaly
from app.schemas.ai_schemas import (
    ExtractedClause as ExtractedClauseSchema,
    RiskScore as RiskScoreSchema,
    ComplianceCheck as ComplianceCheckSchema,
    AIQuery as AIQuerySchema,
    ClauseExtractionRequest,
    NaturalLanguageQueryRequest,
)
from app.db.init_db import (
    contracts_db, 
    extracted_clauses_db, 
    risk_scores_db, 
    compliance_checks_db, 
    ai_queries_db, 
    contract_anomalies_db
)
from app.services.ai.contract_intelligence import (
    extract_clauses,
    calculate_risk_score,
    detect_anomalies,
    process_contract,
    extract_text_from_file,
)
from app.services.ai.mistral_client import mistral_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/extract-clauses", response_model=List[ExtractedClauseSchema])
async def extract_contract_clauses(request: ClauseExtractionRequest):
    """
    Extract clauses from a contract document.
    """
    contract = contracts_db.get(request.contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    text_content = request.text_content
    if not text_content and contract.file_path:
        text_content = extract_text_from_file(contract.file_path)
    
    if not text_content:
        raise HTTPException(status_code=400, detail="No text content available for extraction")
    
    clauses = extract_clauses(contract, text_content)
    
    saved_clauses = []
    for clause in clauses:
        existing_clauses = extracted_clauses_db.get_multi(
            filters={"contract_id": contract.id, "start_position": clause.start_position}
        )
        if existing_clauses:
            saved_clauses.append(existing_clauses[0])
        else:
            saved_clause = extracted_clauses_db.create(obj_in=clause)
            saved_clauses.append(saved_clause)
    
    return saved_clauses


@router.get("/clauses/{contract_id}", response_model=List[ExtractedClauseSchema])
async def get_contract_clauses(contract_id: int, clause_type: Optional[str] = None):
    """
    Get extracted clauses for a contract.
    """
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    filters = {"contract_id": contract_id}
    if clause_type:
        filters["clause_type"] = clause_type
    
    clauses = extracted_clauses_db.get_multi(filters=filters)
    return clauses


@router.post("/risk-score/{contract_id}", response_model=RiskScoreSchema)
async def calculate_contract_risk(contract_id: int):
    """
    Calculate risk score for a contract.
    """
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    clauses = extracted_clauses_db.get_multi(filters={"contract_id": contract_id})
    
    if not clauses:
        text_content = extract_text_from_file(contract.file_path)
        clauses = extract_clauses(contract, text_content)
        for clause in clauses:
            extracted_clauses_db.create(obj_in=clause)
    
    risk_score = calculate_risk_score(contract, clauses)
    
    existing_scores = risk_scores_db.get_multi(filters={"contract_id": contract_id})
    if existing_scores:
        updated_score = risk_scores_db.update(existing_scores[0].id, risk_score)
        return updated_score
    else:
        saved_score = risk_scores_db.create(obj_in=risk_score)
        return saved_score


@router.get("/risk-score/{contract_id}", response_model=RiskScoreSchema)
async def get_contract_risk_score(contract_id: int):
    """
    Get risk score for a contract.
    """
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    risk_scores = risk_scores_db.get_multi(filters={"contract_id": contract_id})
    if not risk_scores:
        raise HTTPException(status_code=404, detail="Risk score not found for this contract")
    
    return risk_scores[0]


@router.post("/anomalies/{contract_id}", response_model=List[ContractAnomaly])
async def detect_contract_anomalies(contract_id: int, background_tasks: BackgroundTasks):
    """
    Detect anomalies in a contract using both traditional NLP and Mistral 7B model.
    """
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    clauses = extracted_clauses_db.get_multi(filters={"contract_id": contract_id})
    
    if not clauses:
        text_content = extract_text_from_file(contract.file_path)
        clauses = extract_clauses(contract, text_content)
        for clause in clauses:
            extracted_clauses_db.create(obj_in=clause)
    
    # Detect anomalies using traditional NLP methods
    anomalies = detect_anomalies(contract, clauses)
    
    saved_anomalies = []
    for anomaly in anomalies:
        existing_anomalies = contract_anomalies_db.get_multi(
            filters={
                "contract_id": contract_id,
                "anomaly_type": anomaly.anomaly_type,
                "description": anomaly.description
            }
        )
        if existing_anomalies:
            saved_anomalies.append(existing_anomalies[0])
        else:
            saved_anomaly = contract_anomalies_db.create(obj_in=anomaly)
            saved_anomalies.append(saved_anomaly)
    
    background_tasks.add_task(detect_mistral_anomalies, contract_id)
    
    return saved_anomalies

async def detect_mistral_anomalies(contract_id: int):
    """
    Detect anomalies using the Mistral 7B model.
    This runs as a background task to avoid blocking the API response.
    """
    try:
        contract = contracts_db.get(contract_id)
        if not contract:
            logger.error(f"Contract {contract_id} not found for Mistral anomaly detection")
            return
        
        text_content = extract_text_from_file(contract.file_path)
        if not text_content:
            logger.error(f"No text content available for contract {contract_id}")
            return
        
        prompt = """Analyze this contract for potential legal issues, anomalies, or risks. 
        Focus on unusual clauses, missing standard protections, or terms that might be disadvantageous.
        Return your findings as a JSON array of objects with 'anomaly_type', 'description', and 'severity' (high/medium/low) fields."""
        
        analysis = await mistral_client.analyze_contract(text_content, prompt)
        
        if isinstance(analysis, dict) and "anomalies" in analysis:
            for anomaly_data in analysis.get("anomalies", []):
                anomaly = ContractAnomaly(
                    contract_id=contract_id,
                    anomaly_type=anomaly_data.get("anomaly_type", "mistral_identified_issue"),
                    description=anomaly_data.get("description", "Unspecified anomaly"),
                    severity=anomaly_data.get("severity", "medium"),
                    detected_at=datetime.now(),
                    metadata={"source": "mistral", "raw_data": anomaly_data}
                )
                
                existing_anomalies = contract_anomalies_db.get_multi(
                    filters={
                        "contract_id": contract_id,
                        "description": anomaly.description
                    }
                )
                
                if not existing_anomalies:
                    contract_anomalies_db.create(obj_in=anomaly)
        
        logger.info(f"Mistral anomaly detection completed for contract {contract_id}")
        
    except Exception as e:
        logger.error(f"Error in Mistral anomaly detection: {e}")



@router.get("/anomalies/{contract_id}", response_model=List[ContractAnomaly])
async def get_contract_anomalies(contract_id: int, severity: Optional[str] = None):
    """
    Get detected anomalies for a contract.
    """
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    filters = {"contract_id": contract_id}
    if severity:
        filters["severity"] = severity
    
    anomalies = contract_anomalies_db.get_multi(filters=filters)
    return anomalies


@router.post("/process/{contract_id}", response_model=Dict[str, Any])
async def process_contract_ai(contract_id: int, background_tasks: BackgroundTasks):
    """
    Process a contract with AI to extract clauses, calculate risk, and detect anomalies.
    Uses both traditional NLP and the Mistral 7B model for enhanced analysis.
    """
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    result = process_contract(contract)
    
    background_tasks.add_task(enhance_contract_analysis, contract_id)
    
    return result

async def enhance_contract_analysis(contract_id: int):
    """
    Enhance contract analysis using the Mistral 7B model.
    This runs as a background task to avoid blocking the API response.
    """
    try:
        contract = contracts_db.get(contract_id)
        if not contract:
            logger.error(f"Contract {contract_id} not found for enhanced analysis")
            return
        
        text_content = extract_text_from_file(contract.file_path)
        if not text_content:
            logger.error(f"No text content available for contract {contract_id}")
            return
        
        risk_analysis = await mistral_client.analyze_contract(
            text_content, 
            "Identify potential legal risks and anomalies in this contract"
        )
        
        clause_analysis = await mistral_client.analyze_contract(
            text_content,
            "Extract and categorize the key clauses in this contract"
        )
        
        if isinstance(risk_analysis, dict) and "risks" in risk_analysis:
            for risk in risk_analysis.get("risks", []):
                anomaly = ContractAnomaly(
                    contract_id=contract_id,
                    anomaly_type="mistral_identified_risk",
                    description=risk.get("description", "Unknown risk"),
                    severity=risk.get("severity", "medium"),
                    detected_at=datetime.now(),
                    metadata={"source": "mistral", "details": risk}
                )
                contract_anomalies_db.create(obj_in=anomaly)
        
        logger.info(f"Enhanced analysis completed for contract {contract_id}")
        
    except Exception as e:
        logger.error(f"Error in enhanced contract analysis: {e}")



@router.post("/query", response_model=AIQuerySchema)
async def natural_language_query(request: NaturalLanguageQueryRequest):
    """
    Process a natural language query about contracts using the Mistral 7B model.
    """
    query_text = request.query
    
    contracts = list(contracts_db.data.values())
    
    related_contracts = []
    
    keywords = query_text.lower().split()
    for contract in contracts:
        contract_text = f"{contract.title} {contract.client_name} {contract.contract_type} {contract.description or ''}"
        contract_text = contract_text.lower()
        
        if any(keyword in contract_text for keyword in keywords):
            related_contracts.append(contract)
    
    related_clauses = []
    context_text = ""
    
    for contract in related_contracts:
        clauses = extracted_clauses_db.get_multi(filters={"contract_id": contract.id})
        related_clauses.extend(clauses)
        
        context_text += f"Contract: {contract.title} (Client: {contract.client_name}, Type: {contract.contract_type})\n"
        contract_clauses = [c for c in clauses]
        if contract_clauses:
            context_text += "Clauses:\n"
            for clause in contract_clauses[:3]:  # Limit to top 3 clauses per contract
                context_text += f"- {clause.clause_type.capitalize()}: {clause.clause_text[:200]}...\n"
        context_text += "\n"
    
    try:
        if context_text:
            response_text = await mistral_client.query_legal_assistant(query_text, context_text)
        else:
            response_text = await mistral_client.query_legal_assistant(
                query_text, 
                "No specific contracts found matching this query."
            )
    except Exception as e:
        logger.error(f"Error querying Mistral model: {e}")
        if not related_contracts:
            response_text = f"I couldn't find any contracts matching your query: '{query_text}'"
        else:
            response_text = f"I found {len(related_contracts)} contracts related to your query: '{query_text}'\n\n"
            
            for i, contract in enumerate(related_contracts[:3]):  # Limit to top 3 for brevity
                response_text += f"{i+1}. {contract.title} (Client: {contract.client_name}, Type: {contract.contract_type})\n"
                
                contract_clauses = [c for c in related_clauses if c.contract_id == contract.id]
                if contract_clauses:
                    response_text += "   Relevant clauses:\n"
                    for j, clause in enumerate(contract_clauses[:2]):  # Limit to top 2 clauses
                        response_text += f"   - {clause.clause_type.capitalize()}: {clause.clause_text[:100]}...\n"
    
    query = AIQuery(
        query_text=query_text,
        response_text=response_text,
        related_contract_ids=[c.id for c in related_contracts],
    )
    saved_query = ai_queries_db.create(obj_in=query)
    
    return saved_query


@router.get("/dashboard/stats", response_model=Dict[str, Any])
async def get_ai_dashboard_stats():
    """
    Get AI dashboard statistics.
    """
    contracts = list(contracts_db.data.values())
    
    risk_scores = list(risk_scores_db.data.values())
    
    anomalies = list(contract_anomalies_db.data.values())
    
    total_contracts = len(contracts)
    analyzed_contracts = len(set(rs.contract_id for rs in risk_scores))
    high_risk_contracts = len([rs for rs in risk_scores if rs.overall_score > 0.7])
    medium_risk_contracts = len([rs for rs in risk_scores if 0.3 <= rs.overall_score <= 0.7])
    low_risk_contracts = len([rs for rs in risk_scores if rs.overall_score < 0.3])
    
    total_anomalies = len(anomalies)
    high_severity_anomalies = len([a for a in anomalies if a.severity == "high"])
    medium_severity_anomalies = len([a for a in anomalies if a.severity == "medium"])
    low_severity_anomalies = len([a for a in anomalies if a.severity == "low"])
    
    extracted_clauses = list(extracted_clauses_db.data.values())
    total_clauses = len(extracted_clauses)
    clause_types = {}
    for clause in extracted_clauses:
        clause_types[clause.clause_type] = clause_types.get(clause.clause_type, 0) + 1
    
    anomalies_by_source = {
        "traditional_nlp": len([a for a in anomalies if not a.metadata or a.metadata.get("source") != "mistral"]),
        "mistral": len([a for a in anomalies if a.metadata and a.metadata.get("source") == "mistral"])
    }
    
    ai_queries = list(ai_queries_db.data.values())
    recent_queries = sorted(ai_queries, key=lambda q: getattr(q, 'created_at', datetime.now()), reverse=True)[:5]
    recent_query_texts = [q.query_text for q in recent_queries]
    
    return {
        "total_contracts": total_contracts,
        "analyzed_contracts": analyzed_contracts,
        "risk_distribution": {
            "high_risk": high_risk_contracts,
            "medium_risk": medium_risk_contracts,
            "low_risk": low_risk_contracts,
        },
        "anomalies": {
            "total": total_anomalies,
            "high_severity": high_severity_anomalies,
            "medium_severity": medium_severity_anomalies,
            "low_severity": low_severity_anomalies,
            "by_source": anomalies_by_source
        },
        "clauses": {
            "total": total_clauses,
            "by_type": clause_types,
        },
        "ai_activity": {
            "recent_queries": recent_query_texts,
            "total_queries": len(ai_queries),
            "model": "OpenHermes-2.5-Mistral-7B"
        }
    }
