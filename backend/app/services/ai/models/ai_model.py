from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.models.base import TimestampModel

class AIAnalysisResult(TimestampModel):
    id: int
    contract_id: int
    analysis_type: str  # clause_extraction, risk_scoring, anomaly_detection
    result: Dict[str, Any]
    model_used: str
    processing_time: float  # in seconds
    language: Optional[str] = None
    confidence_score: Optional[float] = None

class ExtractedClause(BaseModel):
    clause_type: str  # confidentiality, termination, penalties, jurisdiction, obligations
    text: str
    start_index: int
    end_index: int
    confidence: float

class RiskScore(BaseModel):
    score: float  # 0-100
    factors: List[Dict[str, Any]]
    recommendations: List[str]

class AIQuery(TimestampModel):
    id: int
    user_id: Optional[int] = None
    query_text: str
    response_text: str
    model_used: str
    processing_time: float  # in seconds
    language: Optional[str] = None
    is_fallback: bool = False
