from typing import List, Optional, Dict, Any
from datetime import datetime
from app.modules.artur.evaluation.models import ArturSuggestion, SuggestionSource, SuggestionStatus
from app.modules.artur.observation.models import ArturInsight, InsightCategory
from app.services.ai.mistral_client import mistral_client
from app.db.base import InMemoryDB

class EvaluationService:
    def __init__(self):
        self.db = InMemoryDB(ArturSuggestion)
        self.insights_db = InMemoryDB(ArturInsight)  # For accessing insights
        
    async def create_suggestion(self, suggestion_data: Dict[str, Any]) -> ArturSuggestion:
        """Create a new suggestion from evaluation"""
        suggestion = ArturSuggestion(**suggestion_data)
        suggestion.id = self.db.get_next_id(ArturSuggestion)
        self.db.add(ArturSuggestion, suggestion)
        return suggestion
        
    async def get_suggestions(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        source: Optional[str] = None,
        department_id: Optional[int] = None,
        min_confidence: Optional[float] = None
    ) -> List[ArturSuggestion]:
        """Get suggestions with optional filtering"""
        suggestions = self.db.get_multi()
        
        if status:
            suggestions = [s for s in suggestions if s.status == status]
        if source:
            suggestions = [s for s in suggestions if s.source == source]
        if department_id:
            suggestions = [s for s in suggestions if s.department_id == department_id]
        if min_confidence:
            suggestions = [s for s in suggestions if s.confidence_score >= min_confidence]
            
        return suggestions[skip:skip + limit]
    
    async def get_suggestion_by_id(self, suggestion_id: int) -> Optional[ArturSuggestion]:
        """Get a specific suggestion by ID"""
        return self.db.get_by_id(ArturSuggestion, suggestion_id)
    
    async def update_suggestion_status(self, suggestion_id: int, status: str) -> Optional[ArturSuggestion]:
        """Update the status of a suggestion"""
        suggestion = self.db.get_by_id(ArturSuggestion, suggestion_id)
        if not suggestion:
            return None
            
        suggestion.status = status
        suggestion.updated_at = datetime.utcnow()
        self.db.update(ArturSuggestion, suggestion)
        return suggestion
    
    async def evaluate_function_usage_insights(self) -> List[ArturSuggestion]:
        """Evaluate function usage insights and generate suggestions"""
        insights = self.insights_db.get_multi()
        function_insights = [
            i for i in insights 
            if i.category in [InsightCategory.FUNCTION_USAGE, InsightCategory.INACTIVE_ENTITY]
        ]
        
        suggestions = []
        for insight in function_insights:
            if (insight.category == InsightCategory.FUNCTION_USAGE and 
                insight.metrics.get("error_rate", 0) > 0.3):
                
                prompt = f"""
                Function ID {insight.entity_id} in Department ID {insight.department_id} 
                has a high error rate of {insight.metrics.get('error_rate')}. 
                The function has been executed {insight.metrics.get('total_executions')} times 
                in the last {insight.context.get('period_days')} days.
                
                Suggest an action to improve this situation. Format your response as a JSON object with:
                1. issue_summary: A concise description of the problem
                2. suggested_action: An object with 'type' and 'details' fields
                3. confidence_score: A number between 0 and 1 indicating confidence
                """
                
                ai_response = await mistral_client.generate(prompt)
                
                try:
                    import json
                    suggestion_data = ai_response if isinstance(ai_response, dict) else json.loads(ai_response)
                    
                    suggestion = await self.create_suggestion({
                        "department_id": insight.department_id,
                        "issue_summary": suggestion_data.get("issue_summary", "Function has high error rate"),
                        "suggested_action": suggestion_data.get("suggested_action", {}),
                        "confidence_score": suggestion_data.get("confidence_score", 0.7),
                        "source": SuggestionSource.FUNCTION_USAGE,
                        "status": SuggestionStatus.PENDING
                    })
                    suggestions.append(suggestion)
                except Exception:
                    suggestion = await self.create_suggestion({
                        "department_id": insight.department_id,
                        "issue_summary": f"Function {insight.entity_id} has high error rate of {insight.metrics.get('error_rate')}",
                        "suggested_action": {
                            "type": "review_function",
                            "details": {
                                "function_id": insight.entity_id,
                                "error_rate": insight.metrics.get("error_rate"),
                                "total_executions": insight.metrics.get("total_executions")
                            }
                        },
                        "confidence_score": 0.8,
                        "source": SuggestionSource.FUNCTION_USAGE,
                        "status": SuggestionStatus.PENDING
                    })
                    suggestions.append(suggestion)
            
            if (insight.category == InsightCategory.INACTIVE_ENTITY and 
                insight.metrics.get("total_executions", 0) < 3):
                
                suggestion = await self.create_suggestion({
                    "department_id": insight.department_id,
                    "issue_summary": f"Function {insight.entity_id} is rarely used ({insight.metrics.get('total_executions')} times in {insight.metrics.get('days_monitored')} days)",
                    "suggested_action": {
                        "type": "remove_function",
                        "details": {
                            "function_id": insight.entity_id,
                            "usage_count": insight.metrics.get("total_executions"),
                            "period_days": insight.metrics.get("days_monitored")
                        }
                    },
                    "confidence_score": 0.7,
                    "source": SuggestionSource.FUNCTION_USAGE,
                    "status": SuggestionStatus.PENDING
                })
                suggestions.append(suggestion)
                
        return suggestions
    
    async def evaluate_ai_consumption_insights(self) -> List[ArturSuggestion]:
        """Evaluate AI consumption insights and generate suggestions"""
        insights = self.insights_db.get_multi()
        ai_insights = [
            i for i in insights 
            if i.category == InsightCategory.AI_CONSUMPTION
        ]
        
        suggestions = []
        for insight in ai_insights:
            if insight.metrics.get("prompt_count", 0) < 5:
                suggestion = await self.create_suggestion({
                    "department_id": insight.department_id,
                    "issue_summary": f"Department {insight.department_id} has AI enabled but low usage ({insight.metrics.get('prompt_count')} prompts in {insight.metrics.get('days_monitored')} days)",
                    "suggested_action": {
                        "type": "disable_ai",
                        "details": {
                            "department_id": insight.department_id,
                            "prompt_count": insight.metrics.get("prompt_count"),
                            "token_count": insight.metrics.get("token_count"),
                            "period_days": insight.metrics.get("days_monitored")
                        }
                    },
                    "confidence_score": 0.6,
                    "source": SuggestionSource.AI_USAGE,
                    "status": SuggestionStatus.PENDING
                })
                suggestions.append(suggestion)
                
        return suggestions
    
    async def run_all_evaluations(self) -> List[ArturSuggestion]:
        """Run all evaluation functions and return combined suggestions"""
        suggestions = []
        
        function_suggestions = await self.evaluate_function_usage_insights()
        suggestions.extend(function_suggestions)
        
        ai_suggestions = await self.evaluate_ai_consumption_insights()
        suggestions.extend(ai_suggestions)
        
        
        return suggestions

evaluation_service = EvaluationService()
