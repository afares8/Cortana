import pytest
from unittest.mock import patch, MagicMock
from app.modules.artur.observation.models import ArturInsight, InsightCategory, EntityType
from app.modules.artur.evaluation.models import ArturSuggestion, SuggestionStatus, SuggestionSource
from app.modules.artur.intervention.models import ArturIntervention, InterventionStatus, InterventionType
from app.modules.artur.simulation.models import ArturSimulation, SimulationStatus, SimulationResult
from datetime import datetime

class MockDB:
    def get_next_id(self, *args):
        return 1
    
    def add(self, *args, **kwargs):
        pass

@pytest.fixture
def observation_service():
    mock_service = MagicMock()
    mock_service.db = MockDB()
    mock_service.create_insight.side_effect = lambda data: ArturInsight(id=1, **data)
    return mock_service

@pytest.fixture
def evaluation_service():
    mock_service = MagicMock()
    mock_service.db = MockDB()
    mock_service.create_suggestion.side_effect = lambda data: ArturSuggestion(id=1, **data)
    return mock_service

@pytest.fixture
def intervention_service():
    mock_service = MagicMock()
    mock_service.db = MockDB()
    mock_service.create_intervention.side_effect = lambda data: ArturIntervention(id=1, **data)
    return mock_service

@pytest.fixture
def simulation_service():
    mock_service = MagicMock()
    mock_service.db = MockDB()
    mock_service.create_simulation.side_effect = lambda data: ArturSimulation(id=1, **data)
    return mock_service

def test_observation_service_create_insight(observation_service):
    """Test creating an insight with ObservationService"""
    insight_data = {
        "category": InsightCategory.FUNCTION_USAGE,
        "entity_type": EntityType.FUNCTION,
        "entity_id": 1,
        "department_id": 2,
        "metrics": {"total_executions": 100, "error_rate": 0.05},
        "context": {"period_days": 30}
    }
    
    insight = observation_service.create_insight(insight_data)
    
    assert insight.id == 1
    assert insight.category == InsightCategory.FUNCTION_USAGE
    assert insight.entity_type == EntityType.FUNCTION
    assert insight.metrics["total_executions"] == 100

def test_evaluation_service_create_suggestion(evaluation_service):
    """Test creating a suggestion with EvaluationService"""
    suggestion_data = {
        "department_id": 1,
        "issue_summary": "High error rate in function",
        "suggested_action": {"type": "review_function", "details": {"function_id": 123}},
        "confidence_score": 0.85,
        "source": SuggestionSource.FUNCTION_USAGE,
        "status": SuggestionStatus.PENDING
    }
    
    suggestion = evaluation_service.create_suggestion(suggestion_data)
    
    assert suggestion.id == 1
    assert suggestion.department_id == 1
    assert suggestion.issue_summary == "High error rate in function"
    assert suggestion.confidence_score == 0.85

def test_intervention_service_create_intervention(intervention_service):
    """Test creating an intervention with InterventionService"""
    intervention_data = {
        "suggestion_id": 1,
        "intervention_type": InterventionType.MERGE_FUNCTIONS,
        "state_before": {"functions": [{"id": 1}, {"id": 2}]},
        "state_after": {"merged_function": {"id": 3}},
        "status": InterventionStatus.PENDING
    }
    
    intervention = intervention_service.create_intervention(intervention_data)
    
    assert intervention.id == 1
    assert intervention.suggestion_id == 1
    assert intervention.intervention_type == InterventionType.MERGE_FUNCTIONS
    assert intervention.status == InterventionStatus.PENDING

def test_simulation_service_create_simulation(simulation_service):
    """Test creating a simulation with SimulationService"""
    simulation_data = {
        "suggestion_id": 1,
        "simulation_parameters": {"action_type": "merge_functions", "function_ids": [1, 2]},
        "expected_outcomes": {"reduced_complexity": "Reduced number of functions"},
        "dependencies": [{"entity_id": 1, "entity_type": "function"}],
        "status": SimulationStatus.PENDING
    }
    
    simulation = simulation_service.create_simulation(simulation_data)
    
    assert simulation.id == 1
    assert simulation.suggestion_id == 1
    assert simulation.simulation_parameters["action_type"] == "merge_functions"
    assert simulation.status == SimulationStatus.PENDING
