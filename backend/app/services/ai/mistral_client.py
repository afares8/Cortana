"""
Client for interacting with the Mistral 7B model via the Text Generation Inference API.
"""
import json
import logging
import httpx
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MistralRequest(BaseModel):
    inputs: str
    parameters: Dict[str, Any] = {
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.95,
        "do_sample": True,
        "repetition_penalty": 1.1
    }

class MistralClient:
    def __init__(self, base_url: str = "http://ai-service:80"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the Mistral 7B model.
        
        Args:
            prompt: The input prompt for the model
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            The generated text response
        """
        parameters = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True,
            "repetition_penalty": 1.1
        }
        
        parameters.update(kwargs)
        
        request = MistralRequest(
            inputs=prompt,
            parameters=parameters
        )
        
        try:
            response = await self.client.post(
                f"{self.base_url}/generate",
                json=request.dict(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            if "generated_text" in result:
                return result["generated_text"]
            else:
                logger.error(f"Unexpected response format: {result}")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating text with Mistral: {e}")
            return f"Error: {str(e)}"
    
    async def analyze_contract(self, contract_text: str, query: str) -> Dict[str, Any]:
        """
        Analyze a contract using the Mistral 7B model.
        
        Args:
            contract_text: The text of the contract to analyze
            query: The specific analysis query (e.g., "Extract key clauses", "Identify risks")
            
        Returns:
            A dictionary containing the analysis results
        """
        max_contract_length = 3000
        if len(contract_text) > max_contract_length:
            contract_text = contract_text[:max_contract_length] + "..."
        
        prompt = f"""You are a legal AI assistant specialized in contract analysis.

CONTRACT TEXT:
{contract_text}

TASK:
{query}

Provide your analysis in JSON format with appropriate fields based on the task.
"""
        
        try:
            response_text = await self.generate(prompt, temperature=0.3, max_new_tokens=1024)
            
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from response: {json_str}")
                    return {"error": "Failed to parse analysis results", "raw_response": response_text}
            else:
                return {"analysis": response_text}
                
        except Exception as e:
            logger.error(f"Error analyzing contract: {e}")
            return {"error": str(e)}
    
    async def query_legal_assistant(self, query: str, context: Optional[str] = None) -> str:
        """
        Query the legal assistant with a natural language question.
        
        Args:
            query: The user's question
            context: Optional context information (e.g., relevant contract snippets)
            
        Returns:
            The assistant's response
        """
        context_text = f"\nCONTEXT:\n{context}\n\n" if context else "\n"
        
        prompt = f"""You are a legal AI assistant for a contract management system.

USER QUERY:
{query}
{context_text}
Provide a helpful, accurate, and concise response based on the information available.
"""
        
        try:
            response = await self.generate(prompt, temperature=0.7, max_new_tokens=512)
            return response.strip()
        except Exception as e:
            logger.error(f"Error querying legal assistant: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"

mistral_client = MistralClient()
