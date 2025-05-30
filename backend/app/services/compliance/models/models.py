from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field

class EntityType(str, Enum):
    NATURAL = "natural"
    LEGAL = "legal"

class Entity(BaseModel):
    name: str
    country: str
    type: EntityType
    dob: Optional[str] = None
    id_number: Optional[Union[int, str]] = None
    nationality: Optional[str] = None
    activity: Optional[str] = None
    incorporation_date: Optional[str] = None
    role: Optional[str] = None

class CustomerVerifyRequest(BaseModel):
    customer: Entity
    directors: Optional[List[Entity]] = []
    ubos: Optional[List[Entity]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "customer": {
                    "name": "Juan Perez",
                    "dob": "1970-01-01",
                    "country": "PA",
                    "type": "natural"
                },
                "directors": [],
                "ubos": []
            }
        }

class VerificationMatch(BaseModel):
    source: str
    name: str
    score: float
    details: Dict[str, Any]

class EntityVerificationResult(BaseModel):
    name: str
    enriched_data: Dict[str, Any]
    pep_matches: List[VerificationMatch]
    sanctions_matches: List[VerificationMatch]
    risk_score: float

class CustomerVerificationResponse(BaseModel):
    customer: EntityVerificationResult
    directors: Optional[List[EntityVerificationResult]] = []
    ubos: Optional[List[EntityVerificationResult]] = []
    country_risk: Dict[str, Any]
    report: Dict[str, Any]
    sources_checked: List[str]

class ComplianceReport(BaseModel):
    id: Optional[int] = None
    client_name: str
    client_id: str
    report_type: str
    report_path: str
    country: str
    risk_level: str
    created_at: datetime
    updated_at: datetime

class PEPScreeningResult(BaseModel):
    id: Optional[int] = None
    client_name: str
    client_id: str
    match_name: str
    match_score: float
    match_details: str
    report_id: int
    created_at: datetime

class SanctionsScreeningResult(BaseModel):
    id: Optional[int] = None
    client_name: str
    client_id: str
    match_name: str
    match_score: float
    match_details: str
    list_name: str
    report_id: int
    created_at: datetime

class ListUpdate(BaseModel):
    id: Optional[int] = None
    list_name: str
    update_date: datetime
    status: str
    details: Optional[str] = None
