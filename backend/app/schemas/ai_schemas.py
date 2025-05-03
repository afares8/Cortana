from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ExtractedClauseBase(BaseModel):
    """Base schema for extracted clauses."""
    contract_id: int
    clause_type: str
    clause_text: str
    start_position: int
    end_position: int
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedClauseCreate(ExtractedClauseBase):
    """Schema for creating extracted clauses."""
    pass


class ExtractedClauseUpdate(BaseModel):
    """Schema for updating extracted clauses."""
    clause_type: Optional[str] = None
    clause_text: Optional[str] = None
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ExtractedClause(ExtractedClauseBase):
    """Schema for returning extracted clauses."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RiskScoreBase(BaseModel):
    """Base schema for risk scores."""
    contract_id: int
    overall_score: float
    missing_clauses: List[str] = Field(default_factory=list)
    abnormal_durations: bool = False
    red_flag_terms: List[Dict[str, Any]] = Field(default_factory=list)
    risk_factors: Dict[str, float] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)


class RiskScoreCreate(RiskScoreBase):
    """Schema for creating risk scores."""
    pass


class RiskScoreUpdate(BaseModel):
    """Schema for updating risk scores."""
    overall_score: Optional[float] = None
    missing_clauses: Optional[List[str]] = None
    abnormal_durations: Optional[bool] = None
    red_flag_terms: Optional[List[Dict[str, Any]]] = None
    risk_factors: Optional[Dict[str, float]] = None
    last_updated: Optional[datetime] = None


class RiskScore(RiskScoreBase):
    """Schema for returning risk scores."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComplianceCheckBase(BaseModel):
    """Base schema for compliance checks."""
    contract_id: int
    check_type: str
    is_compliant: bool
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    last_checked: datetime = Field(default_factory=datetime.now)


class ComplianceCheckCreate(ComplianceCheckBase):
    """Schema for creating compliance checks."""
    pass


class ComplianceCheckUpdate(BaseModel):
    """Schema for updating compliance checks."""
    check_type: Optional[str] = None
    is_compliant: Optional[bool] = None
    issues: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    last_checked: Optional[datetime] = None


class ComplianceCheck(ComplianceCheckBase):
    """Schema for returning compliance checks."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditLogBase(BaseModel):
    """Base schema for audit logs."""
    contract_id: int
    user_id: Optional[int] = None
    action_type: str
    action_details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit logs."""
    pass


class AuditLog(AuditLogBase):
    """Schema for returning audit logs."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIQueryBase(BaseModel):
    """Base schema for AI queries."""
    query_text: str
    response_text: str
    related_contract_ids: List[int] = Field(default_factory=list)
    query_vector: Optional[List[float]] = None
    is_fallback: bool = False


class AIQueryCreate(AIQueryBase):
    """Schema for creating AI queries."""
    pass


class AIQuery(AIQueryBase):
    """Schema for returning AI queries."""
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContractAnomalyBase(BaseModel):
    """Base schema for contract anomalies."""
    contract_id: int
    anomaly_type: str
    description: str
    severity: str
    detected_at: datetime = Field(default_factory=datetime.now)


class ContractAnomalyCreate(ContractAnomalyBase):
    """Schema for creating contract anomalies."""
    pass


class ContractAnomaly(ContractAnomalyBase):
    """Schema for returning contract anomalies."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClauseExtractionRequest(BaseModel):
    """Schema for requesting clause extraction."""
    contract_id: int
    file_path: Optional[str] = None
    text_content: Optional[str] = None


class NaturalLanguageQueryRequest(BaseModel):
    """Schema for natural language queries."""
    query: str
    filters: Optional[Dict[str, Any]] = None
