from typing import List, Optional, Dict, Any
from datetime import datetime
from app.modules.artur.intervention.models import ArturIntervention, InterventionType, InterventionStatus
from app.modules.artur.evaluation.models import ArturSuggestion, SuggestionStatus
from app.modules.admin.functions.models import Function
from app.modules.automation.rules_engine.models import AutomationRule
from app.modules.ai.models import AIProfile
from app.db.base import InMemoryDB

class InterventionService:
    def __init__(self):
        self.db = InMemoryDB(ArturIntervention)
        self.suggestions_db = InMemoryDB(ArturSuggestion)  # For accessing suggestions
        self.functions_db = InMemoryDB(Function)    # For accessing functions
        self.rules_db = InMemoryDB(AutomationRule)        # For accessing automation rules
        self.ai_profiles_db = InMemoryDB(AIProfile)  # For accessing AI profiles
        
    async def create_intervention(self, intervention_data: Dict[str, Any]) -> ArturIntervention:
        """Create a new intervention record"""
        intervention = ArturIntervention(**intervention_data)
        intervention.id = self.db.get_next_id(ArturIntervention)
        self.db.add(ArturIntervention, intervention)
        return intervention
        
    async def get_interventions(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        intervention_type: Optional[str] = None,
        department_id: Optional[int] = None
    ) -> List[ArturIntervention]:
        """Get interventions with optional filtering"""
        interventions = self.db.get_all(ArturIntervention)
        
        if status:
            interventions = [i for i in interventions if i.status == status]
        if intervention_type:
            interventions = [i for i in interventions if i.intervention_type == intervention_type]
        if department_id:
            interventions = [i for i in interventions if i.department_id == department_id]
            
        return interventions[skip:skip + limit]
    
    async def get_intervention_by_id(self, intervention_id: int) -> Optional[ArturIntervention]:
        """Get a specific intervention by ID"""
        return self.db.get_by_id(ArturIntervention, intervention_id)
    
    async def update_intervention_status(
        self, 
        intervention_id: int, 
        status: str,
        user_id: Optional[int] = None
    ) -> Optional[ArturIntervention]:
        """Update the status of an intervention"""
        intervention = self.db.get_by_id(ArturIntervention, intervention_id)
        if not intervention:
            return None
            
        intervention.status = status
        if status == InterventionStatus.COMPLETED:
            intervention.executed_at = datetime.utcnow()
        if user_id:
            intervention.user_id = user_id
            
        self.db.update(ArturIntervention, intervention)
        return intervention
    
    async def prepare_intervention(self, suggestion_id: int) -> Optional[ArturIntervention]:
        """Prepare an intervention based on a suggestion"""
        suggestion = self.suggestions_db.get_by_id(ArturSuggestion, suggestion_id)
        if not suggestion:
            return None
            
        state_before = {}
        state_after = {}
        intervention_type = suggestion.suggested_action.get("type", "")
        
        if intervention_type == "merge_functions":
            function_ids = suggestion.suggested_action.get("details", {}).get("function_ids", [])
            functions = [self.functions_db.get_by_id(Function, fid) for fid in function_ids]
            functions = [f for f in functions if f]  # Filter out None values
            
            if len(functions) < 2:
                return None
                
            state_before = {
                "functions": [
                    {
                        "id": f.id,
                        "name": f.name,
                        "description": f.description,
                        "input_schema": f.input_schema,
                        "output_schema": f.output_schema,
                        "department_id": f.department_id
                    } for f in functions
                ]
            }
            
            merged_name = suggestion.suggested_action.get("details", {}).get("merged_name", f"Merged Function {functions[0].name}")
            merged_description = f"Merged function combining functionality from: {', '.join([f.name for f in functions])}"
            
            state_after = {
                "merged_function": {
                    "name": merged_name,
                    "description": merged_description,
                    "input_schema": functions[0].input_schema,  # Simplified; would need proper schema merging
                    "output_schema": functions[0].output_schema,  # Simplified; would need proper schema merging
                    "department_id": functions[0].department_id,
                    "source_function_ids": [f.id for f in functions]
                }
            }
            
        elif intervention_type == "remove_function":
            function_id = suggestion.suggested_action.get("details", {}).get("function_id")
            function = self.functions_db.get_by_id(Function, function_id)
            
            if not function:
                return None
                
            state_before = {
                "functions": [{
                    "id": function.id,
                    "name": function.name,
                    "description": function.description,
                    "input_schema": function.input_schema,
                    "output_schema": function.output_schema,
                    "department_id": function.department_id
                }]
            }
            
            state_after = {
                "function_id": function_id,
                "action": {"type": "removed"}
            }
            
        elif intervention_type == "update_ai_profile":
            profile_id = suggestion.suggested_action.get("details", {}).get("profile_id")
            profile = self.ai_profiles_db.get_by_id(AIProfile, profile_id)
            
            if not profile:
                return None
                
            state_before = {
                "profiles": [{
                    "id": profile.id,
                    "name": profile.name,
                    "model": profile.model,
                    "temperature": profile.temperature,
                    "top_p": profile.top_p,
                    "department_id": profile.department_id
                }]
            }
            
            updates = suggestion.suggested_action.get("details", {}).get("updates", {})
            state_after = {
                "profile": {
                    "id": profile.id,
                    "name": profile.name,
                    "model": updates.get("model", profile.model),
                    "temperature": updates.get("temperature", profile.temperature),
                    "top_p": updates.get("top_p", profile.top_p),
                    "department_id": profile.department_id
                }
            }
        
        intervention = await self.create_intervention({
            "suggestion_id": suggestion_id,
            "intervention_type": intervention_type,
            "department_id": suggestion.department_id,
            "state_before": state_before,
            "state_after": state_after,
            "status": InterventionStatus.PENDING
        })
        
        suggestion.status = SuggestionStatus.APPROVED
        suggestion.updated_at = datetime.utcnow()
        self.suggestions_db.update(ArturSuggestion, suggestion)
        
        return intervention
    
    async def execute_intervention(self, intervention_id: int, user_id: Optional[int] = None) -> bool:
        """Execute an approved intervention"""
        intervention = self.db.get_by_id(ArturIntervention, intervention_id)
        if not intervention or intervention.status != InterventionStatus.PENDING:
            return False
            
        intervention.status = InterventionStatus.IN_PROGRESS
        self.db.update(ArturIntervention, intervention)
        
        success = False
        
        try:
            if intervention.intervention_type == InterventionType.MERGE_FUNCTIONS:
                merged_function_data = intervention.state_after.get("merged_function", {})
                if merged_function_data:
                    new_function = Function(
                        name=merged_function_data.get("name"),
                        description=merged_function_data.get("description"),
                        input_schema=merged_function_data.get("input_schema"),
                        output_schema=merged_function_data.get("output_schema"),
                        department_id=merged_function_data.get("department_id")
                    )
                    new_function.id = self.functions_db.get_next_id(Function)
                    self.functions_db.add(Function, new_function)
                    
                    for function_data in intervention.state_before.get("functions", []):
                        function_id = function_data.get("id")
                        function = self.functions_db.get_by_id(Function, function_id)
                        if function:
                            self.functions_db.delete(Function, function_id)
                    
                    success = True
                    
            elif intervention.intervention_type == InterventionType.REMOVE_ENTITY:
                function_id = intervention.state_before.get("function", {}).get("id")
                if function_id:
                    function = self.functions_db.get_by_id(Function, function_id)
                    if function:
                        self.functions_db.delete(Function, function_id)
                        success = True
                        
            elif intervention.intervention_type == InterventionType.UPDATE_AI_PROFILE:
                profile_data = intervention.state_after.get("profile", {})
                profile_id = profile_data.get("id")
                if profile_id:
                    profile = self.ai_profiles_db.get_by_id(AIProfile, profile_id)
                    if profile:
                        profile.model = profile_data.get("model", profile.model)
                        profile.temperature = profile_data.get("temperature", profile.temperature)
                        profile.top_p = profile_data.get("top_p", profile.top_p)
                        self.ai_profiles_db.update(AIProfile, profile)
                        success = True
            
            if success:
                intervention.status = InterventionStatus.COMPLETED
                intervention.executed_at = datetime.utcnow()
                intervention.user_id = user_id
            else:
                intervention.status = InterventionStatus.FAILED
                
            self.db.update(ArturIntervention, intervention)
            
            suggestion_id = intervention.suggestion_id
            suggestion = self.suggestions_db.get_by_id(ArturSuggestion, suggestion_id)
            if suggestion:
                suggestion.status = SuggestionStatus.EXECUTED if success else SuggestionStatus.PENDING
                suggestion.updated_at = datetime.utcnow()
                self.suggestions_db.update(ArturSuggestion, suggestion)
                
            return success
            
        except Exception:
            intervention.status = InterventionStatus.FAILED
            self.db.update(ArturIntervention, intervention)
            return False
    
    async def rollback_intervention(self, intervention_id: int) -> bool:
        """Rollback a completed intervention"""
        intervention = self.db.get_by_id(ArturIntervention, intervention_id)
        if not intervention or intervention.status != InterventionStatus.COMPLETED:
            return False
            
        success = False
        
        try:
            if intervention.intervention_type == InterventionType.MERGE_FUNCTIONS:
                _ = intervention.state_after.get("merged_function", {})
                
                for function_data in intervention.state_before.get("functions", []):
                    new_function = Function(
                        name=function_data.get("name"),
                        description=function_data.get("description"),
                        input_schema=function_data.get("input_schema"),
                        output_schema=function_data.get("output_schema"),
                        department_id=function_data.get("department_id")
                    )
                    new_function.id = self.functions_db.get_next_id(Function)
                    self.functions_db.add(Function, new_function)
                
                success = True
                
            elif intervention.intervention_type == InterventionType.REMOVE_ENTITY:
                function_data = intervention.state_before.get("function", {})
                if function_data:
                    new_function = Function(
                        name=function_data.get("name"),
                        description=function_data.get("description"),
                        input_schema=function_data.get("input_schema"),
                        output_schema=function_data.get("output_schema"),
                        department_id=function_data.get("department_id")
                    )
                    new_function.id = self.functions_db.get_next_id(Function)
                    self.functions_db.add(Function, new_function)
                    success = True
                    
            elif intervention.intervention_type == InterventionType.UPDATE_AI_PROFILE:
                profile_data = intervention.state_before.get("profile", {})
                profile_id = profile_data.get("id")
                if profile_id:
                    profile = self.ai_profiles_db.get_by_id(AIProfile, profile_id)
                    if profile:
                        profile.model = profile_data.get("model", profile.model)
                        profile.temperature = profile_data.get("temperature", profile.temperature)
                        profile.top_p = profile_data.get("top_p", profile.top_p)
                        self.ai_profiles_db.update(AIProfile, profile)
                        success = True
            
            if success:
                intervention.status = InterventionStatus.ROLLED_BACK
                self.db.update(ArturIntervention, intervention)
                
            return success
            
        except Exception:
            return False

intervention_service = InterventionService()
