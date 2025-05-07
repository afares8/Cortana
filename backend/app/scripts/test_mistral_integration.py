"""
Test script to validate Mistral AI integration fixes.
This script tests both the test-mistral endpoint and the generate endpoint.
"""

import asyncio
import httpx
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_mistral_health():
    """Test the /api/v1/test-mistral endpoint."""
    logger.info("Testing Mistral health endpoint...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get("http://localhost:8000/api/v1/test-mistral")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Response status: {response.status_code}")
            
            is_fallback = data.get("is_fallback", True)
            connection_successful = data.get("connection_successful", False)
            environment_suitable = data.get("environment_suitable", False)
            
            logger.info(f"Using fallback mode: {is_fallback}")
            logger.info(f"Connection successful: {connection_successful}")
            logger.info(f"Environment suitable: {environment_suitable}")
            
            env_config = data.get("environment_config", {})
            logger.info(f"Fallback mode from env: {env_config.get('fallback_mode_setting_from_env')}")
            logger.info(f"Current fallback mode: {env_config.get('current_fallback_mode')}")
            
            logger.info("Full response:")
            print(json.dumps(data, indent=2))
            
            return data
            
        except Exception as e:
            logger.error(f"Error testing Mistral health: {e}")
            return None

async def test_mistral_generate():
    """Test the generation endpoint with a simple prompt."""
    logger.info("Testing Mistral generate endpoint...")
    
    test_prompt = "What is a termination clause in a contract?"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/ai/mistral/generate",
                json={
                    "prompt": test_prompt,
                    "debug": True
                }
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Response status: {response.status_code}")
            
            is_fallback = data.get("is_fallback", True)
            logger.info(f"Using fallback mode: {is_fallback}")
            
            response_text = data.get("generated_text", "")
            logger.info(f"Response preview: {response_text[:200]}...")
            
            if "fallback response" in response_text.lower():
                logger.warning("Response contains fallback indicator text")
            
            return data
            
        except Exception as e:
            logger.error(f"Error testing Mistral generate: {e}")
            return None

async def main():
    """Run all tests."""
    health_data = await test_mistral_health()
    
    generate_data = await test_mistral_generate()
    
    if health_data and generate_data:
        logger.info("All tests completed successfully")
        
        health_fallback = health_data.get("is_fallback", True)
        generate_fallback = generate_data.get("is_fallback", True)
        
        if not health_fallback and not generate_fallback:
            logger.info("SUCCESS: Both endpoints are NOT using fallback mode")
            return 0
        else:
            logger.warning("WARNING: One or both endpoints are still using fallback mode")
            return 1
    else:
        logger.error("ERROR: One or both tests failed")
        return 2

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)
