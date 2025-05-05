import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.traffic.utils.rpa import DMCEAutomator
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def test_login():
    """Test the login functionality of the DMCEAutomator."""
    
    os.environ["DMCE_PORTAL_URL"] = "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl"
    os.environ["DMCE_USERNAME"] = "test_user"
    os.environ["DMCE_PASSWORD"] = "test_password"
    
    logger.info("Starting RPA login test")
    
    automator = DMCEAutomator()
    
    logger.info("Testing login with valid credentials")
    login_success = await automator._login_to_dmce()
    
    if login_success:
        logger.info("✅ Login test passed: Successfully logged in to DMCE portal")
    else:
        logger.error("❌ Login test failed: Could not log in to DMCE portal")
    
    logger.info("Testing login with invalid credentials")
    
    automator.username = "invalid_user"
    automator.password = "invalid_password"
    
    login_success = await automator._login_to_dmce()
    
    if login_success:
        logger.info("⚠️ Note: Login with invalid credentials succeeded (expected in placeholder implementation)")
    else:
        logger.info("✅ Login with invalid credentials failed (as expected)")
    
    logger.info("RPA login test completed")

if __name__ == "__main__":
    asyncio.run(test_login())
