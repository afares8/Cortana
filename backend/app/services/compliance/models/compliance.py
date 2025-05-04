from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.models.base import TimestampModel

class ComplianceReport(TimestampModel):
    id: int
    report_type: str  # uaf_report, pep_screening, sanctions_screening
    entity_type: str  # client, provider
    entity_id: int
    report_data: Dict[str, Any]
    status: str  # draft, submitted, approved, rejected
    submitted_by: Optional[int] = None  # user_id
    submitted_at: Optional[datetime] = None
    approved_by: Optional[int] = None  # user_id
    approved_at: Optional[datetime] = None
    notes: Optional[str] = None

class PEPScreeningResult(TimestampModel):
    id: int
    client_id: int
    match_status: str  # no_match, potential_match, confirmed_match
    match_details: Optional[Dict[str, Any]] = None
    screened_by: Optional[int] = None  # user_id
    screened_at: datetime
    risk_level: str  # low, medium, high
    notes: Optional[str] = None

class SanctionsScreeningResult(TimestampModel):
    id: int
    client_id: int
    match_status: str  # no_match, potential_match, confirmed_match
    match_details: Optional[Dict[str, Any]] = None
    screened_by: Optional[int] = None  # user_id
    screened_at: datetime
    risk_level: str  # low, medium, high
    notes: Optional[str] = None

class DocumentRetentionPolicy(TimestampModel):
    id: int
    document_type: str
    retention_period_days: int
    legal_basis: str
    is_active: bool = True
    created_by: Optional[int] = None  # user_id
