import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.async_api import async_playwright
from app.services.traffic.models.traffic import InvoiceRecord, InvoiceItem
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def test_dmce_headless():
    """
    Headless test for the DMCE workflow with real credentials.
    This will connect to the production DMCE system but will NOT submit any forms.
    It will capture screenshots at each step for verification.
    """
    os.environ["DMCE_PORTAL_URL"] = "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl"
    os.environ["DMCE_USERNAME"] = "crandonzlpr"
    os.environ["DMCE_PASSWORD"] = "perfumes"
    
    screenshots_dir = "/tmp/dmce_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    logger.info("Starting DMCE headless test with real credentials")
    logger.info(f"Screenshots will be saved to {screenshots_dir}")
    
    test_record = InvoiceRecord(
        id=1,
        user_id=1,
        upload_date=datetime.now().isoformat(),
        invoice_number="TEST-DEVIN-001",
        invoice_date=datetime.now().isoformat(),
        client_name="Test Client",
        client_id="TC001",
        movement_type="Exit",  # "Exit" will be translated to "Salida" in the DMCE form
        total_value=100.0,
        total_weight=10.0,
        status="Validated",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        items=[]
    )
    
    test_items = [
        InvoiceItem(
            id=1,
            invoice_id=1,
            tariff_code="3303.00.19",  # Perfume tariff code
            description="TEST PERFUME - DO NOT PROCESS",
            quantity=1,
            unit="PIECES",
            weight=5.0,
            value=50.0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        ),
        InvoiceItem(
            id=2,
            invoice_id=1,
            tariff_code="3304.99.90",  # Cosmetics tariff code
            description="TEST COSMETIC - DO NOT PROCESS",
            quantity=1,
            unit="PIECES",
            weight=5.0,
            value=50.0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    ]
    
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            logger.info(f"Navigating to DMCE portal: {os.environ['DMCE_PORTAL_URL']}")
            await page.goto(os.environ["DMCE_PORTAL_URL"], wait_until="networkidle", timeout=60000)
            await page.screenshot(path=f"{screenshots_dir}/01_initial_page.png")
            logger.info("✅ Step 1: Navigated to DMCE portal")
            
            logger.info("Clicking login button to access login page")
            try:
                login_button = await page.wait_for_selector("button:has-text('Ingresar')", timeout=30000)
                if login_button:
                    await login_button.click()
                    await page.wait_for_load_state("networkidle", timeout=30000)
                    await page.screenshot(path=f"{screenshots_dir}/02_after_login_button.png")
                    logger.info("✅ Step 2: Clicked login button")
                else:
                    logger.error("❌ Step 2: Login button not found")
            except Exception as e:
                logger.error(f"❌ Step 2: Error clicking login button: {str(e)}")
                await page.screenshot(path=f"{screenshots_dir}/02_error_login_button.png")
            
            logger.info(f"Entering username: {os.environ['DMCE_USERNAME']}")
            try:
                await page.fill("input[name='username']", os.environ["DMCE_USERNAME"])
                logger.info("Entering password")
                await page.fill("input[name='password']", os.environ["DMCE_PASSWORD"])
                await page.screenshot(path=f"{screenshots_dir}/03_credentials_entered.png")
                logger.info("✅ Step 3: Entered credentials")
            except Exception as e:
                logger.error(f"❌ Step 3: Error entering credentials: {str(e)}")
                await page.screenshot(path=f"{screenshots_dir}/03_error_credentials.png")
            
            logger.info("Submitting login form")
            try:
                await page.click("button[type='submit']")
                await page.wait_for_load_state("networkidle", timeout=60000)
                await page.screenshot(path=f"{screenshots_dir}/04_after_login_submit.png")
                logger.info("✅ Step 4: Submitted login form")
            except Exception as e:
                logger.error(f"❌ Step 4: Error submitting login form: {str(e)}")
                await page.screenshot(path=f"{screenshots_dir}/04_error_login_submit.png")
            
            logger.info("Checking for dashboard")
            dashboard_found = False
            dashboard_selectors = [
                ".dashboard-container", 
                "#dashboard", 
                ".main-content",
                "text=Bienvenido",
                "text=DMCE",
                ".menu-container",
                "#main-menu"
            ]
            
            for selector in dashboard_selectors:
                try:
                    dashboard_element = await page.wait_for_selector(selector, timeout=5000)
                    if dashboard_element:
                        dashboard_found = True
                        logger.info(f"✅ Step 5: Dashboard found with selector: {selector}")
                        break
                except:
                    continue
            
            if not dashboard_found:
                logger.error("❌ Step 5: Dashboard not found")
            
            logger.info("Clicking 'Create New DMCE' button")
            create_button_found = False
            create_button_selectors = [
                "button:has-text('Crear Nueva DMCE')",
                "a:has-text('Crear Nueva DMCE')",
                "button:has-text('Create New DMCE')",
                "a:has-text('Create New DMCE')",
                "button:has-text('Nueva DMCE')",
                "a:has-text('Nueva DMCE')"
            ]
            
            for selector in create_button_selectors:
                try:
                    create_button = await page.wait_for_selector(selector, timeout=5000)
                    if create_button:
                        await create_button.click()
                        create_button_found = True
                        logger.info(f"✅ Step 6: Create button found with selector: {selector}")
                        break
                except:
                    continue
            
            if not create_button_found:
                logger.error("❌ Step 6: Create button not found")
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.screenshot(path=f"{screenshots_dir}/05_after_create_button.png")
            
            logger.info("Checking for form")
            form_found = False
            form_header_selectors = [
                ".form-header",
                "#header-section",
                "form",
                "input[name='date']",
                "input[name='client_number']"
            ]
            
            for selector in form_header_selectors:
                try:
                    form_header = await page.wait_for_selector(selector, timeout=5000)
                    if form_header:
                        form_found = True
                        logger.info(f"✅ Step 7: Form found with selector: {selector}")
                        break
                except:
                    continue
            
            if not form_found:
                logger.error("❌ Step 7: Form not found")
            
            logger.info("Attempting to fill header section")
            await page.screenshot(path=f"{screenshots_dir}/06_form_header.png")
            
            logger.info("Checking for detail tab")
            detail_tab_found = False
            detail_tab_selectors = [
                "button:has-text('Detalle')",
                "a:has-text('Detalle')",
                "button:has-text('Detail')",
                "a:has-text('Detail')",
                "#detail-tab"
            ]
            
            for selector in detail_tab_selectors:
                try:
                    detail_tab = await page.wait_for_selector(selector, timeout=5000)
                    if detail_tab:
                        detail_tab_found = True
                        logger.info(f"✅ Step 9: Detail tab found with selector: {selector}")
                        break
                except:
                    continue
            
            if not detail_tab_found:
                logger.error("❌ Step 9: Detail tab not found")
            else:
                await page.screenshot(path=f"{screenshots_dir}/07_detail_tab.png")
            
            logger.info("Checking for totals tab")
            totals_tab_found = False
            totals_tab_selectors = [
                "button:has-text('Totales')",
                "a:has-text('Totales')",
                "button:has-text('Totals')",
                "a:has-text('Totals')",
                "#totals-tab"
            ]
            
            for selector in totals_tab_selectors:
                try:
                    totals_tab = await page.wait_for_selector(selector, timeout=5000)
                    if totals_tab:
                        totals_tab_found = True
                        logger.info(f"✅ Step 10: Totals tab found with selector: {selector}")
                        break
                except:
                    continue
            
            if not totals_tab_found:
                logger.error("❌ Step 10: Totals tab not found")
            else:
                await page.screenshot(path=f"{screenshots_dir}/08_totals_tab.png")
            
            logger.info("Checking for movement type options")
            movement_type_found = False
            movement_type_selectors = [
                "input[name='movement_type'][value='Salida']",
                "input[value='Salida']",
                "input[name='mode'][value='Salida']",
                "input[id='salida']"
            ]
            
            for selector in movement_type_selectors:
                try:
                    movement_type_field = await page.wait_for_selector(selector, timeout=5000)
                    if movement_type_field:
                        movement_type_found = True
                        logger.info(f"✅ Step 11: Movement type found with selector: {selector}")
                        break
                except:
                    continue
            
            if not movement_type_found:
                logger.error("❌ Step 11: Movement type not found")
            else:
                await page.screenshot(path=f"{screenshots_dir}/09_movement_type.png")
            
            logger.info("Checking for submit button")
            submit_button_found = False
            submit_button_selectors = [
                "button:has-text('Guardar DMCE')",
                "button:has-text('Save DMCE')",
                "button:has-text('Generate Declaration')",
                "button:has-text('Submit')",
                "input[type='submit']"
            ]
            
            for selector in submit_button_selectors:
                try:
                    submit_button = await page.wait_for_selector(selector, timeout=5000)
                    if submit_button:
                        submit_button_found = True
                        logger.info(f"✅ Step 12: Submit button found with selector: {selector}")
                        break
                except:
                    continue
            
            if not submit_button_found:
                logger.error("❌ Step 12: Submit button not found")
            else:
                await page.screenshot(path=f"{screenshots_dir}/10_submit_button.png")
            
            logger.info("Test completed. Closing browser without submitting to production.")
            await browser.close()
            
    except Exception as e:
        logger.error(f"Error during DMCE headless test: {str(e)}")
    
    logger.info("DMCE headless test completed")
    logger.info(f"Screenshots saved to {screenshots_dir}")
    logger.info("Please review the screenshots to verify the workflow implementation")

if __name__ == "__main__":
    asyncio.run(test_dmce_headless())
