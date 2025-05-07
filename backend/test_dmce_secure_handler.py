"""
Test script for the DMCE secure window handler utility.

This script tests the DMCE secure window handler utility that uses explicit window handling
after clicking the login button, directly inspired by Ahmed's Selenium example.
"""
import asyncio
import logging
import os
from app.services.traffic.utils.dmce_secure_handler import dmce_login_with_window_handling

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/dmce_secure_handler_test.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_dmce_secure_handler():
    """
    Test the DMCE secure window handler utility.
    """
    USER = os.getenv("DMCE_USERNAME", "")
    PASS = os.getenv("DMCE_PASSWORD", "")
    URL = os.getenv("DMCE_PORTAL_URL", "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl")
    
    if not USER or not PASS:
        logger.warning("DMCE credentials not set in environment variables")
        logger.warning("Please set DMCE_USERNAME and DMCE_PASSWORD environment variables")
        return False
    
    screenshots_dir = '/tmp/dmce_secure_handler_test'
    os.makedirs(screenshots_dir, exist_ok=True)
    
    logger.info('Starting DMCE secure window handler test')
    logger.info(f'Screenshots will be saved to {screenshots_dir}')
    
    success, dashboard_page, browser = await dmce_login_with_window_handling(
        url=URL,
        username=USER,
        password=PASS,
        headless=False,  # Use non-headless mode for better window handling
        screenshots_dir=screenshots_dir
    )
    
    if success and dashboard_page:
        logger.info("✅ DMCE secure window handler test passed!")
        
        with open(f"{screenshots_dir}/summary.md", "w") as f:
            f.write("# DMCE Secure Window Handler Test Summary\n\n")
            f.write("## Test Results\n\n")
            f.write("- Success: ✅\n")
            f.write("- Dashboard loaded successfully\n\n")
            
            f.write("## Screenshots Captured\n\n")
            for i, filename in enumerate(sorted(os.listdir(screenshots_dir))):
                if filename.endswith(".png"):
                    f.write(f"{i+1}. {filename}\n")
            
            f.write("\n## HTML Files Captured\n\n")
            for i, filename in enumerate(sorted(os.listdir(screenshots_dir))):
                if filename.endswith(".html"):
                    f.write(f"{i+1}. {filename}\n")
        
        logger.info(f"Created summary file at {screenshots_dir}/summary.md")
    else:
        logger.error("❌ DMCE secure window handler test failed!")
        
        with open(f"{screenshots_dir}/summary.md", "w") as f:
            f.write("# DMCE Secure Window Handler Test Summary\n\n")
            f.write("## Test Results\n\n")
            f.write("- Success: ❌\n\n")
            
            f.write("## Screenshots Captured\n\n")
            for i, filename in enumerate(sorted(os.listdir(screenshots_dir))):
                if filename.endswith(".png"):
                    f.write(f"{i+1}. {filename}\n")
            
            f.write("\n## HTML Files Captured\n\n")
            for i, filename in enumerate(sorted(os.listdir(screenshots_dir))):
                if filename.endswith(".html"):
                    f.write(f"{i+1}. {filename}\n")
        
        logger.info(f"Created summary file at {screenshots_dir}/summary.md")
    
    if browser:
        await browser.close()
    
    return success

if __name__ == "__main__":
    asyncio.run(test_dmce_secure_handler())
