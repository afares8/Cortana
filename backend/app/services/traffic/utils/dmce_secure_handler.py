"""
DMCE Portal Login Handler - Secure Window Handling Approach

This module provides a Playwright implementation directly inspired by Ahmed's Selenium example,
focusing on explicit window handling after clicking the login button.
"""
import asyncio
import logging
import os
import time
from typing import Tuple, Optional, List
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError

logger = logging.getLogger(__name__)

async def dmce_login_with_window_handling(
    url: str = os.getenv("DMCE_PORTAL_URL", "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl"),
    username: str = os.getenv("DMCE_USERNAME", ""),
    password: str = os.getenv("DMCE_PASSWORD", ""),
    headless: bool = True,
    screenshots_dir: Optional[str] = None
) -> Tuple[bool, Optional[Page], Optional[Browser]]:
    """
    Login to DMCE portal using explicit window handling.
    
    This implementation is directly inspired by Ahmed's Selenium example:
    driver.switch_to.window(driver.window_handles[-1])
    
    Args:
        url: DMCE portal URL from environment variable
        username: DMCE username from environment variable
        password: DMCE password from environment variable
        headless: Whether to run the browser in headless mode
        screenshots_dir: Directory to save screenshots (optional)
        
    Returns:
        tuple: (success, dashboard_page, browser) where success is a boolean indicating if login was successful,
               dashboard_page is the Playwright page object for the dashboard if successful,
               and browser is the browser instance
    """
    if screenshots_dir:
        os.makedirs(screenshots_dir, exist_ok=True)
    
    logger.info("Starting DMCE login with window handling")
    logger.info(f"Headless mode: {headless}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        
        page = await context.new_page()
        
        try:
            logger.info("Navigating to DMCE portal")
            await page.goto(url, wait_until="networkidle")
            
            if screenshots_dir:
                await page.screenshot(path=f"{screenshots_dir}/01_portal.png", full_page=True)
                with open(f"{screenshots_dir}/portal.html", "w") as f:
                    f.write(await page.content())
            
            pages_before = context.pages
            logger.info(f"Pages before clicking: {len(pages_before)}")
            
            logger.info("Clicking login button")
            await page.click("a.login-btn")
            
            logger.info("Waiting for new window to open")
            await asyncio.sleep(2)
            
            pages_after = context.pages
            logger.info(f"Pages after clicking: {len(pages_after)}")
            
            new_pages = [p for p in pages_after if p not in pages_before]
            
            if new_pages:
                login_page = new_pages[0]
                logger.info("New window detected")
                
                await login_page.wait_for_load_state("networkidle")
                
                if screenshots_dir:
                    await login_page.screenshot(path=f"{screenshots_dir}/02_login_page.png", full_page=True)
                    with open(f"{screenshots_dir}/login_page.html", "w") as f:
                        f.write(await login_page.content())
                
                logger.info("Login page loaded successfully")
                
                logger.info("Filling username field")
                await login_page.fill("input[name='username'], input#username", username)
                
                logger.info("Filling password field")
                await login_page.fill("input[name='password'], input#password", password)
                
                if screenshots_dir:
                    await login_page.screenshot(path=f"{screenshots_dir}/03_before_submit.png", full_page=True)
                
                logger.info("Submitting login form")
                async with login_page.expect_navigation(wait_until="networkidle", timeout=15000):
                    await login_page.click("button:has-text('Sign In'), button[type='submit']")
                
                if screenshots_dir:
                    await login_page.screenshot(path=f"{screenshots_dir}/04_after_login.png", full_page=True)
                
                logger.info("Login form submitted")
                
                dashboard_indicators = [
                    "text=Crear Nueva DMCE",
                    "text=Cerrar Sesión",
                    "text=Create New DMCE",
                    "text=Logout"
                ]
                
                for indicator in dashboard_indicators:
                    try:
                        await login_page.wait_for_selector(indicator, timeout=5000)
                        logger.info(f"Dashboard element found: {indicator}")
                        
                        if screenshots_dir:
                            await login_page.screenshot(path=f"{screenshots_dir}/05_dashboard.png", full_page=True)
                            with open(f"{screenshots_dir}/dashboard.html", "w") as f:
                                f.write(await login_page.content())
                        
                        return True, login_page, browser
                    except TimeoutError:
                        continue
                
                logger.error("No dashboard indicators found in login page")
                
                if screenshots_dir:
                    await login_page.screenshot(path=f"{screenshots_dir}/error_no_dashboard.png", full_page=True)
                
                return False, login_page, browser
            else:
                logger.error("No new window detected after clicking login button")
                
                logger.info("Trying fallback approach - direct URL navigation")
                
                signin_url = url.replace("login.cl", "signin.cl")
                logger.info("Navigating directly to signin URL")
                
                await page.goto(signin_url, wait_until="networkidle")
                
                if screenshots_dir:
                    await page.screenshot(path=f"{screenshots_dir}/02_direct_signin.png", full_page=True)
                
                logger.info("Filling username field")
                await page.fill("input[name='username'], input#username", username)
                
                logger.info("Filling password field")
                await page.fill("input[name='password'], input#password", password)
                
                if screenshots_dir:
                    await page.screenshot(path=f"{screenshots_dir}/03_before_submit_direct.png", full_page=True)
                
                logger.info("Submitting login form")
                async with page.expect_navigation(wait_until="networkidle", timeout=15000):
                    await page.click("button:has-text('Sign In'), button[type='submit']")
                
                if screenshots_dir:
                    await page.screenshot(path=f"{screenshots_dir}/04_after_login_direct.png", full_page=True)
                
                logger.info("Login form submitted")
                
                dashboard_indicators = [
                    "text=Crear Nueva DMCE",
                    "text=Cerrar Sesión",
                    "text=Create New DMCE",
                    "text=Logout"
                ]
                
                for indicator in dashboard_indicators:
                    try:
                        await page.wait_for_selector(indicator, timeout=5000)
                        logger.info(f"Dashboard element found: {indicator}")
                        
                        if screenshots_dir:
                            await page.screenshot(path=f"{screenshots_dir}/05_dashboard_direct.png", full_page=True)
                            with open(f"{screenshots_dir}/dashboard_direct.html", "w") as f:
                                f.write(await page.content())
                        
                        return True, page, browser
                    except TimeoutError:
                        continue
                
                logger.error("No dashboard indicators found in direct navigation")
                
                if screenshots_dir:
                    await page.screenshot(path=f"{screenshots_dir}/error_no_dashboard_direct.png", full_page=True)
                
                return False, page, browser
            
        except Exception as e:
            logger.error(f"Error during DMCE login: {str(e)}")
            
            if screenshots_dir and page:
                await page.screenshot(path=f"{screenshots_dir}/error.png", full_page=True)
            
            return False, None, browser

async def test_dmce_login():
    """
    Test function for DMCE login.
    """
    screenshots_dir = "/tmp/dmce_window_handler"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    username = os.getenv("DMCE_USERNAME", "")
    password = os.getenv("DMCE_PASSWORD", "")
    url = os.getenv("DMCE_PORTAL_URL", "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl")
    
    if not username or not password:
        logger.warning("DMCE credentials not set in environment variables")
        logger.warning("Please set DMCE_USERNAME and DMCE_PASSWORD environment variables")
        return False
    
    logger.info("Starting DMCE login test with window handling")
    logger.info(f"Screenshots will be saved to {screenshots_dir}")
    
    success, dashboard_page, browser = await dmce_login_with_window_handling(
        url=url,
        username=username,
        password=password,
        headless=True,
        screenshots_dir=screenshots_dir
    )
    
    if success and dashboard_page:
        logger.info("DMCE login test passed")
        
        with open(f"{screenshots_dir}/summary.md", "w") as f:
            f.write("# DMCE Login Test Summary\n\n")
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
        logger.error("DMCE login test failed")
        
        with open(f"{screenshots_dir}/summary.md", "w") as f:
            f.write("# DMCE Login Test Summary\n\n")
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    asyncio.run(test_dmce_login())
