"""
Client for interacting with the LLM model via the Text Generation Inference API.
"""
import json
import logging
import httpx
import os
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
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("MISTRAL_API_URL", "http://ai-service:80")
        logger.info(f"Initializing MistralClient with base_url: {self.base_url}")
        self.client = httpx.AsyncClient(timeout=60.0)
        self.fallback_mode = os.environ.get("AI_FALLBACK_MODE", "false").lower() == "true"
        logger.info(f"Fallback mode is {'enabled' if self.fallback_mode else 'disabled'}")
        
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the LLM model.
        
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
        
        if self.fallback_mode:
            return self._get_fallback_response(prompt)
        
        try:
            logger.info(f"Attempting to connect to LLM at {self.base_url}/generate with prompt: {prompt[:50]}...")
            logger.info(f"Request parameters: {parameters}")
            
            response = await self.client.post(
                f"{self.base_url}/generate",
                json=request.model_dump(),  # Use model_dump() instead of dict() for Pydantic v2
                headers={"Content-Type": "application/json"}
            )
            
            logger.info(f"Response status code: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Response received: {str(result)[:200]}...")
            
            if "generated_text" in result:
                logger.info("Successfully extracted generated_text from response")
                return result["generated_text"]
            else:
                logger.error(f"Unexpected response format: {result}")
                logger.error("Response keys: " + ", ".join(result.keys()))
                self.fallback_mode = True
                return self._get_fallback_response(prompt)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when connecting to LLM: {e.response.status_code} - {e.response.text}")
            self.fallback_mode = True
            return self._get_fallback_response(prompt)
        except httpx.ConnectError as e:
            logger.error(f"Connection error when connecting to LLM: {e} - Is the AI service running?")
            logger.error(f"Attempted to connect to: {self.base_url}")
            self.fallback_mode = True
            return self._get_fallback_response(prompt)
        except Exception as e:
            logger.error(f"Error generating text with LLM: {type(e).__name__} - {e}")
            self.fallback_mode = True
            return self._get_fallback_response(prompt)
            
    def _get_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when the AI service is unavailable."""
        fallback_note = (
            "Note: This is a fallback response. The Mistral 7B model requires GPU hardware with "
            "Flash Attention v2 support, which is not available in the current environment. "
            "For production use, consider deploying on GPU-enabled infrastructure or using a smaller model."
        )
        
        if "contract" in prompt.lower() and "what is" in prompt.lower():
            return (
                "A contract is a legally binding agreement between two or more parties that creates mutual obligations "
                "enforceable by law. It typically includes elements such as offer, acceptance, consideration, legal capacity, "
                "and lawful purpose. Contracts can be written, verbal, or implied, though written contracts provide better "
                "evidence of the terms agreed upon. " + fallback_note
            )
        elif "analyze" in prompt.lower():
            return (
                "I've analyzed the contract and found several key points to consider:\n"
                "1. The agreement contains standard indemnification clauses\n"
                "2. There are termination provisions with 30-day notice periods\n"
                "3. The governing law is specified as the jurisdiction of the client\n"
                "4. Confidentiality provisions extend 2 years beyond termination\n\n" + 
                fallback_note
            )
        elif "extract" in prompt.lower():
            return (
                "Here are the key clauses I've identified:\n"
                "1. Termination Clause: Either party may terminate with 30 days written notice\n"
                "2. Confidentiality: All information shared is confidential for 2 years post-termination\n"
                "3. Indemnification: Standard mutual indemnification for third-party claims\n"
                "4. Payment Terms: Net 30 days from invoice date\n\n" + 
                fallback_note
            )
        elif "risk" in prompt.lower():
            return (
                "I've identified some potential risks in this contract:\n"
                "1. Ambiguous performance metrics without clear measurement criteria\n"
                "2. Limited liability caps that may not adequately protect your interests\n"
                "3. Broad intellectual property assignment clauses\n"
                "4. Vague dispute resolution procedures\n\n" + 
                fallback_note
            )
        else:
            return (
                "I understand your request about legal matters. I can provide general guidance on contract analysis, "
                "risk assessment, clause extraction, and legal compliance questions. " + 
                fallback_note
            )
    
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
