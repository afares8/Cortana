import logging
from typing import Dict, List, Any

from app.services.ai.mistral_client import MistralClient

logger = logging.getLogger(__name__)
mistral_client = MistralClient()

async def explain_issues(diagnostic_items: List[Dict[str, Any]]) -> str:
    """
    Generate an explanation for diagnostic issues using Mistral AI.
    
    Args:
        diagnostic_items: List of diagnostic items with issues
        
    Returns:
        str: Explanation of the issues
    """
    try:
        issues = [item for item in diagnostic_items if item["status"] in ["warning", "error"]]
        
        if not issues:
            return "No issues detected in the system."
            
        prompt = "You are an expert system diagnostician. Explain the following system diagnostic issues in plain language, focusing on possible causes and their relations:\n\n"
        
        for issue in issues:
            prompt += f"Component: {issue['component']}\n"
            prompt += f"Status: {issue['status']}\n"
            prompt += f"Description: {issue['description']}\n"
            
            if "error_details" in issue and issue["error_details"]:
                prompt += f"Error: {issue['error_details'].get('error', 'Unknown error')}\n"
                
            if "details" in issue and issue["details"]:
                if isinstance(issue["details"], dict) and "warnings" in issue["details"]:
                    warnings = issue["details"]["warnings"]
                    if warnings:
                        prompt += "Warnings:\n"
                        for warning in warnings:
                            prompt += f"- {warning}\n"
            
            prompt += "\n"
            
        prompt += "Provide a comprehensive but concise explanation of these issues, their potential causes, and how they might be related to each other. Focus on understanding the system state and identifying the root causes."
        
        explanation_result = await mistral_client.generate(prompt)
        
        if isinstance(explanation_result, dict) and "generated_text" in explanation_result:
            explanation = explanation_result["generated_text"]
        else:
            explanation = str(explanation_result)
        
        if "Note: This is a fallback response" in explanation:
            explanation = "The AI explanation service is currently operating in fallback mode. " + \
                         "Please check the AI service status for more information."
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error explaining issues: {e}")
        return str(f"Failed to generate explanation for diagnostic issues: {str(e)}")
