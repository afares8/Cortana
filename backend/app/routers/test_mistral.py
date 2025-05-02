from fastapi import APIRouter, HTTPException
import logging
from app.services.ai.mistral_client import mistral_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/test-mistral")
async def test_mistral():
    """
    Test endpoint to verify if the Mistral 7B model is responding.
    Returns the raw response from the model for a simple prompt.
    """
    try:
        original_fallback_mode = mistral_client.fallback_mode
        mistral_client.fallback_mode = False
        
        logger.info(f"Attempting to connect to Mistral model at: {mistral_client.base_url}")
        
        response = await mistral_client.generate("What is a contract?")
        
        logger.info(f"Received response from Mistral model: {response[:100]}...")
        
        mistral_client.fallback_mode = original_fallback_mode
        
        is_fallback = "fallback response" in response.lower()
        
        return {
            "response": response,
            "is_fallback": is_fallback,
            "model_url": mistral_client.base_url,
            "connection_successful": not is_fallback
        }
    except Exception as e:
        logger.error(f"Error testing Mistral model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test Mistral model: {str(e)}")
