const { firefox } = require('playwright');
const { randomInt } = require('crypto');
const fs = require('fs');
const path = require('path');
const { getDMCECredentials, getDMCEDeclarationData, validateDMCEEnvironment } = require('./credential_handler');

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
  
  if (!validateDMCEEnvironment()) {
    console.error('Environment validation failed. Please check your .env file.');
    process.exit(1);
  }
  
  const declarationData = getDMCEDeclarationData();
  console.log('Environment variables validated successfully');
  
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
    
    let dashboardLoaded = false;
    let retryCount = 0;
    const maxRetries = 3;
    const timeout = 60000; // Increased timeout to 60 seconds
    
    while (!dashboardLoaded && retryCount < maxRetries) {
      try {
        console.log(`Dashboard loading attempt ${retryCount + 1}/${maxRetries}`);
        
        await Promise.race([
          popup.waitForFunction(() => {
            return document.readyState === 'complete' && 
                  document.body.offsetHeight > 0;
          }, { timeout: timeout / maxRetries }),
          
          popup.waitForSelector('a:text("Declaración"), a:text("Factura"), a:text("Consulta"), nav, .menu, .navbar', { 
            timeout: timeout / maxRetries,
            state: 'visible' 
          }),
          
          popup.waitForSelector('iframe', { 
            timeout: timeout / maxRetries,
            state: 'visible' 
          })
        ]);
        
        dashboardLoaded = true;
        console.log('Dashboard loaded successfully');
        
      } catch (error) {
        retryCount++;
        console.log(`Dashboard loading attempt ${retryCount} failed: ${error.message}`);
        
        if (retryCount < maxRetries) {
          console.log(`Waiting 5 seconds before retry ${retryCount + 1}...`);
          await popup.waitForTimeout(5000);
          
          await popup.screenshot({ 
            path: `./screenshots/dashboard_loading_retry_${retryCount}.png`,
            fullPage: true
          });
        } else {
          console.log('Maximum retries reached. Continuing with best effort...');
        }
      }
    }
    
    console.log('Dashboard loading phase complete');
    
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
    
    console.log('Checking for iframes in the dashboard...');
    const iframeCount = await popup.$$eval('iframe', iframes => iframes.length);
    console.log(`Found ${iframeCount} iframes in the dashboard`);
    
    if (iframeCount > 0) {
      console.log('Attempting to access iframe content...');
      
      const iframeHandles = await popup.$$('iframe');
      
      for (let i = 0; i < iframeHandles.length; i++) {
        try {
          console.log(`Accessing iframe ${i + 1}/${iframeCount}`);
          
          const frame = await iframeHandles[i].contentFrame();
          
          if (frame) {
            console.log(`Successfully accessed iframe ${i + 1}`);
            
            try {
              await frame.screenshot({ 
                path: `./screenshots/iframe_${i + 1}_content.png`,
                fullPage: true 
              });
            } catch (screenshotError) {
              console.log(`Warning: Screenshot error for iframe ${i + 1}: ${screenshotError.message}`);
            }
            
            try {
              const frameContent = await frame.content();
              fs.writeFileSync(`./logs/iframe_${i + 1}_content.html`, frameContent);
            } catch (contentError) {
              console.log(`Warning: Error getting content of iframe ${i + 1}: ${contentError.message}`);
            }
            
            try {
              console.log(`Searching for Declaración menu in iframe ${i + 1}...`);
              
              const frameSelectors = [
                'text="Declaración"',
                'a:has-text("Declaración")',
                '.menu a:has-text("Declaración")',
                'nav a:has-text("Declaración")',
                'div.menu-item:has-text("Declaración")',
                '[role="menuitem"]:has-text("Declaración")'
              ];
              
              for (const selector of frameSelectors) {
                try {
                  const declaracionElement = await frame.$(selector);
                  
                  if (declaracionElement) {
                    console.log(`Found "Declaración" menu in iframe ${i + 1} with selector: ${selector}`);
                    await declaracionElement.click();
                    console.log('Clicked on "Declaración" menu in iframe');
                    await popup.waitForTimeout(2000);
                    await popup.screenshot({ 
                      path: './screenshots/after_declaration_menu_click_iframe.png',
                      fullPage: true 
                    });
                    
                    const crearSelectors = [
                      'text="Crear Declaración"',
                      'a:has-text("Crear Declaración")',
                      'a:has-text("Nueva Declaración")',
                      'a[href*="crear"]',
                      'button:has-text("Crear")'
                    ];
                    
                    for (const crearSelector of crearSelectors) {
                      try {
                        const crearElement = await frame.$(crearSelector);
                        
                        if (crearElement) {
                          console.log(`Found "Crear Declaración" link in iframe with selector: ${crearSelector}`);
                          await crearElement.click();
                          console.log('Clicked on "Crear Declaración" link in iframe');
                          await popup.waitForTimeout(2000);
                          await popup.screenshot({ 
                            path: './screenshots/after_crear_declaration_click_iframe.png',
                            fullPage: true 
                          });
                          
                          break;
                        }
                      } catch (crearError) {
                        console.log(`Error with selector ${crearSelector} in iframe ${i + 1}: ${crearError.message}`);
                      }
                    }
                    
                    break; // Break out of the selector loop if we found and clicked Declaración
                  }
                } catch (selectorError) {
                  console.log(`Error with selector ${selector} in iframe ${i + 1}: ${selectorError.message}`);
                }
              }
              
              const clickableElements = await frame.$$eval('a, button', elements => {
                return elements.map(el => ({
                  tagName: el.tagName,
                  text: el.textContent.trim(),
                  id: el.id,
                  className: el.className,
                  href: el.href || null
                })).filter(el => el.text.length > 0);
              });
              
              fs.writeFileSync(`./logs/iframe_${i + 1}_clickable_elements.json`, JSON.stringify(clickableElements, null, 2));
              console.log(`Found ${clickableElements.length} clickable elements in iframe ${i + 1}`);
              
              const potentialMenuItems = clickableElements.filter(el => 
                el.text.toLowerCase().includes('declaraci') || 
                el.text.toLowerCase().includes('declar') ||
                (el.href && (el.href.includes('declaracion') || el.href.includes('declar')))
              );
              
              if (potentialMenuItems.length > 0) {
                console.log(`Found ${potentialMenuItems.length} potential Declaración menu items in iframe ${i + 1}`);
                console.log('Potential menu items:', JSON.stringify(potentialMenuItems, null, 2));
                
                try {
                  const menuSelector = potentialMenuItems[0].id ? 
                    `#${potentialMenuItems[0].id}` : 
                    `text="${potentialMenuItems[0].text}"`;
                  
                  const menuElement = await frame.$(menuSelector);
                  
                  if (menuElement) {
                    console.log(`Clicking potential menu item: ${menuSelector}`);
                    await menuElement.click();
                    console.log('Clicked on potential Declaración menu item');
                    await popup.waitForTimeout(2000);
                    await popup.screenshot({ 
                      path: './screenshots/after_potential_menu_click.png',
                      fullPage: true 
                    });
                  }
                } catch (menuClickError) {
                  console.log(`Error clicking potential menu item: ${menuClickError.message}`);
                }
              }
            } catch (frameSearchError) {
              console.log(`Error searching in iframe ${i + 1}: ${frameSearchError.message}`);
            }
          } else {
            console.log(`Could not access content of iframe ${i + 1}`);
          }
        } catch (iframeError) {
          console.log(`Error accessing iframe ${i + 1}: ${iframeError.message}`);
        }
      }
    }
    
    console.log('Step 2: Navigating to "Crear Declaración"');
    
    await popup.screenshot({ 
      path: './screenshots/pre_navigation_dashboard.png',
      fullPage: true 
    });
    
    console.log('Using direct JavaScript evaluation to interact with the dashboard');
    
    try {
      const clickedDeclaracion = await popup.evaluate(() => {
        function findElementsByText(text, elements) {
          const results = [];
          for (const el of elements) {
            if (el.textContent && el.textContent.trim().includes(text)) {
              results.push(el);
            }
          }
          return results;
        }
        
        
        // 1. Look for elements with exact text "Declaración"
        const declaracionElements = findElementsByText('Declaración', document.querySelectorAll('a, span, div, button'));
        if (declaracionElements.length > 0) {
          console.log('Found Declaración element by text content');
          declaracionElements[0].click();
          return true;
        }
        
        const sidebarElements = document.querySelectorAll('.sidebar a, .sidebar-menu a, .nav-sidebar a, .left-menu a, [role="navigation"] a');
        for (const el of sidebarElements) {
          if (el.textContent && el.textContent.trim().includes('Declaración')) {
            console.log('Found Declaración in sidebar');
            el.click();
            return true;
          }
        }
        
        const leftMenuItems = document.querySelectorAll('.sidebar a, .sidebar-menu a, .nav-sidebar a, .left-menu a, [role="navigation"] a');
        if (leftMenuItems.length > 0) {
          console.log('Clicking first menu item in left sidebar');
          leftMenuItems[0].click();
          return true;
        }
        
        const expandIcons = document.querySelectorAll('a i.fa-caret-down, a i.fa-chevron-down, a i.fa-angle-down, a i.expand-icon, a .dropdown-icon');
        if (expandIcons.length > 0) {
          console.log('Found expand icon, clicking parent element');
          expandIcons[0].closest('a').click();
          return true;
        }
        
        return false;
      });
      
      if (clickedDeclaracion) {
        console.log('Successfully clicked on Declaración menu using JavaScript evaluation');
        await popup.waitForTimeout(2000);
        await popup.screenshot({ path: './screenshots/after_declaration_menu_click_js.png', fullPage: true });
      } else {
        console.log('Could not find Declaración menu using JavaScript evaluation');
      }
    } catch (jsError) {
      console.error('Error using JavaScript to click Declaración menu:', jsError);
    }
    
    try {
      const clickedCrearDeclaracion = await popup.evaluate(() => {
        function findElementsByText(text, elements) {
          const results = [];
          for (const el of elements) {
            if (el.textContent && el.textContent.trim().includes(text)) {
              results.push(el);
            }
          }
          return results;
        }
        
        
        // 1. Look for elements with exact text "Crear Declaración"
        const crearElements = findElementsByText('Crear Declaración', document.querySelectorAll('a, span, div, button'));
        if (crearElements.length > 0) {
          console.log('Found Crear Declaración element by text content');
          crearElements[0].click();
          return true;
        }
        
        // 2. Look for elements with text containing "Crear" and "Declaración"
        const crearElements2 = findElementsByText('Crear', document.querySelectorAll('a, span, div, button'));
        for (const el of crearElements2) {
          if (el.textContent && el.textContent.trim().includes('Declaración')) {
            console.log('Found element with Crear and Declaración');
            el.click();
            return true;
          }
        }
        
        // 3. Look for elements with text containing "Nueva" and "Declaración"
        const nuevaElements = findElementsByText('Nueva', document.querySelectorAll('a, span, div, button'));
        for (const el of nuevaElements) {
          if (el.textContent && el.textContent.trim().includes('Declaración')) {
            console.log('Found element with Nueva and Declaración');
            el.click();
            return true;
          }
        }
        
        // 4. Try clicking on any visible submenu items after clicking Declaración
        const submenuItems = document.querySelectorAll('.submenu a, .dropdown-menu a, .menu-item a');
        if (submenuItems.length > 0) {
          console.log('Clicking first submenu item');
          submenuItems[0].click();
          return true;
        }
        
        return false;
      });
      
      if (clickedCrearDeclaracion) {
        console.log('Successfully clicked on Crear Declaración link using JavaScript evaluation');
        await popup.waitForTimeout(2000);
        await popup.screenshot({ path: './screenshots/after_crear_declaration_click_js.png', fullPage: true });
      } else {
        console.log('Could not find Crear Declaración link using JavaScript evaluation');
      }
    } catch (jsError) {
      console.error('Error using JavaScript to click Crear Declaración link:', jsError);
    }
    
    try {
      console.log('Attempting fallback using direct coordinate click for Declaración menu');
      
      await popup.mouse.click(150, 70); // Adjust these coordinates based on the screenshot
      console.log('Clicked on approximate Declaración menu coordinates');
      await popup.waitForTimeout(3000);
      await popup.screenshot({ path: './screenshots/after_declaration_menu_coordinate_click.png', fullPage: true });
      
      console.log('Attempting to click on Crear Declaración submenu');
      await popup.mouse.click(150, 108); // Adjusted coordinates based on the screenshot
      console.log('Clicked on approximate Crear Declaración coordinates');
      await popup.waitForTimeout(5000); // Increased timeout to allow page to load
      await popup.screenshot({ path: './screenshots/after_crear_declaration_coordinate_click.png', fullPage: true });
      
      const pageTitle = await popup.evaluate(() => {
        const breadcrumbElements = document.querySelectorAll('a, span, div');
        for (const el of breadcrumbElements) {
          if (el.textContent && el.textContent.includes('Crear declaración')) {
            return 'Crear declaración page found';
          }
        }
        return null;
      });
      
      if (pageTitle) {
        console.log('Successfully navigated to Crear declaración page');
      } else {
        console.log('Could not confirm navigation to Crear declaración page');
      }
    } catch (coordinateError) {
      console.error('Error using coordinate click:', coordinateError);
    }
    
    console.log('Waiting for declaration form to load...');
    let formFound = false;
    
    try {
      const formSelectors = [
        '#crearDeclaracionForm',
        'form',
        '.form',
        '.form-container',
        '[role="form"]',
        '.panel-body form',
        '.content form',
        '.main-content form'
      ];
      
      for (const selector of formSelectors) {
        try {
          console.log(`Trying form selector: ${selector}`);
          const form = await popup.waitForSelector(selector, { 
            timeout: 5000,
            state: 'visible' 
          });
          
          if (form) {
            console.log(`Found form with selector: ${selector}`);
            formFound = true;
            await popup.screenshot({ path: './screenshots/declaration_form.png' });
            break;
          }
        } catch (selectorError) {
          console.log(`Selector ${selector} failed: ${selectorError.message}`);
        }
      }
      
      if (!formFound) {
        console.log('Trying to find input fields as fallback');
        const inputSelectors = [
          'input',
          'textarea',
          'select',
          '#inputFactura',
          '#inputFechaDeclaracion',
          '#inputCliente'
        ];
        
        for (const selector of inputSelectors) {
          try {
            const input = await popup.waitForSelector(selector, { 
              timeout: 5000,
              state: 'visible' 
            });
            
            if (input) {
              console.log(`Found input field with selector: ${selector}`);
              formFound = true;
              await popup.screenshot({ path: './screenshots/form_input_found.png' });
              break;
            }
          } catch (inputError) {
            console.log(`Input selector ${selector} failed: ${inputError.message}`);
          }
        }
      }
      
      if (formFound) {
        console.log('Form or input fields found, ready to proceed with form filling');
      } else {
        console.log('Could not find form or input fields, but continuing with best effort');
        await popup.screenshot({ path: './screenshots/form_not_found.png', fullPage: true });
        
        const html = await popup.content();
        fs.writeFileSync('./logs/form_page_content.html', html);
        
        const pageElements = await popup.evaluate(() => {
          const elements = Array.from(document.querySelectorAll('*'));
          return elements
            .filter(el => el.id || (el.className && typeof el.className === 'string' && el.className.length > 0))
            .slice(0, 50)  // Limit to first 50 elements
            .map(el => ({
              tagName: el.tagName,
              id: el.id,
              className: typeof el.className === 'string' ? el.className : null,
              text: el.textContent ? el.textContent.substring(0, 100) : null
            }));
        });
        
        fs.writeFileSync('./logs/form_page_elements.json', JSON.stringify(pageElements, null, 2));
        console.log('Saved page elements to logs/form_page_elements.json for debugging');
      }
    } catch (error) {
      console.error('Error during form detection:', error);
      await popup.screenshot({ path: './screenshots/form_detection_error.png', fullPage: true });
      console.log('Continuing with process despite form detection error');
    }
    
    console.log('Step 3: Filling Section A - Datos de la Declaración');
    
    try {
      await popup.fill('#inputFactura', declarationData.invoiceId);
      console.log('Filled Invoice ID');
    } catch (error) {
      console.error('Error filling Invoice ID:', error);
      await popup.screenshot({ path: './screenshots/invoice_id_error.png' });
    }
    
    try {
      await popup.fill('#inputFechaDeclaracion', declarationData.date);
      console.log('Filled Declaration Date');
    } catch (error) {
      console.error('Error filling Declaration Date:', error);
      await popup.screenshot({ path: './screenshots/date_error.png' });
    }
    
    try {
      await popup.fill('#inputCliente', declarationData.customerCode);
      console.log('Filled Customer Code');
    } catch (error) {
      console.error('Error filling Customer Code:', error);
      await popup.screenshot({ path: './screenshots/customer_code_error.png' });
    }
    
    console.log('Step 4: Filling Section B - Datos de la Mercancía');
    
    try {
      await popup.fill('input[name="descripcion"]', declarationData.goodsDescription);
      console.log('Filled Goods Description');
    } catch (error) {
      console.error('Error filling Goods Description:', error);
      await popup.screenshot({ path: './screenshots/description_error.png' });
    }
    
    try {
      await popup.fill('input[name="cantidad"]', declarationData.quantity);
      console.log('Filled Quantity');
    } catch (error) {
      console.error('Error filling Quantity:', error);
      await popup.screenshot({ path: './screenshots/quantity_error.png' });
    }
    
    try {
      await popup.fill('input[name="pesoKg"]', declarationData.weightKg);
      console.log('Filled Weight');
    } catch (error) {
      console.error('Error filling Weight:', error);
      await popup.screenshot({ path: './screenshots/weight_error.png' });
    }
    
    try {
      await popup.fill('input[name="volumenM3"]', declarationData.volumeM3);
      console.log('Filled Volume');
    } catch (error) {
      console.error('Error filling Volume:', error);
      await popup.screenshot({ path: './screenshots/volume_error.png' });
    }
    
    console.log('Step 5: Filling Section C - Transporte');
    
    try {
      await popup.selectOption('#selectTransporte', declarationData.transportType);
      console.log('Selected Transport Type');
    } catch (error) {
      console.error('Error selecting Transport Type:', error);
      await popup.screenshot({ path: './screenshots/transport_type_error.png' });
    }
    
    if (declarationData.transportType === 'AIR') {
      try {
        await popup.fill('#inputVuelo', declarationData.flightNumber);
        console.log('Filled Flight Number');
      } catch (error) {
        console.error('Error filling Flight Number:', error);
        await popup.screenshot({ path: './screenshots/flight_number_error.png' });
      }
      
      try {
        await popup.fill('#inputTransportista', declarationData.carrierName);
        console.log('Filled Carrier Name');
      } catch (error) {
        console.error('Error filling Carrier Name:', error);
        await popup.screenshot({ path: './screenshots/carrier_name_error.png' });
      }
    }
    
    console.log('Step 6: Filling Section D - Declaración Aduanera');
    
    try {
      await popup.fill('#inputHsCode', declarationData.hsCode);
      console.log('Filled HS Code');
    } catch (error) {
      console.error('Error filling HS Code:', error);
      await popup.screenshot({ path: './screenshots/hs_code_error.png' });
    }
    
    try {
      await popup.fill('input[name="paisOrigen"]', declarationData.originCountry);
      console.log('Filled Origin Country');
    } catch (error) {
      console.error('Error filling Origin Country:', error);
      await popup.screenshot({ path: './screenshots/origin_country_error.png' });
    }
    
    try {
      await popup.fill('input[name="paisDestino"]', declarationData.destinationCountry);
      console.log('Filled Destination Country');
    } catch (error) {
      console.error('Error filling Destination Country:', error);
      await popup.screenshot({ path: './screenshots/destination_country_error.png' });
    }
    
    try {
      await popup.fill('input[name="valorDeclarado"]', declarationData.declaredValue);
      console.log('Filled Declared Value');
    } catch (error) {
      console.error('Error filling Declared Value:', error);
      await popup.screenshot({ path: './screenshots/declared_value_error.png' });
    }
    
    try {
      await popup.selectOption('#selectMoneda', declarationData.valueCurrency);
      console.log('Selected Currency');
    } catch (error) {
      console.error('Error selecting Currency:', error);
      await popup.screenshot({ path: './screenshots/currency_error.png' });
    }
    
    console.log('Step 7: Filling Section E - Documentos Adjuntos');
    
    if (declarationData.commercialInvoicePath) {
      try {
        await popup.setInputFiles('input#uploadFacturaComercial', declarationData.commercialInvoicePath);
        console.log('Uploaded Commercial Invoice');
      } catch (error) {
        console.error('Error uploading Commercial Invoice:', error);
        await popup.screenshot({ path: './screenshots/invoice_upload_error.png' });
      }
    }
    
    if (declarationData.packingListPath) {
      try {
        await popup.setInputFiles('input#uploadPackingList', declarationData.packingListPath);
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
      const downloadPath = path.join(declarationData.downloadDir, `declaration_${transactionId || 'unknown'}.pdf`);
      await download.saveAs(downloadPath);
      console.log(`PDF downloaded to: ${downloadPath}`);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      await popup.screenshot({ path: './screenshots/pdf_download_error.png', fullPage: true });
    }
    
    try {
      const screenshotPath = path.join(declarationData.downloadDir, `declaration_${transactionId || 'unknown'}.png`);
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
