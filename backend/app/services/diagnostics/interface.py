import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
   
from app.services.diagnostics.checker import run_all_checks
from app.services.diagnostics.explainer import explain_issues
from app.services.diagnostics.code_suggester import suggest_action
from app.services.diagnostics.predictive import analyze_trends
from app.services.diagnostics.stats_tracker import log_diagnostic_run, get_component_history, get_diagnostic_stats

logger = logging.getLogger(__name__)

class DiagnosticsService:
    """Service for running diagnostics on the system."""
    
    async def run_diagnostics(self, components: Optional[List[str]] = None, 
                             include_explanations: bool = True,
                             include_suggestions: bool = True,
                             include_predictions: bool = False) -> Dict[str, Any]:
        """
        Run diagnostics on the system.
        
        Args:
            components: List of components to diagnose. If None, all components will be diagnosed.
            include_explanations: Whether to include explanations for issues using Mistral AI
            include_suggestions: Whether to include suggestions for fixing issues
            include_predictions: Whether to include predictions for future issues
            
        Returns:
            Dict[str, Any]: Diagnostic results
        """
        try:
            diagnostic_items = await run_all_checks()
            
            if components:
                diagnostic_items = [item for item in diagnostic_items 
                                   if item.get("component") in components]
            
            if include_suggestions:
                for item in diagnostic_items:
                    if item.get("status") in ["warning", "error"]:
                        suggestion = await suggest_action(item)
                        if suggestion:
                            item["suggested_action"] = suggestion
            
            if include_predictions:
                for item in diagnostic_items:
                    component = item.get("component")
                    if component:
                        history = await get_component_history(component)
                        prediction = await analyze_trends(component, history)
                        item["prediction"] = prediction
            
            if any(item.get("status") == "error" for item in diagnostic_items):
                overall_status = "error"
            elif any(item.get("status") == "warning" for item in diagnostic_items):
                overall_status = "warning"
            else:
                overall_status = "healthy"
            
            explanation = None
            if include_explanations and overall_status in ["warning", "error"]:
                explanation = await explain_issues(diagnostic_items)
            
            await log_diagnostic_run(diagnostic_items)
            
            return {
                "items": diagnostic_items,
                "overall_status": overall_status,
                "timestamp": datetime.utcnow(),
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Error running diagnostics: {e}")
            return {
                "items": [{
                    "component": "diagnostics",
                    "status": "error",
                    "description": "Error running diagnostics",
                    "timestamp": datetime.utcnow(),
                    "error_details": {
                        "error": str(e)
                    }
                }],
                "overall_status": "error",
                "timestamp": datetime.utcnow(),
                "error": str(e)
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get diagnostic statistics.
        
        Returns:
            Dict[str, Any]: Diagnostic statistics
        """
        try:
            return await get_diagnostic_stats()
        except Exception as e:
            logger.error(f"Error getting diagnostic stats: {e}")
            return {
                "error": str(e)
            }

diagnostics_service = DiagnosticsService()
