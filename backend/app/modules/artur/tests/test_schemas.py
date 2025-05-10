from pydantic import ValidationError
from app.modules.artur.observation.schemas import ArturInsightBase, ArturInsightCreate, ArturInsightOut
from app.modules.artur.evaluation.schemas import ArturSuggestionBase, ArturSuggestionCreate, ArturSuggestionOut
from app.modules.artur.intervention.schemas import ArturInterventionBase, ArturInterventionCreate, ArturInterventionOut
from app.modules.artur.simulation.schemas import ArturSimulationBase, ArturSimulationCreate, ArturSimulationOut
from datetime import datetime

def test_artur_insight_schema():
    """Test ArturInsight schemas validation"""
    data = {
        "category": "function_usage",
        "entity_type": "function",
        "entity_id": 1,
        "department_id": 2,
        "metrics": {"total_executions": 100, "error_rate": 0.05},
        "context": {"period_days": 30}
    }
    
    insight_base = ArturInsightBase(**data)
    assert insight_base.category == "function_usage"
    assert insight_base.entity_type == "function"
    assert insight_base.metrics["total_executions"] == 100
    
    insight_create = ArturInsightCreate(**data)
    assert insight_create.category == "function_usage"
    
    out_data = data.copy()
    out_data.update({
        "id": 1,
        "created_at": datetime.utcnow()
    })
    
    insight_out = ArturInsightOut(**out_data)
    assert insight_out.id == 1
    assert isinstance(insight_out.created_at, datetime)

def test_artur_suggestion_schema():
    """Test ArturSuggestion schemas validation"""
    data = {
        "department_id": 1,
        "issue_summary": "High error rate in function",
        "suggested_action": {"type": "review_function", "details": {"function_id": 123}},
        "confidence_score": 0.85,
        "source": "function_usage",
        "status": "pending"
    }
    
    suggestion_base = ArturSuggestionBase(**data)
    assert suggestion_base.department_id == 1
    assert suggestion_base.issue_summary == "High error rate in function"
    assert suggestion_base.confidence_score == 0.85
    
    suggestion_create = ArturSuggestionCreate(**data)
    assert suggestion_create.source == "function_usage"
    assert suggestion_create.status == "pending"
    
    out_data = data.copy()
    out_data.update({
        "id": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    suggestion_out = ArturSuggestionOut(**out_data)
    assert suggestion_out.id == 1
    assert isinstance(suggestion_out.created_at, datetime)
    assert isinstance(suggestion_out.updated_at, datetime)

def test_artur_intervention_schema():
    """Test ArturIntervention schemas validation"""
    data = {
        "suggestion_id": 1,
        "intervention_type": "merge_functions",
        "state_before": {"functions": [{"id": 1}, {"id": 2}]},
        "state_after": {"merged_function": {"id": 3}},
        "status": "pending"
    }
    
    intervention_base = ArturInterventionBase(**data)
    assert intervention_base.suggestion_id == 1
    assert intervention_base.intervention_type == "merge_functions"
    assert len(intervention_base.state_before["functions"]) == 2
    
    intervention_create = ArturInterventionCreate(**data)
    assert intervention_create.status == "pending"
    
    out_data = data.copy()
    out_data.update({
        "id": 1,
        "created_at": datetime.utcnow(),
        "executed_at": None,
        "rolled_back_at": None
    })
    
    intervention_out = ArturInterventionOut(**out_data)
    assert intervention_out.id == 1
    assert isinstance(intervention_out.created_at, datetime)
    assert intervention_out.executed_at is None
    assert intervention_out.rolled_back_at is None

def test_artur_simulation_schema():
    """Test ArturSimulation schemas validation"""
    data = {
        "suggestion_id": 1,
        "simulation_parameters": {"action_type": "merge_functions", "function_ids": [1, 2]},
        "expected_outcomes": {"reduced_complexity": "Reduced number of functions"},
        "dependencies": [{"entity_id": 1, "entity_type": "function"}],
        "status": "pending"
    }
    
    simulation_base = ArturSimulationBase(**data)
    assert simulation_base.suggestion_id == 1
    assert simulation_base.simulation_parameters["action_type"] == "merge_functions"
    assert len(simulation_base.dependencies) == 1
    
    simulation_create = ArturSimulationCreate(**data)
    assert simulation_create.status == "pending"
    
    out_data = data.copy()
    out_data.update({
        "id": 1,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "actual_outcomes": {},
        "result": "neutral"
    })
    
    simulation_out = ArturSimulationOut(**out_data)
    assert simulation_out.id == 1
    assert isinstance(simulation_out.created_at, datetime)
    assert simulation_out.completed_at is None
    assert simulation_out.result == "neutral"
