from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class EntityBase(BaseModel):
    name: str
    dob: Optional[date] = None
    country: str
    type: str  # "natural" or "legal"

class CustomerVerifyBase(BaseModel):
    customer: EntityBase
    directors: Optional[List[EntityBase]] = []
    ubos: Optional[List[EntityBase]] = []  # Ultimate Beneficial Owners

class CustomerVerifyRequest(CustomerVerifyBase):
    pass

class VerificationMatch(BaseModel):
    source: str
    source_id: str
    name: str
    match_type: str  # "exact", "partial", "alias"
    score: float
    details: Dict[str, Any]

class VerificationResult(BaseModel):
    status: str  # "clear", "watchlist", "matched"
    matches: List[VerificationMatch] = []
    source: str
    timestamp: datetime = datetime.utcnow()

class CustomerVerificationResponse(BaseModel):
    pep: VerificationResult
    ofac: VerificationResult
    un: VerificationResult
    eu: VerificationResult
    uk: Optional[VerificationResult] = None
    local: Optional[VerificationResult] = None
    wikidata: Optional[VerificationResult] = None
    enriched_data: Dict[str, Any] = {}
    verification_id: str
    created_at: datetime = datetime.utcnow()
