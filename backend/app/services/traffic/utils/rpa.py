import logging
import asyncio
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime
import os
from playwright.async_api import async_playwright, Browser, Page, ElementHandle

from app.services.traffic.models.traffic import InvoiceRecord, InvoiceItem
from app.core.config import settings

logger = logging.getLogger(__name__)

class DMCEAutomator:
    """
    Utility for automating interactions with the DMCE portal.
    Uses Playwright for browser automation to fill and submit DMCE forms.
    """
    
    def __init__(self):
        self.dmce_url = settings.DMCE_PORTAL_URL if settings.DMCE_PORTAL_URL else "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl"
        self.username = settings.DMCE_USERNAME
        self.password = settings.DMCE_PASSWORD
        
        logger.info(f"Initialized DMCEAutomator with URL: {self.dmce_url}")
    
    async def submit_to_dmce(
        self, 
        record: InvoiceRecord,
        items: List[InvoiceItem]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Submit a record to the DMCE portal.
        
        Args:
            record: Invoice record to submit
            items: List of invoice items
            
        Returns:
            Tuple of (success, dmce_number, error_message)
        """
        try:
            logger.info(f"Starting DMCE submission for invoice {record.invoice_number}")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    login_success = await self._login_to_dmce(page)
                    if not login_success:
                        await browser.close()
                        return False, None, "Failed to login to DMCE portal"
                    
                    nav_success = await self._navigate_to_form(page, record.movement_type)
                    if not nav_success:
                        await browser.close()
                        return False, None, f"Failed to navigate to {record.movement_type} form"
                    
                    # Step 3: Fill the header section
                    header_success = await self._fill_form_header(page, record)
                    if not header_success:
                        await browser.close()
                        return False, None, "Failed to fill DMCE header"
                    
                    items_success = await self._fill_item_details(page, items)
                    if not items_success:
                        await browser.close()
                        return False, None, "Failed to fill DMCE item details"
                    
                    totals_success = await self._calculate_totals_and_select_mode(page, record)
                    if not totals_success:
                        await browser.close()
                        return False, None, "Failed to calculate totals or select mode"
                    
                    submit_success, dmce_number, error = await self._submit_form(page)
                    
                    await browser.close()
                    return submit_success, dmce_number, error
                    
                except Exception as e:
                    await browser.close()
                    raise e
                
        except Exception as e:
            logger.error(f"Error submitting to DMCE: {str(e)}")
            return False, None, str(e)
    
    async def _login_to_dmce(self, page: Page) -> bool:
        """
        Log in to the DMCE portal using a simplified approach with expect_navigation.
        This approach recognizes that clicking the login button simply navigates the current tab
        to signin.cl, rather than opening a popup or iframe.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            import re
            
            # Navigate to the DMCE portal URL
            logger.info(f"Navigating to DMCE portal: {self.dmce_url}")
            await page.goto(self.dmce_url, wait_until="networkidle")
            await page.screenshot(path="/tmp/dmce_01_portal.png")
            
            logger.info("Clicking login button with expect_navigation")
            try:
                async with page.expect_navigation(
                    url=re.compile(r'.*/signin\.cl\?language=.*'),
                    wait_until='networkidle',
                    timeout=15000
                ):
                    await page.click("button:has-text('LOGIN'), text=LOGIN, text=Iniciar Sesión")
                
                logger.info(f"✅ Arrived at signin page: {page.url}")
                await page.screenshot(path="/tmp/dmce_02_signin.png")
            except Exception as e:
                logger.error(f"Failed to navigate to signin page: {str(e)}")
                
                login_selectors = [
                    "text=Login",
                    "text=INICIAR SESIÓN",
                    "text=Iniciar Sesión",
                    "a.login-button",
                    ".login-link",
                    ".header-login",
                    "a:has-text('LOGIN')",
                    "a:has-text('Login')",
                    "a:has-text('INICIAR')",
                    "a:has-text('Iniciar')",
                    "button:has-text('Login')",
                    "button:has-text('INICIAR')",
                    "button:has-text('Iniciar')"
                ]
                
                for selector in login_selectors:
                    try:
                        logger.info(f"Trying alternative selector: {selector}")
                        async with page.expect_navigation(
                            url=re.compile(r'.*/signin\.cl\?language=.*'),
                            wait_until='networkidle',
                            timeout=10000
                        ):
                            await page.click(selector)
                        
                        logger.info(f"✅ Arrived at signin page using alternative selector: {page.url}")
                        await page.screenshot(path="/tmp/dmce_02_signin_alternative.png")
                        break
                    except Exception:
                        continue
            
            logger.info(f"Entering username: {self.username}")
            await page.fill("input[name='username'], input#username", self.username)
            
            logger.info("Entering password")
            await page.fill("input[name='password'], input#password", self.password)
            
            await page.screenshot(path="/tmp/dmce_03_before_submit.png")
            
            logger.info("Submitting login form")
            try:
                async with page.expect_navigation(wait_until='networkidle', timeout=15000):
                    await page.click("button:has-text('Sign In'), button[type='submit']")
                
                logger.info(f"✅ Logged in: now at {page.url}")
                await page.screenshot(path="/tmp/dmce_04_dashboard.png")
            except Exception as e:
                logger.error(f"Failed to navigate after login submission: {str(e)}")
                return False
            
            try:
                dashboard_indicators = [
                    "text=Crear Nueva DMCE",
                    "text=Cerrar Sesión",
                    ".dashboard-container", 
                    ".main-container", 
                    ".user-info",
                    "text=Dashboard",
                    "text=Logout",
                    "text=Create New DMCE"
                ]
                
                for indicator in dashboard_indicators:
                    try:
                        element = await page.wait_for_selector(indicator, timeout=2000)
                        if element:
                            logger.info(f"Successfully logged in to DMCE portal (found {indicator})")
                            return True
                    except Exception:
                        continue
                
                logger.error("Could not verify successful login")
                return False
            except Exception as e:
                logger.error(f"Error verifying login: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"Error logging in to DMCE: {str(e)}")
            return False
    
    async def _navigate_to_form(self, page: Page, movement_type: str) -> bool:
        """
        Navigate to the appropriate form based on movement type.
        
        Args:
            page: Playwright page object
            movement_type: "Exit" or "Transfer"
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            logger.info(f"Navigating to {movement_type} form")
            
            await page.click("button:has-text('Crear Nueva DMCE')")
            await page.wait_for_load_state("networkidle")
            
            # Verify form is loaded by checking for header section
            form_header = await page.wait_for_selector(".form-header", timeout=5000)
            if not form_header:
                logger.error("Failed to load DMCE form")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to form: {str(e)}")
            return False
    
    async def _fill_form_header(self, page: Page, record: InvoiceRecord) -> bool:
        """
        Fill the header section of the DMCE form.
        
        Args:
            page: Playwright page object
            record: Invoice record data
            
        Returns:
            True if header filled successfully, False otherwise
        """
        try:
            logger.info(f"Filling header section for invoice {record.invoice_number}")
            
            await page.click("input.date-field")
            await page.fill("input.date-field", record.invoice_date.strftime("%d/%m/%Y"))
            
            await page.fill("input[name='client_number']", record.client_id)
            
            await page.fill("input[name='address']", record.client_name)
            
            await page.fill("input[name='consignee']", record.client_name)
            
            await page.fill("input[name='shipper']", "Shipping Line")
            
            await page.fill("input[name='document']", "B/L")
            
            await page.fill("input[name='brand']", "")
            
            await page.fill("textarea[name='observations']", f"Invoice: {record.invoice_number}")
            
            await page.select_option("select[name='terms']", "FOB")
            
            await page.fill("input[name='freight']", "0.00")
            
            await page.fill("input[name='insurance']", "0.00")
            
            await page.fill("input[name='others']", "0.00")
            
            await page.click("button:has-text('Guardar')")
            await page.wait_for_load_state("networkidle")
            
            logger.info("Successfully filled header section")
            return True
            
        except Exception as e:
            logger.error(f"Error filling header section: {str(e)}")
            return False
            
    async def _fill_item_details(self, page: Page, items: List[InvoiceItem]) -> bool:
        """
        Fill the item details section of the DMCE form.
        
        Args:
            page: Playwright page object
            items: List of invoice items
            
        Returns:
            True if details filled successfully, False otherwise
        """
        try:
            logger.info(f"Filling item details for {len(items)} items")
            
            # Navigate to the Detail tab
            await page.click("button:has-text('Detalle')")
            await page.wait_for_load_state("networkidle")
            
            for item in items:
                logger.info(f"Adding item: {item.description}")
                
                await page.click("button:has-text('Agregar Detalle')")
                
                await page.fill("input[name='tariff_code']", item.tariff_code)
                
                description_field = await page.query_selector("input[name='description']")
                if description_field:
                    await description_field.fill(item.description)
                
                await page.select_option("select[name='unit']", item.unit)
                
                await page.fill("input[name='quantity']", str(item.quantity))
                
                await page.fill("input[name='packages']", str(int(item.quantity)))
                
                await page.fill("input[name='weight']", str(item.weight))
                
                subtotal = await page.wait_for_selector(".subtotal-field")
                
                await page.click("button:has-text('Confirmar')")
            
            logger.info("Successfully filled all item details")
            return True
            
        except Exception as e:
            logger.error(f"Error filling item details: {str(e)}")
            return False
    
    async def _calculate_totals_and_select_mode(self, page: Page, record: InvoiceRecord) -> bool:
        """
        Calculate totals and select movement type.
        
        Args:
            page: Playwright page object
            record: Invoice record data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Calculating totals and selecting movement type")
            
            # Navigate to Totals tab
            await page.click("button:has-text('Totales')")
            await page.wait_for_load_state("networkidle")
            
            await page.click("button:has-text('Calcular Totales')")
            await page.wait_for_load_state("networkidle")
            
            total_field = await page.query_selector(".total-dmce-field")
            if total_field:
                total_value = await total_field.text_content()
                logger.info(f"Total DMCE value: {total_value}")
            
            movement_type = "Salida" if record.movement_type.lower() == "exit" else "Traspaso"
            logger.info(f"Selecting movement type: {movement_type}")
            
            await page.click(f"input[name='movement_type'][value='{movement_type}']")
            
            return True
            
        except Exception as e:
            logger.error(f"Error calculating totals and selecting mode: {str(e)}")
            return False
    
    async def _submit_form(self, page: Page) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Submit the DMCE form and capture the result.
        
        Args:
            page: Playwright page object
            
        Returns:
            Tuple of (success, dmce_number, error_message)
        """
        try:
            logger.info("Submitting DMCE form")
            
            await page.click("button:has-text('Guardar DMCE')")
            await page.wait_for_load_state("networkidle")
            
            success_message = await page.query_selector(".success-message")
            if success_message:
                message_text = await success_message.text_content()
                
                dmce_number = "DMCE-" + message_text.split("DMCE-")[1].split(" ")[0]
                
                logger.info(f"Successfully submitted DMCE. Reference: {dmce_number}")
                return True, dmce_number, None
            else:
                error_message = "No success message found after submission"
                logger.error(error_message)
                return False, None, error_message
            
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            return False, None, str(e)
