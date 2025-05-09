from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class DiagnosticItemBase(BaseModel):
    """Base model for a diagnostic item."""
    component: str = Field(..., description="Component being diagnosed")
    status: str = Field(..., description="Status of the component (healthy, warning, error)")
    description: str = Field(..., description="Description of the diagnostic item")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the diagnosis")

class DiagnosticItem(DiagnosticItemBase):
    """Complete model for a diagnostic item."""
    id: Optional[int] = Field(None, description="ID of the diagnostic item")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Details of the error if any")
    suggested_action: Optional[str] = Field(None, description="Suggested action to fix the issue")
    prediction: Optional[Dict[str, Any]] = Field(None, description="Prediction data if available")

class DiagnosticsRunRequest(BaseModel):
    """Request model for the diagnostics run endpoint."""
    components: Optional[List[str]] = Field(None, description="List of components to diagnose. If not provided, all components will be diagnosed.")
    include_explanations: bool = Field(True, description="Whether to include explanations for issues using Mistral AI")
    include_suggestions: bool = Field(True, description="Whether to include suggestions for fixing issues")
    include_predictions: bool = Field(False, description="Whether to include predictions for future issues")

class DiagnosticsResponse(BaseModel):
    """Response model for the diagnostics run endpoint."""
    items: List[DiagnosticItem] = Field(..., description="List of diagnostic items")
    overall_status: str = Field(..., description="Overall status of the system (healthy, warning, error)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the diagnosis")
    error: Optional[str] = Field(None, description="Error message if the diagnosis failed")
    explanation: Optional[str] = Field(None, description="Explanation of the issues using Mistral AI")

class DiagnosticsLogItem(DiagnosticItem):
    """Model for a diagnostic log item."""
    log_id: str = Field(..., description="Unique ID of the log item")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

class DiagnosticsStatsBase(BaseModel):
    """Base model for diagnostics statistics."""
    total_runs: int = Field(..., description="Total number of diagnostic runs")
    healthy_count: int = Field(..., description="Number of healthy components")
    warning_count: int = Field(..., description="Number of components with warnings")
    error_count: int = Field(..., description="Number of components with errors")
    components_checked: List[str] = Field(..., description="List of components checked")

class DiagnosticsStats(DiagnosticsStatsBase):
    """Complete model for diagnostics statistics."""
    last_run: datetime = Field(..., description="Timestamp of the last diagnostic run")
    history: Dict[str, List[Dict[str, Any]]] = Field(..., description="Historical data of component statuses")
