from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, UploadFile, File
from pydantic import BaseModel

from app.services.ai.models.ai_model import AIAnalysisResult, ExtractedClause, RiskScore, AIQuery
from app.services.ai.schemas.ai_schema import GenerateRequest, GenerateResponse
from app.services.ai.schemas.contextual_schema import ContextualGenerateRequest, ContextualGenerateResponse
from app.services.ai.services.ai_service import ai_service

router = APIRouter()

@router.post("/analyze/contract/{contract_id}", response_model=AIAnalysisResult)
async def analyze_contract_endpoint(
    contract_id: int = Path(..., gt=0),
    analysis_type: str = Query(..., description="Type of analysis: clause_extraction, risk_scoring, anomaly_detection")
):
    """Analyze a contract using AI."""
    result = await ai_service.analyze_contract(contract_id, analysis_type)
    if not result:
        raise HTTPException(status_code=404, detail="Contract not found or analysis failed")
    return result

@router.post("/extract/clauses", response_model=List[ExtractedClause])
async def extract_clauses_endpoint(
    file: UploadFile = File(...),
    clause_types: Optional[List[str]] = Query(None, description="Types of clauses to extract. If not provided, all types will be extracted.")
):
    """Extract clauses from a contract document."""
    clauses = await ai_service.extract_clauses(file, clause_types)
    return clauses

@router.post("/score/risk", response_model=RiskScore)
async def score_risk_endpoint(
    contract_id: int = Query(..., gt=0, description="ID of the contract to score")
):
    """Score the risk of a contract."""
    risk_score = await ai_service.score_risk(contract_id)
    if not risk_score:
        raise HTTPException(status_code=404, detail="Contract not found or risk scoring failed")
    return risk_score

@router.post("/detect/anomalies", response_model=Dict[str, Any])
async def detect_anomalies_endpoint(
    contract_id: int = Query(..., gt=0, description="ID of the contract to analyze")
):
    """Detect anomalies in a contract."""
    anomalies = await ai_service.detect_anomalies(contract_id)
    if not anomalies:
        raise HTTPException(status_code=404, detail="Contract not found or anomaly detection failed")
    return anomalies

@router.post("/query", response_model=AIQuery)
async def query_endpoint(
    query: str = Body(..., embed=True),
    user_id: Optional[int] = Body(None, embed=True)
):
    """Query the AI system."""
    result = await ai_service.query(query, user_id)
    return result

@router.post("/mistral/generate", response_model=GenerateResponse)
async def generate_endpoint(request: GenerateRequest):
    """Generate text using the Mistral model."""
    response = await ai_service.generate(
        inputs=request.inputs,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        debug=request.debug
    )
    return response

@router.post("/contextual-generate", response_model=ContextualGenerateResponse)
async def contextual_generate_endpoint(request: ContextualGenerateRequest):
    """
    Generate text using the Mistral model with context from internal application data.
    
    This endpoint:
    1. Classifies the intent of the query
    2. Retrieves relevant context data based on the intent
    3. Builds an enhanced prompt with the context data
    4. Generates a response using the enhanced prompt
    5. Returns the response with additional context information
    
    Example:
    ```
    {
      "query": "Que es lo que tengo pendiente?",
      "user_id": 1,
      "max_new_tokens": 500,
      "temperature": 0.7,
      "top_p": 0.9,
      "debug": false
    }
    ```
    """
    response = await ai_service.contextual_generate(
        query=request.query,
        user_id=request.user_id,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        debug=request.debug
    )
    return response
