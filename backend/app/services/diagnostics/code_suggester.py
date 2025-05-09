import logging
from typing import Dict, List, Any, Optional

from app.services.ai.mistral_client import MistralClient

logger = logging.getLogger(__name__)
mistral_client = MistralClient()

async def suggest_action(diagnostic_item: Dict[str, Any]) -> Optional[str]:
    """
    Generate a suggested action for fixing a diagnostic issue using Mistral AI.
    
    Args:
        diagnostic_item: Diagnostic item with an issue
        
    Returns:
        Optional[str]: Suggested action for fixing the issue
    """
    try:
        if diagnostic_item["status"] == "healthy":
            return None
            
        component = diagnostic_item["component"]
        status = diagnostic_item["status"]
        description = diagnostic_item["description"]
        
        error_details = diagnostic_item.get("error_details", {})
        error = error_details.get("error", "Unknown error") if error_details else "Unknown error"
        
        details = diagnostic_item.get("details", {})
        warnings = details.get("warnings", []) if isinstance(details, dict) else []
        
        prompt = "You are an expert system diagnostician and troubleshooter. Suggest a concrete action to fix the following system diagnostic issue:\n\n"
        prompt += f"Component: {component}\n"
        prompt += f"Status: {status}\n"
        prompt += f"Description: {description}\n"
        
        if error and error != "Unknown error":
            prompt += f"Error: {error}\n"
            
        if warnings:
            prompt += "Warnings:\n"
            for warning in warnings:
                prompt += f"- {warning}\n"
        
        if isinstance(details, dict):
            if component == "system_resources":
                if "cpu_percent" in details:
                    prompt += f"CPU Usage: {details['cpu_percent']}%\n"
                if "memory_percent" in details:
                    prompt += f"Memory Usage: {details['memory_percent']}%\n"
                if "disk_percent" in details:
                    prompt += f"Disk Usage: {details['disk_percent']}%\n"
            elif component.startswith("docker_"):
                if "status" in details:
                    prompt += f"Container Status: {details['status']}\n"
                if "image" in details:
                    prompt += f"Image: {details['image']}\n"
            elif component == "ai_service":
                if "service_type" in details:
                    prompt += f"Service Type: {details['service_type']}\n"
            elif component == "database":
                if "is_writable" in details:
                    prompt += f"Is Writable: {details['is_writable']}\n"
        
        prompt += "\nSuggest a specific, concrete action to fix this issue. Be precise and focus on actionable steps. If multiple actions may be needed, prioritize them based on likelihood of resolving the issue."
        
        suggestion_result = await mistral_client.generate(prompt)
        
        if isinstance(suggestion_result, dict) and "generated_text" in suggestion_result:
            suggestion = suggestion_result["generated_text"]
        else:
            suggestion = str(suggestion_result)
        
        if "Note: This is a fallback response" in suggestion:
            if component == "system_resources":
                return "Consider freeing up system resources by closing unnecessary applications or increasing available resources."
            elif component.startswith("docker_"):
                return "Try restarting the Docker container or checking its logs for specific error messages."
            elif component == "ai_service":
                return "Verify that the AI service container is running and properly configured. Check the container logs for more detailed error information."
            elif component == "database":
                return "Ensure the database directory exists and has proper write permissions."
            else:
                return "Check logs and configuration for this component to identify specific issues."
        
        return suggestion
        
    except Exception as e:
        logger.error(f"Error suggesting action: {e}")
        return f"Failed to generate action suggestion: {str(e)}"
