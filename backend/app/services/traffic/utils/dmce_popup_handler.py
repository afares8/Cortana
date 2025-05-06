"""
DMCE Portal Popup Handler Utility

This module provides functions for handling the DMCE portal login process,
including popup detection and direct URL navigation fallback.
"""
import asyncio
import logging
import os
import re
from typing import Tuple, Optional
from playwright.async_api import Page, Browser, BrowserContext, TimeoutError

logger = logging.getLogger(__name__)

async def login_to_dmce(page: Page, username: str, password: str) -> Tuple[bool, Optional[Page]]:
    """
    Login to DMCE portal using popup window detection with fallback to direct URL.
    
    Args:
        page: Playwright page object
        username: DMCE username
        password: DMCE password
        
    Returns:
        tuple: (success, dashboard_page) where success is a boolean indicating if login was successful
               and dashboard_page is the Playwright page object for the dashboard if successful
    """
    try:
        logger.info("Setting up popup event listener")
        popup_promise = page.wait_for_event("popup", timeout=10000)
        
        logger.info("Clicking login button (should open popup)...")
        await page.click("a.login-btn")
        
        try:
            popup = await popup_promise
            logger.info("✅ Popup detected!")
            
            await popup.wait_for_load_state("networkidle")
            logger.info(f"✅ Popup URL: {popup.url()}")
            
            logger.info(f"Filling username: {username}")
            await popup.fill("input[name='username'], input#username", username)
            
            logger.info("Filling password")
            await popup.fill("input[name='password'], input#password", password)
            
            logger.info("Submitting login form")
            async with popup.expect_navigation(wait_until="networkidle", timeout=15000):
                await popup.click("button:has-text('Sign In'), button[type='submit']")
            
            logger.info(f"✅ Logged in, now at: {popup.url()}")
            
            dashboard_indicators = [
                "text=Crear Nueva DMCE",
                "text=Cerrar Sesión",
                "text=Create New DMCE",
                "text=Logout"
            ]
            
            for indicator in dashboard_indicators:
                try:
                    await popup.wait_for_selector(indicator, timeout=5000)
                    logger.info(f"✅ Dashboard element found: {indicator}")
                    return True, popup
                except TimeoutError:
                    continue
            
            logger.error("❌ No dashboard indicators found in popup")
            return False, popup
            
        except TimeoutError:
            logger.info("❌ No popup detected within timeout, trying direct URL approach")
            
            base_url = re.match(r'(https?://[^/]+)', page.url).group(1)
            signin_url = f"{base_url}/TFBFTZ/cusLogin/signin.cl?language=en"
            
            logger.info(f"Navigating directly to: {signin_url}")
            await page.goto(signin_url, wait_until="networkidle")
            
            logger.info(f"Filling username: {username}")
            await page.fill("input[name='username'], input#username", username)
            
            logger.info("Filling password")
            await page.fill("input[name='password'], input#password", password)
            
            logger.info("Submitting login form")
            async with page.expect_navigation(wait_until="networkidle", timeout=15000):
                await page.click("button:has-text('Sign In'), button[type='submit']")
            
            logger.info(f"✅ Logged in, now at: {page.url()}")
            
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
                    return True, page
                except TimeoutError:
                    continue
            
            logger.error("❌ No dashboard indicators found")
            return False, page
        
    except Exception as e:
        logger.error(f"Error during DMCE login: {str(e)}")
        return False, None

async def setup_dmce_session(
    browser: Browser, 
    url: str, 
    username: str, 
    password: str,
    screenshots_dir: Optional[str] = None
) -> Tuple[bool, Optional[Page], Optional[BrowserContext]]:
    """
    Set up a DMCE session by navigating to the portal and logging in.
    
    Args:
        browser: Playwright browser object
        url: DMCE portal URL
        username: DMCE username
        password: DMCE password
        screenshots_dir: Directory to save screenshots (optional)
        
    Returns:
        tuple: (success, dashboard_page, context) where success is a boolean indicating if login was successful,
               dashboard_page is the Playwright page object for the dashboard if successful,
               and context is the browser context
    """
    if screenshots_dir:
        os.makedirs(screenshots_dir, exist_ok=True)
    
    try:
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        
        page = await context.new_page()
        
        logger.info(f"Navigating to DMCE portal: {url}")
        await page.goto(url, wait_until="networkidle")
        
        if screenshots_dir:
            await page.screenshot(path=f"{screenshots_dir}/01_portal.png", full_page=True)
        
        success, dashboard_page = await login_to_dmce(page, username, password)
        
        if success and dashboard_page and screenshots_dir:
            await dashboard_page.screenshot(path=f"{screenshots_dir}/05_dashboard.png", full_page=True)
            logger.info("✅ Login successful!")
        elif not success and screenshots_dir:
            if dashboard_page:
                await dashboard_page.screenshot(path=f"{screenshots_dir}/error.png", full_page=True)
            else:
                await page.screenshot(path=f"{screenshots_dir}/error.png", full_page=True)
            logger.error("❌ Login failed")
        
        return success, dashboard_page, context
        
    except Exception as e:
        logger.error(f"Error during DMCE session setup: {str(e)}")
        
        if screenshots_dir and page:
            await page.screenshot(path=f"{screenshots_dir}/error.png", full_page=True)
        
        return False, None, None
