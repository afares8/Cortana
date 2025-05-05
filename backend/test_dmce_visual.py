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

async def test_dmce_visual():
    """
    Visual test for the DMCE workflow with real credentials.
    This will connect to the production DMCE system with a visible browser.
    """
    os.environ["DMCE_PORTAL_URL"] = "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl"
    os.environ["DMCE_USERNAME"] = "crandonzlpr"
    os.environ["DMCE_PASSWORD"] = "perfumes"
    
    screenshots_dir = "/tmp/dmce_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    logger.info("Starting DMCE visual test with real credentials")
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
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            logger.info(f"Navigating to DMCE portal: {os.environ['DMCE_PORTAL_URL']}")
            await page.goto(os.environ["DMCE_PORTAL_URL"], wait_until="networkidle", timeout=60000)
            await page.screenshot(path=f"{screenshots_dir}/01_initial_page.png")
            
            logger.info("Clicking login button to access login page")
            login_button = await page.wait_for_selector("button:has-text('Ingresar')", timeout=30000)
            if login_button:
                await login_button.click()
                await page.wait_for_load_state("networkidle", timeout=30000)
                await page.screenshot(path=f"{screenshots_dir}/02_after_login_button.png")
            
            logger.info(f"Entering username: {os.environ['DMCE_USERNAME']}")
            await page.fill("input[name='username']", os.environ["DMCE_USERNAME"])
            
            logger.info("Entering password")
            await page.fill("input[name='password']", os.environ["DMCE_PASSWORD"])
            
            await page.screenshot(path=f"{screenshots_dir}/03_credentials_entered.png")
            
            logger.info("Submitting login form")
            await page.click("button[type='submit']")
            
            await page.wait_for_load_state("networkidle", timeout=60000)
            await page.screenshot(path=f"{screenshots_dir}/04_after_login_submit.png")
            
            logger.info("Please verify login was successful and press Enter to continue...")
            input()
            
            logger.info("Clicking 'Create New DMCE' button")
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
                        logger.info(f"Create button found with selector: {selector}")
                        break
                except:
                    continue
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.screenshot(path=f"{screenshots_dir}/05_after_create_button.png")
            
            logger.info("Please verify form loaded and press Enter to continue...")
            input()
            
            logger.info("Filling header section")
            
            try:
                await page.fill("input[type='date']", test_record.invoice_date.split('T')[0])
                logger.info("Date field filled")
            except:
                logger.warning("Could not fill date field automatically")
                logger.info("Please fill the date field manually and press Enter to continue...")
                input()
            
            field_mappings = [
                {"name": "Client Number", "selectors": ["input[name='client_number']", "#client_number"], "value": test_record.client_id},
                {"name": "Address", "selectors": ["input[name='address']", "#address"], "value": test_record.client_name},
                {"name": "Consignee", "selectors": ["input[name='consignee']", "#consignee"], "value": test_record.client_name},
                {"name": "Shipper", "selectors": ["input[name='shipper']", "#shipper"], "value": "Shipping Line"},
                {"name": "Document", "selectors": ["input[name='document']", "#document"], "value": "B/L"},
                {"name": "Brand", "selectors": ["input[name='brand']", "#brand"], "value": ""},
                {"name": "Observations", "selectors": ["textarea[name='observations']", "#observations"], "value": f"Invoice: {test_record.invoice_number}"}
            ]
            
            for field in field_mappings:
                field_filled = False
                for selector in field["selectors"]:
                    try:
                        await page.fill(selector, field["value"])
                        field_filled = True
                        logger.info(f"{field['name']} field filled")
                        break
                    except:
                        continue
                
                if not field_filled:
                    logger.warning(f"Could not fill {field['name']} field automatically")
            
            try:
                await page.select_option("select[name='terms']", "FOB")
                logger.info("Terms field selected")
            except:
                logger.warning("Could not select terms field automatically")
            
            numeric_field_mappings = [
                {"name": "Freight", "selectors": ["input[name='freight']", "#freight"], "value": "0.00"},
                {"name": "Insurance", "selectors": ["input[name='insurance']", "#insurance"], "value": "0.00"},
                {"name": "Others", "selectors": ["input[name='others']", "#others"], "value": "0.00"}
            ]
            
            for field in numeric_field_mappings:
                field_filled = False
                for selector in field["selectors"]:
                    try:
                        await page.fill(selector, field["value"])
                        field_filled = True
                        logger.info(f"{field['name']} field filled")
                        break
                    except:
                        continue
                
                if not field_filled:
                    logger.warning(f"Could not fill {field['name']} field automatically")
            
            await page.screenshot(path=f"{screenshots_dir}/06_header_filled.png")
            
            logger.info("Please verify header filled correctly and press Enter to continue...")
            input()
            
            logger.info("Saving header")
            save_button_selectors = [
                "button:has-text('Guardar')",
                "button:has-text('Save')",
                "input[type='submit']",
                "button[type='submit']"
            ]
            
            for selector in save_button_selectors:
                try:
                    save_button = await page.wait_for_selector(selector, timeout=5000)
                    if save_button:
                        await save_button.click()
                        logger.info(f"Save button clicked with selector: {selector}")
                        break
                except:
                    continue
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.screenshot(path=f"{screenshots_dir}/07_after_header_save.png")
            
            logger.info("Please verify header saved and press Enter to continue...")
            input()
            
            logger.info("Navigating to Detail tab")
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
                        await detail_tab.click()
                        logger.info(f"Detail tab clicked with selector: {selector}")
                        break
                except:
                    continue
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.screenshot(path=f"{screenshots_dir}/08_detail_tab.png")
            
            logger.info("Please verify detail tab loaded and press Enter to continue...")
            input()
            
            for i, item in enumerate(test_items):
                logger.info(f"Adding item {i+1}: {item.description}")
                
                add_detail_selectors = [
                    "button:has-text('Agregar Detalle')",
                    "button:has-text('Add Detail')",
                    "a:has-text('Agregar Detalle')",
                    "a:has-text('Add Detail')"
                ]
                
                for selector in add_detail_selectors:
                    try:
                        add_detail = await page.wait_for_selector(selector, timeout=5000)
                        if add_detail:
                            await add_detail.click()
                            logger.info(f"Add detail button clicked with selector: {selector}")
                            break
                    except:
                        continue
                
                await page.wait_for_load_state("networkidle", timeout=30000)
                await page.screenshot(path=f"{screenshots_dir}/09_add_detail_{i+1}.png")
                
                item_field_mappings = [
                    {"name": "Tariff Code", "selectors": ["input[name='tariff_code']", "#tariff_code"], "value": item.tariff_code},
                    {"name": "Description", "selectors": ["input[name='description']", "#description"], "value": item.description},
                    {"name": "Quantity", "selectors": ["input[name='quantity']", "#quantity"], "value": str(item.quantity)},
                    {"name": "Packages", "selectors": ["input[name='packages']", "#packages"], "value": str(int(item.quantity))},
                    {"name": "Weight", "selectors": ["input[name='weight']", "#weight"], "value": str(item.weight)}
                ]
                
                for field in item_field_mappings:
                    field_filled = False
                    for selector in field["selectors"]:
                        try:
                            await page.fill(selector, field["value"])
                            field_filled = True
                            logger.info(f"{field['name']} field filled")
                            break
                        except:
                            continue
                    
                    if not field_filled:
                        logger.warning(f"Could not fill {field['name']} field automatically")
                
                try:
                    await page.select_option("select[name='unit']", item.unit)
                    logger.info("Unit field selected")
                except:
                    logger.warning("Could not select unit field automatically")
                
                await page.screenshot(path=f"{screenshots_dir}/10_item_details_{i+1}.png")
                
                logger.info(f"Please verify item {i+1} details filled correctly and press Enter to continue...")
                input()
                
                confirm_button_selectors = [
                    "button:has-text('Confirmar')",
                    "button:has-text('Confirm')",
                    "input[type='submit']",
                    "button[type='submit']"
                ]
                
                for selector in confirm_button_selectors:
                    try:
                        confirm_button = await page.wait_for_selector(selector, timeout=5000)
                        if confirm_button:
                            await confirm_button.click()
                            logger.info(f"Confirm button clicked with selector: {selector}")
                            break
                    except:
                        continue
                
                await page.wait_for_load_state("networkidle", timeout=30000)
                await page.screenshot(path=f"{screenshots_dir}/11_after_item_confirm_{i+1}.png")
                
                logger.info(f"Please verify item {i+1} confirmed and press Enter to continue...")
                input()
            
            logger.info("Navigating to Totals tab")
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
                        await totals_tab.click()
                        logger.info(f"Totals tab clicked with selector: {selector}")
                        break
                except:
                    continue
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.screenshot(path=f"{screenshots_dir}/12_totals_tab.png")
            
            logger.info("Please verify totals tab loaded and press Enter to continue...")
            input()
            
            logger.info("Calculating totals")
            calculate_button_selectors = [
                "button:has-text('Calcular Totales')",
                "button:has-text('Calculate Totals')",
                "a:has-text('Calcular Totales')",
                "a:has-text('Calculate Totals')"
            ]
            
            for selector in calculate_button_selectors:
                try:
                    calculate_button = await page.wait_for_selector(selector, timeout=5000)
                    if calculate_button:
                        await calculate_button.click()
                        logger.info(f"Calculate button clicked with selector: {selector}")
                        break
                except:
                    continue
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.screenshot(path=f"{screenshots_dir}/13_after_calculate_totals.png")
            
            logger.info("Please verify totals calculated and press Enter to continue...")
            input()
            
            movement_type = "Salida" if test_record.movement_type.lower() == "exit" else "Traspaso"
            logger.info(f"Selecting movement type: {movement_type}")
            
            movement_type_selectors = [
                f"input[name='movement_type'][value='{movement_type}']",
                f"input[value='{movement_type}']",
                f"input[name='mode'][value='{movement_type}']",
                f"input[id='{movement_type.lower()}']"
            ]
            
            movement_type_selected = False
            for selector in movement_type_selectors:
                try:
                    movement_type_field = await page.wait_for_selector(selector, timeout=5000)
                    if movement_type_field:
                        await movement_type_field.click()
                        movement_type_selected = True
                        logger.info(f"Movement type selected with selector: {selector}")
                        break
                except:
                    continue
            
            if not movement_type_selected:
                logger.warning(f"Could not select movement type automatically")
                logger.info("Please select the movement type manually and press Enter to continue...")
                input()
            
            await page.screenshot(path=f"{screenshots_dir}/14_movement_type_selected.png")
            
            logger.info("Please verify movement type selected and press Enter to continue...")
            input()
            
            logger.info("Submitting form")
            submit_button_selectors = [
                "button:has-text('Guardar DMCE')",
                "button:has-text('Save DMCE')",
                "button:has-text('Generate Declaration')",
                "button:has-text('Submit')",
                "input[type='submit']"
            ]
            
            logger.info("Do you want to actually submit the form? (y/n)")
            submit_choice = input().lower()
            
            if submit_choice == 'y':
                for selector in submit_button_selectors:
                    try:
                        submit_button = await page.wait_for_selector(selector, timeout=5000)
                        if submit_button:
                            await submit_button.click()
                            logger.info(f"Submit button clicked with selector: {selector}")
                            break
                    except:
                        continue
                
                await page.wait_for_load_state("networkidle", timeout=30000)
                await page.screenshot(path=f"{screenshots_dir}/15_after_submit.png")
                
                logger.info("Please verify submission result and press Enter to continue...")
                input()
            else:
                logger.info("Skipping actual submission as requested")
            
            logger.info("Test completed. Closing browser...")
            await browser.close()
            
    except Exception as e:
        logger.error(f"Error during DMCE visual test: {str(e)}")
    
    logger.info("DMCE visual test completed")
    logger.info(f"Screenshots saved to {screenshots_dir}")

if __name__ == "__main__":
    asyncio.run(test_dmce_visual())
