const { firefox } = require('playwright');
const { randomInt } = require('crypto');
const fs = require('fs');
const path = require('path');
const { getDMCECredentials } = require('./credential_handler');

/**
 * DMCE Portal Full Process Automation Script
 * 
 * This script automates the complete DMCE process:
 * 1. Login to the DMCE portal
 * 2. Navigate to "Crear Declaración"
 * 3. Fill all form sections (A-E)
 * 4. Submit the declaration
 * 5. Download the PDF
 * 6. Logout
 */
(async () => {
  const dirs = ['./videos', './screenshots', './logs', './downloads'];
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  });
  
  console.log('Starting DMCE full process automation');
  
  const browser = await firefox.launch({
    headless: false,
    args: ['-private'],
  });
  
  const context = await browser.newContext({
    locale: 'es-PA',
    timezoneId: 'America/Panama',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 },
    recordVideo: { dir: './videos/' },
    recordTrace: { snapshots: true, screenshots: true },
    acceptDownloads: true
  });
  
  context.on('request', request => {
    console.log(`>> Request: ${request.method()} ${request.url()}`);
  });
  
  context.on('response', response => {
    const status = response.status();
    if (status >= 400) {
      console.log(`!! Error Response: ${status} ${response.url()}`);
    } else {
      console.log(`<< Response: ${status} ${response.url()}`);
    }
  });
  
  await context.tracing.start({ screenshots: true, snapshots: true });
  const page = await context.newPage();
  let popup;
  
  try {
    console.log('Step 1: Navigating to login page');
    await page.goto('https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl?language=es', { 
      timeout: 30000,
      waitUntil: 'networkidle' 
    });
    console.log('Loaded initial login page');
    
    try {
      await page.screenshot({ 
        path: './screenshots/initial_page.png',
        timeout: 5000 
      });
    } catch (error) {
      console.log(`Warning: Screenshot timeout for initial_page.png: ${error.message}`);
    }

    console.log('Opening login popup');
    const loginBtn = await page.waitForSelector('a.login-btn', { timeout: 20000 });
    const box = await loginBtn.boundingBox();
    
    await page.mouse.move(
      randomInt(Math.floor(box.x), Math.floor(box.x + box.width)),
      randomInt(Math.floor(box.y), Math.floor(box.y + box.height)),
      { steps: randomInt(10, 25) }
    );
    
    await page.waitForTimeout(randomInt(500, 1200));
    
    const [popupPromise] = await Promise.all([
      page.waitForEvent('popup', { timeout: 20000 }),
      loginBtn.click()
    ]);
    
    popup = await popupPromise;
    await popup.waitForLoadState('networkidle');
    console.log('Popup URL:', popup.url());
    
    try {
      await popup.screenshot({ 
        path: './screenshots/login_popup.png',
        timeout: 5000 
      });
    } catch (error) {
      console.log(`Warning: Screenshot timeout for login_popup.png: ${error.message}`);
    }

    console.log('Extracting form fields and submitting credentials');
    
    const hiddenData = await popup.$$eval('form input[type="hidden"]', els =>
      els.reduce((m, e) => ({ ...m, [e.name]: e.value }), {})
    );
    
    console.log('Hidden form fields:', Object.keys(hiddenData));
    
    const credentials = getDMCECredentials();
    
    const payload = {
      ...hiddenData,
      j_username: credentials.username,
      j_password: credentials.password
    };
    
    await popup.type('#j_username', payload.j_username, { delay: randomInt(100, 200) });
    await popup.type('#j_password', payload.j_password, { delay: randomInt(100, 200) });
    await popup.mouse.wheel(0, randomInt(100, 300));
    console.log('Filled credentials');
    
    await Promise.all([
      popup.waitForNavigation({ timeout: 30000 }),
      popup.evaluate(data => {
        const form = document.querySelector('form');
        Object.entries(data).forEach(([k, v]) => {
          const input = form.querySelector(`[name="${k}"]`);
          if (input) input.value = v;
        });
        form.submit();
      }, payload)
    ]);
    
    console.log('Post-login URL:', popup.url());
    
    try {
      await popup.screenshot({ 
        path: './screenshots/post_login.png',
        timeout: 5000 
      });
    } catch (error) {
      console.log(`Warning: Screenshot timeout for post_login.png: ${error.message}`);
    }
    
    if (popup.url().includes('login_error')) {
      throw new Error('Login failed: ' + popup.url());
    }
    
    console.log('Waiting for dashboard to load');
    
    await popup.waitForFunction(() => {
      return document.readyState === 'complete' && 
             !document.querySelector('body[style*="display: none"]') &&
             document.body.offsetHeight > 0;
    }, { timeout: 30000 });
    
    console.log('Dashboard loaded');
    
    try {
      await popup.screenshot({ 
        path: './screenshots/dashboard_loaded.png',
        timeout: 5000 
      });
    } catch (error) {
      console.log(`Warning: Screenshot timeout for dashboard_loaded.png: ${error.message}`);
    }
    
    const currentUrl = popup.url();
    if (!currentUrl.includes('dashboard')) {
      console.log(`Warning: Expected dashboard URL, but got: ${currentUrl}`);
      console.log('Continuing with process...');
    }
    
    console.log('Step 2: Navigating to "Crear Declaración"');
    
    try {
      const declMenu = await popup.waitForSelector('a:text("Declaración")', { 
        timeout: 10000,
        state: 'visible' 
      });
      await declMenu.click();
      console.log('Clicked on "Declaración" menu');
    } catch (error) {
      console.error('Error finding "Declaración" menu:', error);
      await popup.screenshot({ path: './screenshots/declaration_menu_error.png', fullPage: true });
      throw new Error('Could not find "Declaración" menu');
    }
    
    try {
      const createDecl = await popup.waitForSelector('a:text("Crear Declaración")', { 
        timeout: 5000,
        state: 'visible' 
      });
      await createDecl.click();
      console.log('Clicked on "Crear Declaración"');
    } catch (error) {
      console.error('Error finding "Crear Declaración" link:', error);
      await popup.screenshot({ path: './screenshots/crear_declaration_error.png', fullPage: true });
      throw new Error('Could not find "Crear Declaración" link');
    }
    
    try {
      await popup.waitForSelector('#crearDeclaracionForm', { timeout: 10000 });
      console.log('Declaration form loaded');
      await popup.screenshot({ path: './screenshots/declaration_form.png' });
    } catch (error) {
      console.error('Error finding declaration form:', error);
      await popup.screenshot({ path: './screenshots/form_load_error.png', fullPage: true });
      throw new Error('Could not find declaration form');
    }
    
    console.log('Step 3: Filling Section A - Datos de la Declaración');
    
    try {
      await popup.fill('#inputFactura', process.env.DMCE_INVOICE_ID || '');
      console.log('Filled Invoice ID');
    } catch (error) {
      console.error('Error filling Invoice ID:', error);
      await popup.screenshot({ path: './screenshots/invoice_id_error.png' });
    }
    
    try {
      await popup.fill('#inputFechaDeclaracion', process.env.DMCE_DATE || '');
      console.log('Filled Declaration Date');
    } catch (error) {
      console.error('Error filling Declaration Date:', error);
      await popup.screenshot({ path: './screenshots/date_error.png' });
    }
    
    try {
      await popup.fill('#inputCliente', process.env.DMCE_CUSTOMER_CODE || '');
      console.log('Filled Customer Code');
    } catch (error) {
      console.error('Error filling Customer Code:', error);
      await popup.screenshot({ path: './screenshots/customer_code_error.png' });
    }
    
    console.log('Step 4: Filling Section B - Datos de la Mercancía');
    
    try {
      await popup.fill('input[name="descripcion"]', process.env.DMCE_GOODS_DESCRIPTION || '');
      console.log('Filled Goods Description');
    } catch (error) {
      console.error('Error filling Goods Description:', error);
      await popup.screenshot({ path: './screenshots/description_error.png' });
    }
    
    try {
      await popup.fill('input[name="cantidad"]', process.env.DMCE_QUANTITY || '');
      console.log('Filled Quantity');
    } catch (error) {
      console.error('Error filling Quantity:', error);
      await popup.screenshot({ path: './screenshots/quantity_error.png' });
    }
    
    try {
      await popup.fill('input[name="pesoKg"]', process.env.DMCE_WEIGHT_KG || '');
      console.log('Filled Weight');
    } catch (error) {
      console.error('Error filling Weight:', error);
      await popup.screenshot({ path: './screenshots/weight_error.png' });
    }
    
    try {
      await popup.fill('input[name="volumenM3"]', process.env.DMCE_VOLUME_M3 || '');
      console.log('Filled Volume');
    } catch (error) {
      console.error('Error filling Volume:', error);
      await popup.screenshot({ path: './screenshots/volume_error.png' });
    }
    
    console.log('Step 5: Filling Section C - Transporte');
    
    try {
      await popup.selectOption('#selectTransporte', process.env.DMCE_TRANSPORT_TYPE || '');
      console.log('Selected Transport Type');
    } catch (error) {
      console.error('Error selecting Transport Type:', error);
      await popup.screenshot({ path: './screenshots/transport_type_error.png' });
    }
    
    if (process.env.DMCE_TRANSPORT_TYPE === 'AIR') {
      try {
        await popup.fill('#inputVuelo', process.env.DMCE_FLIGHT_NUMBER || '');
        console.log('Filled Flight Number');
      } catch (error) {
        console.error('Error filling Flight Number:', error);
        await popup.screenshot({ path: './screenshots/flight_number_error.png' });
      }
      
      try {
        await popup.fill('#inputTransportista', process.env.DMCE_CARRIER_NAME || '');
        console.log('Filled Carrier Name');
      } catch (error) {
        console.error('Error filling Carrier Name:', error);
        await popup.screenshot({ path: './screenshots/carrier_name_error.png' });
      }
    }
    
    console.log('Step 6: Filling Section D - Declaración Aduanera');
    
    try {
      await popup.fill('#inputHsCode', process.env.DMCE_HS_CODE || '');
      console.log('Filled HS Code');
    } catch (error) {
      console.error('Error filling HS Code:', error);
      await popup.screenshot({ path: './screenshots/hs_code_error.png' });
    }
    
    try {
      await popup.fill('input[name="paisOrigen"]', process.env.DMCE_ORIGIN_COUNTRY || '');
      console.log('Filled Origin Country');
    } catch (error) {
      console.error('Error filling Origin Country:', error);
      await popup.screenshot({ path: './screenshots/origin_country_error.png' });
    }
    
    try {
      await popup.fill('input[name="paisDestino"]', process.env.DMCE_DESTINATION_COUNTRY || '');
      console.log('Filled Destination Country');
    } catch (error) {
      console.error('Error filling Destination Country:', error);
      await popup.screenshot({ path: './screenshots/destination_country_error.png' });
    }
    
    try {
      await popup.fill('input[name="valorDeclarado"]', process.env.DMCE_DECLARED_VALUE || '');
      console.log('Filled Declared Value');
    } catch (error) {
      console.error('Error filling Declared Value:', error);
      await popup.screenshot({ path: './screenshots/declared_value_error.png' });
    }
    
    try {
      await popup.selectOption('#selectMoneda', process.env.DMCE_VALUE_CURRENCY || '');
      console.log('Selected Currency');
    } catch (error) {
      console.error('Error selecting Currency:', error);
      await popup.screenshot({ path: './screenshots/currency_error.png' });
    }
    
    console.log('Step 7: Filling Section E - Documentos Adjuntos');
    
    if (process.env.DMCE_COMMERCIAL_INVOICE_PATH) {
      try {
        const invoicePath = process.env.DMCE_COMMERCIAL_INVOICE_PATH;
        await popup.setInputFiles('input#uploadFacturaComercial', invoicePath);
        console.log('Uploaded Commercial Invoice');
      } catch (error) {
        console.error('Error uploading Commercial Invoice:', error);
        await popup.screenshot({ path: './screenshots/invoice_upload_error.png' });
      }
    }
    
    if (process.env.DMCE_PACKING_LIST_PATH) {
      try {
        const packingListPath = process.env.DMCE_PACKING_LIST_PATH;
        await popup.setInputFiles('input#uploadPackingList', packingListPath);
        console.log('Uploaded Packing List');
      } catch (error) {
        console.error('Error uploading Packing List:', error);
        await popup.screenshot({ path: './screenshots/packing_list_upload_error.png' });
      }
    }
    
    console.log('Step 8: Submitting form and capturing transaction ID');
    
    try {
      const submitBtn = await popup.waitForSelector('#submitDeclarationBtn', { timeout: 10000 });
      await submitBtn.click();
      console.log('Clicked submit button');
    } catch (error) {
      console.error('Error finding submit button:', error);
      await popup.screenshot({ path: './screenshots/submit_button_error.png', fullPage: true });
      throw new Error('Could not find submit button');
    }
    
    try {
      await popup.waitForSelector('#lblTransactionId', { timeout: 30000 });
      console.log('Declaration submitted successfully');
      await popup.screenshot({ path: './screenshots/declaration_submitted.png' });
    } catch (error) {
      console.error('Error finding transaction ID:', error);
      await popup.screenshot({ path: './screenshots/transaction_id_error.png', fullPage: true });
      throw new Error('Could not find transaction ID');
    }
    
    let transactionId;
    try {
      transactionId = await popup.$eval('#lblTransactionId', el => el.textContent.trim());
      console.log(`DMCE Transaction ID: ${transactionId}`);
      
      fs.writeFileSync('./logs/transaction_id.txt', transactionId);
    } catch (error) {
      console.error('Error capturing transaction ID:', error);
      await popup.screenshot({ path: './screenshots/transaction_id_capture_error.png' });
    }
    
    try {
      const downloadPromise = popup.waitForEvent('download');
      const dlBtn = await popup.waitForSelector('#downloadDeclarationPdf', { timeout: 10000 });
      await dlBtn.click();
      console.log('Clicked download button');
      
      const download = await downloadPromise;
      const downloadPath = path.join(process.env.DMCE_DOWNLOAD_DIR || './downloads', `declaration_${transactionId || 'unknown'}.pdf`);
      await download.saveAs(downloadPath);
      console.log(`PDF downloaded to: ${downloadPath}`);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      await popup.screenshot({ path: './screenshots/pdf_download_error.png', fullPage: true });
    }
    
    try {
      const screenshotPath = path.join(process.env.DMCE_DOWNLOAD_DIR || './screenshots', `declaration_${transactionId || 'unknown'}.png`);
      await popup.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`Audit screenshot saved to: ${screenshotPath}`);
    } catch (error) {
      console.error('Error taking audit screenshot:', error);
    }
    
    console.log('Step 9: Logging out');
    
    try {
      const logoutLink = await popup.waitForSelector('a:text("Cerrar sesión")', { timeout: 10000 });
      await logoutLink.click();
      console.log('Clicked logout link');
      
      await popup.waitForURL(url => url.includes('/signin.cl'), { timeout: 10000 });
      console.log('Logged out successfully');
      await popup.screenshot({ path: './screenshots/logout_success.png' });
    } catch (error) {
      console.error('Error during logout:', error);
      await popup.screenshot({ path: './screenshots/logout_error.png', fullPage: true });
    }
    
    console.log('DMCE full process automation completed successfully');
    
  } catch (error) {
    console.error('Error during automation:', error);
    
    if (popup) {
      try {
        await popup.screenshot({ 
          path: './screenshots/error_state.png',
          timeout: 5000,
          fullPage: true
        });
      } catch (screenshotError) {
        console.log(`Warning: Screenshot timeout for error_state.png: ${screenshotError.message}`);
      }
      
      console.log('Current URL at error:', popup.url());
      
      try {
        const html = await popup.content();
        fs.writeFileSync('./logs/error_page.html', html);
      } catch (contentError) {
        console.log(`Warning: Error getting page content: ${contentError.message}`);
      }
    } else if (page) {
      try {
        await page.screenshot({ 
          path: './screenshots/error_state.png',
          timeout: 5000,
          fullPage: true
        });
      } catch (screenshotError) {
        console.log(`Warning: Screenshot timeout for error_state.png: ${screenshotError.message}`);
      }
    }
  } finally {
    await context.tracing.stop({ path: 'trace.zip' });
    console.log('Trace saved to trace.zip');
    
    await browser.close();
    console.log('Browser closed');
  }
})();
