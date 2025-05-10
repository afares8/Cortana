from app.modules.artur.observation.models import ArturInsight, InsightCategory, EntityType
from app.modules.artur.evaluation.models import ArturSuggestion, SuggestionStatus, SuggestionSource
from app.modules.artur.intervention.models import ArturIntervention, InterventionStatus, InterventionType
from app.modules.artur.simulation.models import ArturSimulation, SimulationStatus, SimulationResult

def test_artur_insight_model():
    """Test ArturInsight model initialization"""
    insight = ArturInsight(
        category=InsightCategory.FUNCTION_USAGE,
        entity_type=EntityType.FUNCTION,
        entity_id=1,
        department_id=2,
        metrics={"total_executions": 100, "error_rate": 0.05},
        context={"period_days": 30}
    )
    
    assert insight.category == InsightCategory.FUNCTION_USAGE
    assert insight.entity_type == EntityType.FUNCTION
    assert insight.entity_id == 1
    assert insight.department_id == 2
    assert insight.metrics["total_executions"] == 100
    assert insight.metrics["error_rate"] == 0.05
    assert insight.context["period_days"] == 30

def test_artur_suggestion_model():
    """Test ArturSuggestion model initialization"""
    suggestion = ArturSuggestion(
        department_id=1,
        issue_summary="High error rate in function",
        suggested_action={"type": "review_function", "details": {"function_id": 123}},
        confidence_score=0.85,
        source=SuggestionSource.FUNCTION_USAGE,
        status=SuggestionStatus.PENDING
    )
    
    assert suggestion.department_id == 1
    assert suggestion.issue_summary == "High error rate in function"
    assert suggestion.suggested_action["type"] == "review_function"
    assert suggestion.confidence_score == 0.85
    assert suggestion.source == SuggestionSource.FUNCTION_USAGE
    assert suggestion.status == SuggestionStatus.PENDING

def test_artur_intervention_model():
    """Test ArturIntervention model initialization"""
    intervention = ArturIntervention(
        suggestion_id=1,
        intervention_type=InterventionType.MERGE_FUNCTIONS,
        state_before={"functions": [{"id": 1}, {"id": 2}]},
        state_after={"merged_function": {"id": 3}},
        status=InterventionStatus.PENDING
    )
    
    assert intervention.suggestion_id == 1
    assert intervention.intervention_type == InterventionType.MERGE_FUNCTIONS
    assert len(intervention.state_before["functions"]) == 2
    assert intervention.state_after["merged_function"]["id"] == 3
    assert intervention.status == InterventionStatus.PENDING

def test_artur_simulation_model():
    """Test ArturSimulation model initialization"""
    simulation = ArturSimulation(
        suggestion_id=1,
        simulation_parameters={"action_type": "merge_functions", "function_ids": [1, 2]},
        expected_outcomes={"reduced_complexity": "Reduced number of functions"},
        dependencies=[{"entity_id": 1, "entity_type": "function"}],
        status=SimulationStatus.PENDING
    )
    
    assert simulation.suggestion_id == 1
    assert simulation.simulation_parameters["action_type"] == "merge_functions"
    assert len(simulation.simulation_parameters["function_ids"]) == 2
    assert "reduced_complexity" in simulation.expected_outcomes
    assert len(simulation.dependencies) == 1
    assert simulation.status == SimulationStatus.PENDING
