from fastapi import APIRouter, HTTPException
import logging
import os
import platform
import psutil
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
        system_info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "cpu_count": psutil.cpu_count(logical=False),
            "logical_cpu_count": psutil.cpu_count(logical=True),
            "has_gpu": False,  # Default assumption for cloud environment
        }
        
        current_fallback_mode = mistral_client.fallback_mode
        fallback_env_var = os.environ.get("AI_FALLBACK_MODE", "false").lower() == "true"
        
        logger.info(f"Attempting to connect to Mistral model at: {mistral_client.base_url}")
        logger.info(f"Current fallback mode: {current_fallback_mode}, Environment setting: {fallback_env_var}")
        
        original_fallback_mode = mistral_client.fallback_mode
        mistral_client.fallback_mode = False
        
        try:
            response = await mistral_client.generate("What is a contract?")
            is_fallback = "fallback response" in response.lower()
        except Exception as connection_error:
            logger.error(f"Connection error: {connection_error}")
            response = f"Connection error: {str(connection_error)}"
            is_fallback = True
        finally:
            mistral_client.fallback_mode = original_fallback_mode
        
        logger.info(f"Received response from Mistral model: {response[:100]}...")
        
        hardware_requirements = {
            "gpu": "Required - NVIDIA GPU with CUDA support",
            "memory": "Minimum 16GB RAM",
            "disk": "Minimum 15GB free space for model weights",
            "special_requirements": "Flash Attention v2 support required for Mistral model"
        }
        
        return {
            "response": response,
            "is_fallback": is_fallback,
            "model_url": mistral_client.base_url,
            "connection_successful": not is_fallback,
            "system_info": system_info,
            "hardware_requirements": hardware_requirements,
            "environment_config": {
                "fallback_mode_setting": fallback_env_var,
                "current_fallback_mode": current_fallback_mode,
                "mistral_api_url": os.environ.get("MISTRAL_API_URL", "http://ai-service:80")
            },
            "recommendation": "The Mistral 7B model requires GPU with Flash Attention v2 support. "
                             "For CPU-only environments, use fallback mode or consider a smaller model."
        }
    except Exception as e:
        logger.error(f"Error testing Mistral model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test Mistral model: {str(e)}")
