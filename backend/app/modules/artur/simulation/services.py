from typing import List, Optional, Dict, Any
from datetime import datetime
from app.modules.artur.simulation.models import ArturSimulation, SimulationStatus, SimulationResult
from app.modules.artur.evaluation.models import ArturSuggestion, SuggestionStatus
from app.modules.admin.functions.models import Function
from app.modules.automation.rules_engine.models import AutomationRule
from app.modules.ai.models import AIProfile
from app.modules.admin.roles.models import Role
from app.db.base import InMemoryDB

class SimulationService:
    def __init__(self):
        self.db = InMemoryDB(ArturSimulation)
        self.suggestions_db = InMemoryDB(ArturSuggestion)  # For accessing suggestions
        self.functions_db = InMemoryDB(Function)    # For accessing functions
        self.rules_db = InMemoryDB(AutomationRule)        # For accessing automation rules
        self.ai_profiles_db = InMemoryDB(AIProfile)  # For accessing AI profiles
        self.roles_db = InMemoryDB(Role)        # For accessing roles
        
    async def create_simulation(self, simulation_data: Dict[str, Any]) -> ArturSimulation:
        """Create a new simulation record"""
        simulation = ArturSimulation(**simulation_data)
        simulation.id = self.db.get_next_id(ArturSimulation)
        self.db.add(ArturSimulation, simulation)
        return simulation
        
    async def get_simulations(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        result: Optional[str] = None,
        suggestion_id: Optional[int] = None
    ) -> List[ArturSimulation]:
        """Get simulations with optional filtering"""
        simulations = self.db.get_multi()
        
        if status:
            simulations = [s for s in simulations if s.status == status]
        if result:
            simulations = [s for s in simulations if s.result == result]
        if suggestion_id:
            simulations = [s for s in simulations if s.suggestion_id == suggestion_id]
            
        return simulations[skip:skip + limit]
    
    async def get_simulation_by_id(self, simulation_id: int) -> Optional[ArturSimulation]:
        """Get a specific simulation by ID"""
        return self.db.get_by_id(ArturSimulation, simulation_id)
    
    async def update_simulation(
        self, 
        simulation_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[ArturSimulation]:
        """Update a simulation"""
        simulation = self.db.get_by_id(ArturSimulation, simulation_id)
        if not simulation:
            return None
            
        for key, value in update_data.items():
            if hasattr(simulation, key):
                setattr(simulation, key, value)
                
        self.db.update(ArturSimulation, simulation)
        return simulation
    
    async def prepare_simulation(self, suggestion_id: int) -> Optional[ArturSimulation]:
        """Prepare a simulation based on a suggestion"""
        suggestion = self.suggestions_db.get_by_id(ArturSuggestion, suggestion_id)
        if not suggestion:
            return None
            
        simulation_parameters = {}
        expected_outcomes = {}
        dependencies = []
        
        action_type = suggestion.suggested_action.get("type", "")
        
        if action_type == "merge_functions":
            function_ids = suggestion.suggested_action.get("details", {}).get("function_ids", [])
            
            for function_id in function_ids:
                function = self.functions_db.get_by_id(Function, function_id)
                if function:
                    rules = self.rules_db.get_multi()
                    dependent_rules = []
                    
                    for rule in rules:
                        for action in rule.actions:
                            if (action.get("type") == "run_function" and 
                                action.get("function_id") == function_id):
                                dependent_rules.append({
                                    "id": rule.id,
                                    "name": rule.name,
                                    "type": "automation_rule"
                                })
                    
                    dependencies.append({
                        "entity_id": function_id,
                        "entity_type": "function",
                        "name": function.name,
                        "dependents": dependent_rules
                    })
            
            simulation_parameters = {
                "action_type": "merge_functions",
                "function_ids": function_ids,
                "merged_name": suggestion.suggested_action.get("details", {}).get("merged_name", "Merged Function")
            }
            
            expected_outcomes = {
                "reduced_complexity": "Reduced number of functions by merging similar ones",
                "improved_maintenance": "Easier to maintain a single function instead of multiple similar ones",
                "potential_risks": "Rules using these functions will need to be updated"
            }
            
        elif action_type == "remove_function":
            function_id = suggestion.suggested_action.get("details", {}).get("function_id")
            function = self.functions_db.get_by_id(Function, function_id)
            
            if function:
                rules = self.rules_db.get_all(AutomationRule)
                dependent_rules = []
                
                for rule in rules:
                    for action in rule.actions:
                        if (action.get("type") == "run_function" and 
                            action.get("function_id") == function_id):
                            dependent_rules.append({
                                "id": rule.id,
                                "name": rule.name,
                                "type": "automation_rule"
                            })
                
                dependencies.append({
                    "entity_id": function_id,
                    "entity_type": "function",
                    "name": function.name,
                    "dependents": dependent_rules
                })
            
            simulation_parameters = {
                "action_type": "remove_function",
                "function_id": function_id
            }
            
            expected_outcomes = {
                "reduced_complexity": "Removed unused function to simplify system",
                "potential_risks": f"Any rules using function {function_id} will break"
            }
            
        elif action_type == "update_ai_profile":
            profile_id = suggestion.suggested_action.get("details", {}).get("profile_id")
            profile = self.ai_profiles_db.get_by_id(AIProfile, profile_id)
            
            if profile:
                departments_using_profile: List[Dict[str, Any]] = []  # This would need proper implementation
                
                dependencies.append({
                    "entity_id": profile_id,
                    "entity_type": "ai_profile",
                    "name": profile.name,
                    "dependents": departments_using_profile
                })
            
            updates = suggestion.suggested_action.get("details", {}).get("updates", {})
            simulation_parameters = {
                "action_type": "update_ai_profile",
                "profile_id": profile_id,
                "updates": updates
            }
            
            expected_outcomes = {
                "improved_performance": "Optimized AI parameters for better results",
                "potential_risks": "Changed behavior might affect existing AI interactions"
            }
        
        simulation = await self.create_simulation({
            "suggestion_id": suggestion_id,
            "simulation_parameters": simulation_parameters,
            "expected_outcomes": expected_outcomes,
            "dependencies": dependencies,
            "status": SimulationStatus.PENDING
        })
        
        suggestion.status = SuggestionStatus.SIMULATED
        suggestion.updated_at = datetime.utcnow()
        self.suggestions_db.update(ArturSuggestion, suggestion)
        
        return simulation
    
    async def run_simulation(self, simulation_id: int) -> bool:
        """Run a prepared simulation"""
        simulation = self.db.get_by_id(ArturSimulation, simulation_id)
        if not simulation or simulation.status != SimulationStatus.PENDING:
            return False
            
        simulation.status = SimulationStatus.RUNNING
        self.db.update(ArturSimulation, simulation)
        
        try:
            action_type = simulation.simulation_parameters.get("action_type")
            actual_outcomes = {}
            result = SimulationResult.NEUTRAL
            
            if action_type == "merge_functions":
                function_ids = simulation.simulation_parameters.get("function_ids", [])
                
                breaking_rules = []
                for dependency in simulation.dependencies:
                    if dependency.get("entity_type") == "function":
                        for dependent in dependency.get("dependents", []):
                            if dependent.get("type") == "automation_rule":
                                breaking_rules.append(dependent)
                
                if breaking_rules:
                    actual_outcomes = {
                        "breaking_changes": f"Would break {len(breaking_rules)} automation rules",
                        "affected_rules": breaking_rules,
                        "recommendation": "Update affected rules before merging functions"
                    }
                    result = SimulationResult.NOT_RECOMMENDED
                else:
                    actual_outcomes = {
                        "complexity_reduction": f"Would reduce function count by {len(function_ids) - 1}",
                        "breaking_changes": "No breaking changes detected",
                        "recommendation": "Safe to proceed with function merge"
                    }
                    result = SimulationResult.RECOMMENDED
                    
            elif action_type == "remove_function":
                breaking_rules = []
                for dependency in simulation.dependencies:
                    if dependency.get("entity_type") == "function":
                        for dependent in dependency.get("dependents", []):
                            if dependent.get("type") == "automation_rule":
                                breaking_rules.append(dependent)
                
                if breaking_rules:
                    actual_outcomes = {
                        "breaking_changes": f"Would break {len(breaking_rules)} automation rules",
                        "affected_rules": breaking_rules,
                        "recommendation": "Update or remove affected rules before removing function"
                    }
                    result = SimulationResult.NOT_RECOMMENDED
                else:
                    actual_outcomes = {
                        "complexity_reduction": "Would remove unused function",
                        "breaking_changes": "No breaking changes detected",
                        "recommendation": "Safe to proceed with function removal"
                    }
                    result = SimulationResult.RECOMMENDED
                    
            elif action_type == "update_ai_profile":
                updates = simulation.simulation_parameters.get("updates", {})
                
                if updates.get("temperature", 0) > 0.9:
                    actual_outcomes = {
                        "performance_impact": "High temperature may lead to unpredictable responses",
                        "recommendation": "Consider using a lower temperature value"
                    }
                    result = SimulationResult.NEUTRAL
                else:
                    actual_outcomes = {
                        "performance_impact": "Changes should improve AI response quality",
                        "recommendation": "Safe to proceed with AI profile update"
                    }
                    result = SimulationResult.RECOMMENDED
            
            simulation.status = SimulationStatus.COMPLETED
            simulation.result = result
            simulation.actual_outcomes = actual_outcomes
            simulation.completed_at = datetime.utcnow()
            self.db.update(ArturSimulation, simulation)
            
            return True
            
        except Exception:
            simulation.status = SimulationStatus.FAILED
            self.db.update(ArturSimulation, simulation)
            return False
    
    async def simulate_intervention(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate an intervention before execution.
        
        This endpoint allows for safe preview (sandbox) of system changes suggested by Artur.
        """
        action_type = simulation_data.get("action_type", "")
        details = simulation_data.get("details", {})
        dependencies_affected = []
        impact_assessment = {}
        recommendation = ""
        success = True
        result = SimulationResult.NEUTRAL
        
        try:
            if action_type == "merge_functions":
                function_ids = details.get("function_ids", [])
                
                breaking_rules = []
                for function_id in function_ids:
                    function = self.functions_db.get_by_id(Function, function_id)
                    if function:
                        rules = self.rules_db.get_multi()
                        for rule in rules:
                            for action in rule.actions:
                                if (action.get("type") == "run_function" and 
                                    action.get("function_id") == function_id):
                                    breaking_rules.append({
                                        "id": rule.id,
                                        "name": rule.name,
                                        "type": "automation_rule"
                                    })
                        
                        dependencies_affected.append({
                            "entity_id": function_id,
                            "entity_type": "function",
                            "name": function.name,
                            "impact": "Will be merged"
                        })
                
                if breaking_rules:
                    impact_assessment = {
                        "breaking_changes": f"Would break {len(breaking_rules)} automation rules",
                        "affected_rules": breaking_rules,
                        "complexity_reduction": f"Would reduce function count by {len(function_ids) - 1}"
                    }
                    recommendation = "Update affected rules before merging functions"
                    result = SimulationResult.NOT_RECOMMENDED
                else:
                    impact_assessment = {
                        "complexity_reduction": f"Would reduce function count by {len(function_ids) - 1}",
                        "breaking_changes": "No breaking changes detected"
                    }
                    recommendation = "Safe to proceed with function merge"
                    result = SimulationResult.RECOMMENDED
                    
            elif action_type == "remove_function":
                function_id = details.get("function_id")
                function = self.functions_db.get_by_id(Function, function_id)
                
                if function:
                    rules = self.rules_db.get_multi()
                    breaking_rules = []
                    
                    for rule in rules:
                        for action in rule.actions:
                            if (action.get("type") == "run_function" and 
                                action.get("function_id") == function_id):
                                breaking_rules.append({
                                    "id": rule.id,
                                    "name": rule.name,
                                    "type": "automation_rule"
                                })
                    
                    dependencies_affected.append({
                        "entity_id": function_id,
                        "entity_type": "function",
                        "name": function.name,
                        "impact": "Will be removed"
                    })
                    
                    if breaking_rules:
                        impact_assessment = {
                            "breaking_changes": f"Would break {len(breaking_rules)} automation rules",
                            "affected_rules": breaking_rules
                        }
                        recommendation = "Update or remove affected rules before removing function"
                        result = SimulationResult.NOT_RECOMMENDED
                    else:
                        impact_assessment = {
                            "complexity_reduction": "Would remove unused function",
                            "breaking_changes": "No breaking changes detected"
                        }
                        recommendation = "Safe to proceed with function removal"
                        result = SimulationResult.RECOMMENDED
                
            elif action_type == "update_ai_profile":
                profile_id = details.get("profile_id")
                profile = self.ai_profiles_db.get_by_id(AIProfile, profile_id)
                updates = details.get("updates", {})
                
                if profile:
                    dependencies_affected.append({
                        "entity_id": profile_id,
                        "entity_type": "ai_profile",
                        "name": profile.name,
                        "impact": "Configuration will be updated"
                    })
                    
                    if updates.get("temperature", 0) > 0.9:
                        impact_assessment = {
                            "performance_impact": "High temperature may lead to unpredictable responses"
                        }
                        recommendation = "Consider using a lower temperature value"
                        result = SimulationResult.NEUTRAL
                    else:
                        impact_assessment = {
                            "performance_impact": "Changes should improve AI response quality"
                        }
                        recommendation = "Safe to proceed with AI profile update"
                        result = SimulationResult.RECOMMENDED
            
            return {
                "success": success,
                "result": str(result),  # Convert enum to string
                "details": details,
                "impact_assessment": impact_assessment,
                "dependencies_affected": dependencies_affected,
                "recommendation": recommendation
            }
            
        except Exception as e:
            return {
                "success": False,
                "result": "error",  # Use string instead of enum
                "details": {"error": str(e)},
                "impact_assessment": {"error": "Failed to simulate intervention"},
                "dependencies_affected": [],
                "recommendation": "Unable to provide recommendation due to simulation error"
            }

simulation_service = SimulationService()
