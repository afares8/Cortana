import os
import json
import logging
import httpx
from typing import Optional, Dict, Any, List, Union
import time

from app.services.ai.utils.spanish_input_pipeline import SpanishInputPipeline

logger = logging.getLogger(__name__)

class MistralClient:
    """
    Client for interacting with the Mistral 7B model.
    """
    
    def __init__(self):
        self.api_url = os.getenv("MISTRAL_API_URL", "http://ai-service:80")
        self.model_name = os.getenv("MISTRAL_MODEL_NAME", "teknium/OpenHermes-2.5-Mistral-7B")
        self.fallback_mode = os.getenv("AI_FALLBACK_MODE", "true").lower() == "true"
        self.language_mode = os.getenv("AI_LANGUAGE_MODE", "auto")
        self.spanish_pipeline = SpanishInputPipeline()
        
        self._check_service_health()
    
    async def generate(
        self,
        prompt: str,
        max_new_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9,
        debug: bool = False
    ) -> str:
        """
        Generate text using the Mistral model.
        """
        if self.fallback_mode:
            return self._get_fallback_response(prompt)
        
        original_prompt = prompt
        processed_prompt = prompt
        
        if self.language_mode == "es" or (self.language_mode == "auto" and self.spanish_pipeline.is_spanish(prompt)):
            try:
                processed_prompt = self.spanish_pipeline.preprocess(prompt)
                if debug:
                    logger.info(f"Spanish input detected. Original: '{original_prompt}' -> Processed: '{processed_prompt}'")
            except Exception as e:
                logger.error(f"Error in Spanish preprocessing: {str(e)}")
                processed_prompt = prompt
        
        try:
            payload = {
                "inputs": processed_prompt,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "top_p": top_p
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.api_url}/generate", json=payload)
                
                if response.status_code != 200:
                    logger.error(f"Error from Mistral API: {response.status_code} - {response.text}")
                    self.fallback_mode = True
                    return self._get_fallback_response(prompt)
                
                result = response.json()
                
                if isinstance(result, list) and "generated_text" in result[0]:
                    logger.info("Successfully extracted generated_text from response (list format)")
                    return result[0]["generated_text"]
                elif isinstance(result, dict) and "generated_text" in result:
                    logger.info("Successfully extracted generated_text from response (dict format)")
                    return result["generated_text"]
                else:
                    logger.error(f"Unexpected response format: {result}")
                    self.fallback_mode = True
                    return self._get_fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"Error calling Mistral API: {str(e)}")
            self.fallback_mode = True
            return self._get_fallback_response(prompt)
    
    def _check_service_health(self):
        """
        Check if the AI service is healthy.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.api_url}/health")
                
                if response.status_code == 200:
                    logger.info("AI service is healthy")
                    self.fallback_mode = False
                    return
                
                logger.warning(f"AI service health check failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"Error checking AI service health: {str(e)}")
        
        logger.warning("Using fallback mode for AI service")
        self.fallback_mode = True
    
    def _get_fallback_response(self, prompt: str) -> str:
        """
        Get a fallback response when the AI service is not available.
        """
        try:
            mock_file = os.path.join(os.path.dirname(__file__), "mock_service", "generate")
            if os.path.exists(mock_file):
                with open(mock_file, "r") as f:
                    mock_data = json.load(f)
                    return mock_data.get("generated_text", "Fallback response not available")
        except Exception as e:
            logger.error(f"Error reading fallback response: {str(e)}")
        
        return "This is a fallback response. The AI service is currently unavailable."
