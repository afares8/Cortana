from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class AIAnalysisResultBase(BaseModel):
    contract_id: int
    analysis_type: str  # clause_extraction, risk_scoring, anomaly_detection
    result: Dict[str, Any]
    model_used: str
    processing_time: float  # in seconds
    language: Optional[str] = None
    confidence_score: Optional[float] = None

class AIAnalysisResultCreate(AIAnalysisResultBase):
    pass

class AIAnalysisResultInDBBase(AIAnalysisResultBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AIAnalysisResult(AIAnalysisResultInDBBase):
    pass

class ExtractedClauseBase(BaseModel):
    clause_type: str  # confidentiality, termination, penalties, jurisdiction, obligations
    text: str
    start_index: int
    end_index: int
    confidence: float

class ExtractedClause(ExtractedClauseBase):
    pass

class RiskScoreBase(BaseModel):
    score: float  # 0-100
    factors: List[Dict[str, Any]]
    recommendations: List[str]

class RiskScore(RiskScoreBase):
    pass

class AIQueryBase(BaseModel):
    user_id: Optional[int] = None
    query_text: str
    response_text: str
    model_used: str
    processing_time: float  # in seconds
    language: Optional[str] = None
    is_fallback: bool = False

class AIQueryCreate(AIQueryBase):
    pass

class AIQueryInDBBase(AIQueryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AIQuery(AIQueryInDBBase):
    pass

class GenerateRequest(BaseModel):
    inputs: str
    max_new_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    debug: Optional[bool] = False

class GenerateResponse(BaseModel):
    generated_text: str
    is_fallback: bool = False
    model: str = "teknium/OpenHermes-2.5-Mistral-7B"
    original_input: Optional[str] = None
    processed_input: Optional[str] = None
    spanish_processing: Optional[Dict[str, Any]] = None
    debug_info: Optional[Dict[str, Any]] = None
