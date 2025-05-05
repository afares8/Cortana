import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.traffic.utils.rpa import DMCEAutomator
from app.services.traffic.models.traffic import InvoiceRecord, InvoiceItem
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def test_login_with_mocks():
    """Test the login functionality of the DMCEAutomator using mocks."""
    
    os.environ["DMCE_PORTAL_URL"] = "https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl"
    os.environ["DMCE_USERNAME"] = "test_user"
    os.environ["DMCE_PASSWORD"] = "test_password"
    
    logger.info("Starting RPA login test with mocks")
    
    mock_page = AsyncMock()
    mock_selector = AsyncMock()
    
    mock_page.wait_for_selector.return_value = mock_selector
    mock_page.goto = AsyncMock()
    mock_selector.click = AsyncMock()
    
    automator = DMCEAutomator()
    
    logger.info("Testing login with valid credentials")
    login_success = await automator._login_to_dmce(mock_page)
    
    mock_page.goto.assert_called_once_with(automator.dmce_url, wait_until="networkidle")
    mock_page.wait_for_selector.assert_any_call("button:has-text('Ingresar')", timeout=10000)
    mock_page.fill.assert_any_call("input[name='username']", automator.username)
    mock_page.fill.assert_any_call("input[name='password']", automator.password)
    
    if login_success:
        logger.info("✅ Login test passed: Successfully logged in to DMCE portal")
    else:
        logger.error("❌ Login test failed: Could not log in to DMCE portal")
    
    logger.info("RPA login test with mocks completed")

async def test_full_submission_with_mocks():
    """Test the full DMCE submission process using mocks."""
    
    logger.info("Starting full DMCE submission test with mocks")
    
    with patch('playwright.async_api.async_playwright') as mock_playwright:
        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_selector = AsyncMock()
        
        mock_page.wait_for_selector.return_value = mock_selector
        mock_page.query_selector.return_value = mock_selector
        mock_selector.text_content.return_value = "DMCE-20250505-12345 created successfully"
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        
        automator = DMCEAutomator()
        
        test_record = InvoiceRecord(
            id=1,
            user_id=1,
            upload_date=datetime.now().isoformat(),
            invoice_number="TEST-123",
            invoice_date=datetime.now().isoformat(),
            client_name="Test Client",
            client_id="TC001",
            movement_type="Exit",
            total_value=1000.0,
            total_weight=100.0,
            status="Validated",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            items=[]
        )
        
        test_items = [
            InvoiceItem(
                id=1,
                invoice_id=1,
                tariff_code="8471.30.00",
                description="Computer Equipment",
                quantity=10,
                unit="PIECES",
                weight=50.0,
                value=500.0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            InvoiceItem(
                id=2,
                invoice_id=1,
                tariff_code="8517.12.00",
                description="Mobile Phones",
                quantity=5,
                unit="PIECES",
                weight=50.0,
                value=500.0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        ]
        
        success, dmce_number, error = await automator.submit_to_dmce(test_record, test_items)
        
        if success:
            logger.info(f"✅ DMCE automation test passed. Reference: {dmce_number}")
        else:
            logger.error(f"❌ DMCE automation test failed: {error}")
        
    logger.info("Full DMCE submission test completed")

if __name__ == "__main__":
    asyncio.run(test_login_with_mocks())
    asyncio.run(test_full_submission_with_mocks())
