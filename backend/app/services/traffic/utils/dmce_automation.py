"""
DMCE Portal Automation Utility

This module provides a comprehensive implementation for automating the DMCE portal,
combining multiple approaches for maximum reliability and handling the challenges
of popup windows and potential anti-automation measures.
"""
import asyncio
import logging
import os
import sys
import time
from typing import Tuple, Optional, Dict, Any, List
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError

logger = logging.getLogger(__name__)

class DMCEAutomation:
    """
    DMCE Portal Automation class that provides methods for interacting with the DMCE portal.
    
    This class combines multiple approaches for handling the DMCE portal's popup window
    and login process, with fallback mechanisms for maximum reliability.
    """
    
    def __init__(
        self,
        url: str = "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl",
        username: str = "crandonzlpr",
        password: str = "perfumes",
        headless: bool = True,
        screenshots_dir: Optional[str] = None,
        timeout: int = 30000
    ):
        """
        Initialize the DMCEAutomation class.
        
        Args:
            url: DMCE portal URL
            username: DMCE username
            password: DMCE password
            headless: Whether to run the browser in headless mode
            screenshots_dir: Directory to save screenshots (optional)
            timeout: Timeout for navigation and selector operations (in milliseconds)
        """
        self.url = url
        self.username = username
        self.password = password
        self.headless = headless
        self.screenshots_dir = screenshots_dir
        self.timeout = timeout
        self.browser = None
        self.context = None
        self.page = None
        self.dashboard_page = None
        
        if self.screenshots_dir:
            os.makedirs(self.screenshots_dir, exist_ok=True)
    
    async def __aenter__(self):
        """
        Async context manager entry point.
        """
        self.playwright = await async_playwright().__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point.
        """
        if self.browser:
            await self.browser.close()
        await self.playwright.__aexit__(exc_type, exc_val, exc_tb)
    
    async def setup_browser(self):
        """
        Set up the browser and context.
        
        Returns:
            bool: True if setup was successful, False otherwise
        """
        try:
            browser_args = {}
            if not self.headless:
                browser_args["args"] = ["--disable-popup-blocking", "--start-maximized"]
            
            self.browser = await self.playwright.chromium.launch(headless=self.headless, **browser_args)
            
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True
            )
            
            self.page = await self.context.new_page()
            
            return True
        except Exception as e:
            logger.error(f"Error setting up browser: {str(e)}")
            return False
    
    async def navigate_to_portal(self):
        """
        Navigate to the DMCE portal.
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            logger.info(f"Navigating to DMCE portal: {self.url}")
            await self.page.goto(self.url, wait_until="networkidle", timeout=self.timeout)
            
            if self.screenshots_dir:
                await self.page.screenshot(path=f"{self.screenshots_dir}/01_portal.png", full_page=True)
                
                html = await self.page.content()
                with open(f"{self.screenshots_dir}/portal.html", "w") as f:
                    f.write(html)
            
            return True
        except Exception as e:
            logger.error(f"Error navigating to portal: {str(e)}")
            return False
    
    async def login_with_popup_detection(self) -> bool:
        """
        Login to DMCE portal using popup detection approach.
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        try:
            logger.info("Trying popup detection approach")
            
            popup_promise = self.page.wait_for_event("popup", timeout=10000)
            
            logger.info("Clicking login button...")
            await self.page.click("a.login-btn")
            
            popup = await popup_promise
            logger.info("✅ Popup detected!")
            
            await popup.wait_for_load_state("networkidle", timeout=self.timeout)
            
            if self.screenshots_dir:
                await popup.screenshot(path=f"{self.screenshots_dir}/02_popup_detected.png", full_page=True)
                
                popup_html = await popup.content()
                with open(f"{self.screenshots_dir}/popup.html", "w") as f:
                    f.write(popup_html)
            
            logger.info(f"✅ Popup URL: {popup.url}")
            
            logger.info(f"Filling username: {self.username}")
            await popup.fill("input[name='username'], input#username", self.username)
            
            logger.info("Filling password")
            await popup.fill("input[name='password'], input#password", self.password)
            
            if self.screenshots_dir:
                await popup.screenshot(path=f"{self.screenshots_dir}/03_before_submit.png", full_page=True)
            
            logger.info("Submitting login form")
            async with popup.expect_navigation(wait_until="networkidle", timeout=self.timeout):
                await popup.click("button:has-text('Sign In'), button[type='submit']")
            
            if self.screenshots_dir:
                await popup.screenshot(path=f"{self.screenshots_dir}/04_after_login.png", full_page=True)
            
            logger.info(f"✅ Logged in, now at: {popup.url}")
            
            if await self.verify_dashboard(popup):
                self.dashboard_page = popup
                return True
            
            return False
            
        except TimeoutError:
            logger.error("❌ Popup detection approach failed")
            return False
        except Exception as e:
            logger.error(f"Error during popup detection login: {str(e)}")
            return False
    
    async def login_with_window_handling(self) -> bool:
        """
        Login to DMCE portal using window handling approach.
        
        This is equivalent to driver.switch_to.window(driver.window_handles[-1]) in Selenium.
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        try:
            logger.info("Trying window handling approach")
            
            pages_before = self.context.pages
            logger.info(f"Pages before clicking: {len(pages_before)}")
            
            try:
                await self.page.click("a.login-btn")
            except:
                logger.info("Login button already clicked, continuing with window handling")
            
            logger.info("Waiting for new window to open...")
            await asyncio.sleep(2)
            
            pages_after = self.context.pages
            logger.info(f"Pages after clicking: {len(pages_after)}")
            
            new_pages = [p for p in pages_after if p not in pages_before]
            
            if new_pages:
                login_page = new_pages[0]
                logger.info("✅ New window detected!")
                
                await login_page.wait_for_load_state("networkidle", timeout=self.timeout)
                
                if self.screenshots_dir:
                    await login_page.screenshot(path=f"{self.screenshots_dir}/02_window_handling.png", full_page=True)
                    
                    login_html = await login_page.content()
                    with open(f"{self.screenshots_dir}/login_page.html", "w") as f:
                        f.write(login_html)
                
                logger.info(f"✅ Login page URL: {login_page.url}")
                
                logger.info(f"Filling username: {self.username}")
                await login_page.fill("input[name='username'], input#username", self.username)
                
                logger.info("Filling password")
                await login_page.fill("input[name='password'], input#password", self.password)
                
                if self.screenshots_dir:
                    await login_page.screenshot(path=f"{self.screenshots_dir}/03_before_submit_window.png", full_page=True)
                
                logger.info("Submitting login form")
                async with login_page.expect_navigation(wait_until="networkidle", timeout=self.timeout):
                    await login_page.click("button:has-text('Sign In'), button[type='submit']")
                
                if self.screenshots_dir:
                    await login_page.screenshot(path=f"{self.screenshots_dir}/04_after_login_window.png", full_page=True)
                
                logger.info(f"✅ Logged in, now at: {login_page.url}")
                
                if await self.verify_dashboard(login_page):
                    self.dashboard_page = login_page
                    return True
                
                return False
            else:
                logger.error("❌ No new window detected after clicking login button")
                return False
                
        except Exception as e:
            logger.error(f"Error during window handling login: {str(e)}")
            return False
    
    async def login_with_direct_url(self) -> bool:
        """
        Login to DMCE portal using direct URL navigation approach.
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        try:
            logger.info("Trying direct URL approach")
            
            signin_url = self.url.replace("login.cl", "signin.cl")
            logger.info(f"Navigating directly to: {signin_url}")
            
            await self.page.goto(signin_url, wait_until="networkidle", timeout=self.timeout)
            
            if self.screenshots_dir:
                await self.page.screenshot(path=f"{self.screenshots_dir}/02_direct_signin.png", full_page=True)
            
            logger.info(f"Filling username: {self.username}")
            await self.page.fill("input[name='username'], input#username", self.username)
            
            logger.info("Filling password")
            await self.page.fill("input[name='password'], input#password", self.password)
            
            if self.screenshots_dir:
                await self.page.screenshot(path=f"{self.screenshots_dir}/03_before_submit_direct.png", full_page=True)
            
            logger.info("Submitting login form")
            async with self.page.expect_navigation(wait_until="networkidle", timeout=self.timeout):
                await self.page.click("button:has-text('Sign In'), button[type='submit']")
            
            if self.screenshots_dir:
                await self.page.screenshot(path=f"{self.screenshots_dir}/04_after_login_direct.png", full_page=True)
            
            logger.info(f"✅ Logged in, now at: {self.page.url}")
            
            if await self.verify_dashboard(self.page):
                self.dashboard_page = self.page
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error during direct URL login: {str(e)}")
            return False
    
    async def verify_dashboard(self, page: Page) -> bool:
        """
        Verify that the page contains dashboard indicators.
        
        Args:
            page: Playwright page object to verify
            
        Returns:
            bool: True if dashboard indicators are found, False otherwise
        """
        dashboard_indicators = [
            "text=Crear Nueva DMCE",
            "text=Cerrar Sesión",
            "text=Create New DMCE",
            "text=Logout"
        ]
        
        for indicator in dashboard_indicators:
            try:
                await page.wait_for_selector(indicator, timeout=5000)
                logger.info(f"✅ Dashboard element found: {indicator}")
                
                if self.screenshots_dir:
                    await page.screenshot(path=f"{self.screenshots_dir}/05_dashboard.png", full_page=True)
                    
                    dashboard_html = await page.content()
                    with open(f"{self.screenshots_dir}/dashboard.html", "w") as f:
                        f.write(dashboard_html)
                
                return True
            except TimeoutError:
                continue
        
        logger.error("❌ No dashboard indicators found")
        
        if self.screenshots_dir:
            await page.screenshot(path=f"{self.screenshots_dir}/error_no_dashboard.png", full_page=True)
        
        return False
    
    async def login(self) -> bool:
        """
        Login to DMCE portal using multiple approaches.
        
        This method tries multiple approaches in sequence:
        1. Popup detection
        2. Window handling
        3. Direct URL navigation
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        if await self.login_with_popup_detection():
            logger.info("✅ Login successful with popup detection approach")
            return True
        
        if await self.login_with_window_handling():
            logger.info("✅ Login successful with window handling approach")
            return True
        
        if await self.login_with_direct_url():
            logger.info("✅ Login successful with direct URL approach")
            return True
        
        logger.error("❌ All login approaches failed")
        return False
    
    async def create_new_dmce(self) -> bool:
        """
        Create a new DMCE declaration.
        
        This method assumes that login has been successful and dashboard_page is set.
        
        Returns:
            bool: True if creation was successful, False otherwise
        """
        if not self.dashboard_page:
            logger.error("❌ Dashboard page not set, login first")
            return False
        
        try:
            logger.info("Clicking 'Create New DMCE' button")
            await self.dashboard_page.click("text=Create New DMCE, text=Crear Nueva DMCE")
            
            await self.dashboard_page.wait_for_load_state("networkidle", timeout=self.timeout)
            
            if self.screenshots_dir:
                await self.dashboard_page.screenshot(path=f"{self.screenshots_dir}/06_new_dmce_form.png", full_page=True)
            
            logger.info("✅ New DMCE form loaded")
            return True
            
        except Exception as e:
            logger.error(f"Error creating new DMCE: {str(e)}")
            
            if self.screenshots_dir and self.dashboard_page:
                await self.dashboard_page.screenshot(path=f"{self.screenshots_dir}/error_create_dmce.png", full_page=True)
            
            return False
    
    async def close(self):
        """
        Close the browser.
        """
        if self.browser:
            await self.browser.close()
            self.browser = None

async def test_dmce_automation(
    url: str = "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl",
    username: str = "crandonzlpr",
    password: str = "perfumes",
    headless: bool = True,
    screenshots_dir: Optional[str] = None
) -> bool:
    """
    Test function for DMCE automation.
    
    Args:
        url: DMCE portal URL
        username: DMCE username
        password: DMCE password
        headless: Whether to run the browser in headless mode
        screenshots_dir: Directory to save screenshots (optional)
        
    Returns:
        bool: True if automation was successful, False otherwise
    """
    if screenshots_dir is None:
        screenshots_dir = "/tmp/dmce_automation_test"
    
    os.makedirs(screenshots_dir, exist_ok=True)
    
    logger.info(f"Starting DMCE automation test")
    logger.info(f"URL: {url}")
    logger.info(f"Headless: {headless}")
    logger.info(f"Screenshots will be saved to {screenshots_dir}")
    
    async with DMCEAutomation(
        url=url,
        username=username,
        password=password,
        headless=headless,
        screenshots_dir=screenshots_dir
    ) as dmce:
        if not await dmce.setup_browser():
            logger.error("❌ Failed to set up browser")
            return False
        
        if not await dmce.navigate_to_portal():
            logger.error("❌ Failed to navigate to portal")
            return False
        
        if not await dmce.login():
            logger.error("❌ Failed to login")
            return False
        
        if not await dmce.create_new_dmce():
            logger.error("❌ Failed to create new DMCE")
            return False
        
        logger.info("✅ DMCE automation test passed!")
        return True

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    import subprocess
    
    script_path = "/tmp/dmce_automation_test.py"
    with open(script_path, "w") as f:
        f.write("""
import asyncio
import logging
import os
import sys
from app.services.traffic.utils.dmce_automation import test_dmce_automation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    USER = os.getenv("DMCE_USERNAME", "crandonzlpr")
    PASS = os.getenv("DMCE_PASSWORD", "perfumes")
    URL  = os.getenv("DMCE_PORTAL_URL", "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl")
    
    screenshots_dir = '/tmp/dmce_automation_xvfb'
    os.makedirs(screenshots_dir, exist_ok=True)
    
    logger.info(f'Starting DMCE automation test with non-headless mode')
    logger.info(f'Screenshots will be saved to {screenshots_dir}')
    
    success = await test_dmce_automation(
        url=URL,
        username=USER,
        password=PASS,
        headless=False,
        screenshots_dir=screenshots_dir
    )
    
    if success:
        logger.info("✅ DMCE automation test passed!")
        sys.exit(0)
    else:
        logger.error("❌ DMCE automation test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
""")
    
    cmd = ["xvfb-run", "-a", "python", script_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    logger.info(f"xvfb-run stdout: {result.stdout}")
    logger.info(f"xvfb-run stderr: {result.stderr}")
    
    screenshots_dir = '/tmp/dmce_automation_xvfb'
    os.makedirs(screenshots_dir, exist_ok=True)
    
    with open(f"{screenshots_dir}/summary.md", "w") as f:
        f.write("# DMCE Automation Test Summary\n\n")
        f.write("## Test Results\n\n")
        f.write(f"- Return Code: {result.returncode}\n")
        f.write(f"- Success: {'✅' if result.returncode == 0 else '❌'}\n\n")
        
        f.write("## Stdout\n\n")
        f.write("```\n")
        f.write(result.stdout)
        f.write("\n```\n\n")
        
        f.write("## Stderr\n\n")
        f.write("```\n")
        f.write(result.stderr)
        f.write("\n```\n\n")
        
        f.write("## Screenshots Captured\n\n")
        if os.path.exists(screenshots_dir):
            for i, filename in enumerate(sorted([f for f in os.listdir(screenshots_dir) if f.endswith(".png")])):
                f.write(f"{i+1}. {filename}\n")
        else:
            f.write("No screenshots captured.\n")
        
        f.write("\n## HTML Files Captured\n\n")
        if os.path.exists(screenshots_dir):
            for i, filename in enumerate(sorted([f for f in os.listdir(screenshots_dir) if f.endswith(".html")])):
                f.write(f"{i+1}. {filename}\n")
        else:
            f.write("No HTML files captured.\n")
    
    logger.info(f"Created summary file at {screenshots_dir}/summary.md")
    
    sys.exit(result.returncode)
