from datetime import date, datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.models.base import TimestampModel
from app.models.contract import Contract


class ExtractedClause(TimestampModel):
    """Model for storing extracted clauses from contracts."""
    id: Optional[int] = None
    contract_id: int
    clause_type: str  # confidentiality, termination, penalties, jurisdiction, obligations, etc.
    clause_text: str
    start_position: int
    end_position: int
    confidence_score: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskScore(TimestampModel):
    """Model for storing risk assessment of contracts."""
    id: Optional[int] = None
    contract_id: int
    overall_score: float  # 0.0 to 1.0, higher means more risky
    missing_clauses: List[str] = Field(default_factory=list)
    abnormal_durations: bool = False
    red_flag_terms: List[Dict[str, Any]] = Field(default_factory=list)
    risk_factors: Dict[str, float] = Field(default_factory=dict)  # Individual risk factor scores
    last_updated: datetime = Field(default_factory=datetime.now)


class ComplianceCheck(TimestampModel):
    """Model for storing compliance checks for contracts."""
    id: Optional[int] = None
    contract_id: int
    check_type: str  # jurisdiction, data_policy, regulatory, etc.
    is_compliant: bool
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    last_checked: datetime = Field(default_factory=datetime.now)


class AuditLog(TimestampModel):
    """Model for storing audit logs for contract actions."""
    id: Optional[int] = None
    contract_id: int
    user_id: Optional[int] = None
    action_type: str  # view, edit, approve, terminate, etc.
    action_details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class AIQuery(TimestampModel):
    """Model for storing natural language queries and responses."""
    id: Optional[int] = None
    query_text: str
    response_text: str
    related_contract_ids: List[int] = Field(default_factory=list)
    query_vector: Optional[List[float]] = None  # For semantic search
    timestamp: datetime = Field(default_factory=datetime.now)


class ContractAnomaly(TimestampModel):
    """Model for storing detected anomalies in contracts."""
    id: Optional[int] = None
    contract_id: int
    anomaly_type: str  # policy_deviation, template_deviation, etc.
    description: str
    severity: str  # low, medium, high
    detected_at: datetime = Field(default_factory=datetime.now)
