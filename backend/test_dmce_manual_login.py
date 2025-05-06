"""
Test script for the DMCE manual login utility.

This script tests the DMCE manual login utility that provides a fallback
mechanism when automated login fails.
"""
import asyncio
import logging
import os
from app.services.traffic.utils.dmce_manual_login import start_manual_login, complete_manual_login, cleanup_session

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/dmce_manual_login_test.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_dmce_manual_login():
    """
    Test the DMCE manual login utility.
    """
    company = "Crandon"
    
    logger.info(f'Starting DMCE manual login test for company {company}')
    
    start_result = await start_manual_login(company=company)
    
    if not start_result.get("success", False):
        logger.error(f"Failed to start manual login session: {start_result.get('error', 'Unknown error')}")
        return False
    
    session_id = start_result.get("sessionId")
    logger.info(f"Manual login session started with ID: {session_id}")
    
    logger.info("Please complete the login process in the Firefox window that opened.")
    logger.info("Press Enter when you have completed the login process...")
    
    input()
    
    complete_result = await complete_manual_login(session_id=session_id)
    
    if complete_result.get("success", False):
        logger.info("✅ DMCE manual login test passed!")
        logger.info(complete_result.get("message", "Login completed successfully"))
    else:
        logger.error(f"❌ DMCE manual login test failed: {complete_result.get('error', 'Unknown error')}")
    
    await cleanup_session(session_id)
    
    return complete_result.get("success", False)

if __name__ == "__main__":
    asyncio.run(test_dmce_manual_login())
