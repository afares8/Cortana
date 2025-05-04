from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ComplianceReportBase(BaseModel):
    report_type: str  # uaf_report, pep_screening, sanctions_screening
    entity_type: str  # client, provider
    entity_id: int
    report_data: Dict[str, Any]
    status: str = "draft"  # draft, submitted, approved, rejected
    submitted_by: Optional[int] = None  # user_id
    submitted_at: Optional[datetime] = None
    approved_by: Optional[int] = None  # user_id
    approved_at: Optional[datetime] = None
    notes: Optional[str] = None

class ComplianceReportCreate(ComplianceReportBase):
    pass

class ComplianceReportUpdate(BaseModel):
    report_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    submitted_by: Optional[int] = None
    submitted_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    notes: Optional[str] = None

class ComplianceReportInDBBase(ComplianceReportBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ComplianceReport(ComplianceReportInDBBase):
    pass

class PEPScreeningResultBase(BaseModel):
    client_id: int
    match_status: str  # no_match, potential_match, confirmed_match
    match_details: Optional[Dict[str, Any]] = None
    screened_by: Optional[int] = None  # user_id
    screened_at: datetime = datetime.utcnow()
    risk_level: str  # low, medium, high
    notes: Optional[str] = None

class PEPScreeningResultCreate(PEPScreeningResultBase):
    pass

class PEPScreeningResultUpdate(BaseModel):
    match_status: Optional[str] = None
    match_details: Optional[Dict[str, Any]] = None
    screened_by: Optional[int] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None

class PEPScreeningResultInDBBase(PEPScreeningResultBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PEPScreeningResult(PEPScreeningResultInDBBase):
    pass

class SanctionsScreeningResultBase(BaseModel):
    client_id: int
    match_status: str  # no_match, potential_match, confirmed_match
    match_details: Optional[Dict[str, Any]] = None
    screened_by: Optional[int] = None  # user_id
    screened_at: datetime = datetime.utcnow()
    risk_level: str  # low, medium, high
    notes: Optional[str] = None

class SanctionsScreeningResultCreate(SanctionsScreeningResultBase):
    pass

class SanctionsScreeningResultUpdate(BaseModel):
    match_status: Optional[str] = None
    match_details: Optional[Dict[str, Any]] = None
    screened_by: Optional[int] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None

class SanctionsScreeningResultInDBBase(SanctionsScreeningResultBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SanctionsScreeningResult(SanctionsScreeningResultInDBBase):
    pass

class DocumentRetentionPolicyBase(BaseModel):
    document_type: str
    retention_period_days: int
    legal_basis: str
    is_active: bool = True
    created_by: Optional[int] = None  # user_id

class DocumentRetentionPolicyCreate(DocumentRetentionPolicyBase):
    pass

class DocumentRetentionPolicyUpdate(BaseModel):
    retention_period_days: Optional[int] = None
    legal_basis: Optional[str] = None
    is_active: Optional[bool] = None

class DocumentRetentionPolicyInDBBase(DocumentRetentionPolicyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentRetentionPolicy(DocumentRetentionPolicyInDBBase):
    pass
