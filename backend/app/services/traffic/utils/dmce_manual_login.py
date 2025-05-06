"""
DMCE Manual Login Handler

This module provides a backend API for handling manual login to the DMCE portal
using Firefox in Private Browsing mode as required by the DMCE support team.
"""
import asyncio
import logging
import os
import time
import uuid
from typing import Dict, Optional, Tuple, Any
from fastapi import HTTPException
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from app.core.config import settings

logger = logging.getLogger(__name__)

active_sessions: Dict[str, Dict[str, Any]] = {}

async def start_manual_login(company: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a manual login session by opening Firefox in Private Browsing mode.
    
    Args:
        company: Company name to use credentials for (optional)
        
    Returns:
        dict: Response with session ID and status information
    """
    session_id = str(uuid.uuid4())
    screenshots_dir = f"/tmp/dmce_manual_login_{session_id}"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    logger.info(f"Starting manual login session {session_id} for company {company}")
    
    try:
        username = settings.DMCE_USERNAME
        password = settings.DMCE_PASSWORD
        url = settings.DMCE_PORTAL_URL or "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl"
        
        playwright = await async_playwright().start()
        headless_mode = os.environ.get("DMCE_TEST_HEADLESS", "false").lower() == "true"
        browser = await playwright.firefox.launch(
            headless=headless_mode,
            args=["--private"]  # Enable Private Browsing mode
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        
        pages = context.pages
        if not pages:
            page = await context.new_page()
        else:
            page = pages[0]
            
        await page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        await context.clear_cookies()
        
        await page.goto(url, wait_until="networkidle")
        
        await page.screenshot(path=f"{screenshots_dir}/01_portal.png", full_page=True)
        
        pages_before = context.pages
        
        await page.click("a.login-btn")
        
        await asyncio.sleep(2)
        
        pages_after = context.pages
        
        new_pages = [p for p in pages_after if p not in pages_before]
        
        if new_pages:
            login_page = new_pages[0]
            
            await login_page.wait_for_load_state("networkidle")
            
            await login_page.screenshot(path=f"{screenshots_dir}/02_login_page.png", full_page=True)
            
            try:
                await login_page.fill("input[name='username'], input#username", username)
                await login_page.fill("input[name='password'], input#password", password)
                
                await login_page.screenshot(path=f"{screenshots_dir}/03_prefilled.png", full_page=True)
            except Exception as e:
                logger.warning(f"Could not pre-fill login form: {str(e)}")
            
            active_sessions[session_id] = {
                "playwright": playwright,
                "browser": browser,
                "context": context,
                "page": login_page,
                "company": company,
                "screenshots_dir": screenshots_dir,
                "start_time": time.time(),
                "status": "login_page_opened"
            }
            
            return {
                "success": True,
                "message": "Manual login window opened successfully",
                "sessionId": session_id,
                "company": company
            }
        else:
            logger.warning("No new window detected after clicking login button")
            
            active_sessions[session_id] = {
                "playwright": playwright,
                "browser": browser,
                "context": context,
                "page": page,
                "company": company,
                "screenshots_dir": screenshots_dir,
                "start_time": time.time(),
                "status": "no_login_page"
            }
            
            return {
                "success": False,
                "error": "Could not open login window. Please click the yellow 'Login' button manually.",
                "sessionId": session_id,
                "company": company
            }
    
    except Exception as e:
        logger.error(f"Error starting manual login session: {str(e)}")
        return {
            "success": False,
            "error": f"Error starting manual login session: {str(e)}",
            "sessionId": session_id,
            "company": company
        }

async def complete_manual_login(session_id: str) -> Dict[str, Any]:
    """
    Complete a manual login session by checking if login was successful.
    
    Args:
        session_id: Session ID of the manual login session
        
    Returns:
        dict: Response with status information
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    session = active_sessions[session_id]
    page = session["page"]
    screenshots_dir = session["screenshots_dir"]
    
    try:
        logger.info(f"Completing manual login session {session_id}")
        
        await page.screenshot(path=f"{screenshots_dir}/04_after_manual_login.png", full_page=True)
        
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
                
                await page.screenshot(path=f"{screenshots_dir}/05_dashboard.png", full_page=True)
                
                session["status"] = "login_successful"
                
                return {
                    "success": True,
                    "message": "Manual login completed successfully",
                    "sessionId": session_id
                }
            except Exception:
                continue
        
        logger.warning(f"No dashboard indicators found for session {session_id}")
        
        session["status"] = "login_failed"
        
        return {
            "success": False,
            "error": "Could not verify successful login. Please ensure you are logged in to the DMCE portal.",
            "sessionId": session_id
        }
    
    except Exception as e:
        logger.error(f"Error completing manual login session: {str(e)}")
        
        session["status"] = "error"
        
        return {
            "success": False,
            "error": f"Error completing manual login session: {str(e)}",
            "sessionId": session_id
        }

async def cleanup_session(session_id: str) -> None:
    """
    Clean up a manual login session by closing the browser.
    
    Args:
        session_id: Session ID of the manual login session
    """
    if session_id not in active_sessions:
        return
    
    session = active_sessions[session_id]
    
    try:
        logger.info(f"Cleaning up manual login session {session_id}")
        
        if "browser" in session and session["browser"]:
            await session["browser"].close()
        
        if "playwright" in session and session["playwright"]:
            await session["playwright"].stop()
        
        active_sessions.pop(session_id, None)
    
    except Exception as e:
        logger.error(f"Error cleaning up manual login session: {str(e)}")

async def cleanup_old_sessions(max_age_seconds: int = 3600) -> None:
    """
    Clean up old manual login sessions.
    
    Args:
        max_age_seconds: Maximum age of sessions in seconds before cleanup
    """
    current_time = time.time()
    
    for session_id in list(active_sessions.keys()):
        session = active_sessions[session_id]
        
        if current_time - session["start_time"] > max_age_seconds:
            await cleanup_session(session_id)
