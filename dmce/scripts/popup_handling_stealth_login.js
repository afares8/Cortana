const { firefox } = require('playwright');
const { randomInt } = require('crypto');
const fs = require('fs');
const { getDMCECredentials } = require('./credential_handler');

async function retry(fn, retries = 2, delay = 2000, onError = null) {
  let lastError;
  for (let attempt = 1; attempt <= retries + 1; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      console.log(`Attempt ${attempt}/${retries + 1} failed: ${error.message}`);
      
      if (onError) {
        await onError(error, attempt);
      }
      
      if (attempt <= retries) {
        console.log(`Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        delay = Math.min(delay * 1.5, 10000);
      }
    }
  }
  throw lastError;
}

(async () => {
  const dirs = ['./videos', './screenshots', './logs'];
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir);
    }
  }

  const logFile = `./logs/automation_log_${Date.now()}.txt`;
  const log = (message) => {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}`;
    console.log(logMessage);
    fs.appendFileSync(logFile, logMessage + '\n');
  };

  log('Starting DMCE portal automation');
  
  const browser = await firefox.launch({
    headless: false,
    args: ['-private'],
  });
  
  const context = await browser.newContext({
    locale: 'es-PA',
    timezoneId: 'America/Panama',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 },
    recordVideo: { dir: '../videos/' },
    recordTrace: { snapshots: true, screenshots: true },
    permissions: ['notifications'],
    acceptDownloads: true
  });
  
  context.on('page', async (page) => {
    log(`New page/popup detected: ${page.url()}`);
    
    page.on('dialog', async dialog => {
      log(`Dialog detected: ${dialog.type()} - ${dialog.message()}`);
      await dialog.accept();
      log(`Dialog accepted`);
    });
    
    page.on('console', msg => {
      log(`Console [${msg.type()}]: ${msg.text()}`);
    });
  });
  
  context.on('request', request => {
    if (request.resourceType() === 'xhr' || request.resourceType() === 'fetch') {
      log(`>> Request: ${request.method()} ${request.url()}`);
    }
  });
  
  context.on('response', response => {
    const status = response.status();
    const url = response.url();
    
    if (response.request().resourceType() === 'xhr' || 
        response.request().resourceType() === 'fetch' || 
        status >= 400) {
      log(`<< Response: ${status} ${url}`);
      
      if (status >= 400) {
        log(`!! Error Response: ${status} ${url}`);
      }
    }
  });
  
  await context.tracing.start({ screenshots: true, snapshots: true });
  
  const page = await context.newPage();
  let popup;
  
  try {
    log('Step 1: Navigating to login page');
    await retry(async () => {
      await page.goto('https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl?language=es', { 
        timeout: 30000,
        waitUntil: 'networkidle' 
      });
      log('Loaded initial login page');
    }, 2, 3000, async (error) => {
      log(`Error loading login page: ${error.message}`);
      await page.screenshot({ path: `../screenshots/login_page_error_${Date.now()}.png` });
    });
    
    await page.screenshot({ path: '../screenshots/initial_page.png' });

    log('Step 2: Opening login popup');
    popup = await retry(async () => {
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
      
      const popupInstance = await popupPromise;
      await popupInstance.waitForLoadState('networkidle');
      log('Popup URL: ' + popupInstance.url());
      return popupInstance;
    }, 2, 3000, async (error) => {
      log(`Error opening login popup: ${error.message}`);
      await page.screenshot({ path: `../screenshots/login_popup_error_${Date.now()}.png` });
    });
    
    await popup.screenshot({ path: '../screenshots/login_popup.png' });

    log('Step 3: Extracting form fields and submitting credentials');
    await retry(async () => {
      const hiddenData = await popup.$$eval('form input[type="hidden"]', els =>
        els.reduce((m, e) => ({ ...m, [e.name]: e.value }), {})
      );
      
      log('Hidden form fields: ' + Object.keys(hiddenData).join(', '));
      
      const credentials = getDMCECredentials();
      
      const payload = {
        ...hiddenData,
        j_username: credentials.username,
        j_password: credentials.password
      };
      
      await popup.type('#j_username', payload.j_username, { delay: randomInt(100, 200) });
      await popup.type('#j_password', payload.j_password, { delay: randomInt(100, 200) });
      await popup.mouse.wheel(0, randomInt(100, 300));
      log('Filled credentials');
      
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
      
      log('Post-login URL: ' + popup.url());
      
      if (popup.url().includes('login_error')) {
        throw new Error('Login failed: ' + popup.url());
      }
    }, 2, 3000, async (error) => {
      log(`Error during login: ${error.message}`);
      await popup.screenshot({ path: `../screenshots/login_error_${Date.now()}.png` });
    });
    
    await popup.screenshot({ path: '../screenshots/post_login.png' });
    
    log('Step 4: Handling dashboard popups and waiting for dashboard to load');
    
    const popupCheckInterval = setInterval(async () => {
      const pages = context.pages();
      for (let i = 0; i < pages.length; i++) {
        const p = pages[i];
        if (p !== page && p !== popup) {
          log(`Found additional popup: ${p.url()}`);
          await p.screenshot({ path: `../screenshots/additional_popup_${i}_${Date.now()}.png` });
          
          try {
            const closeButtons = await p.$$('button, .close, .btn-close, [aria-label="Close"], [title="Close"]');
            if (closeButtons.length > 0) {
              log(`Clicking close button on popup`);
              await closeButtons[0].click();
            } else {
              log(`Pressing Escape to close popup`);
              await p.keyboard.press('Escape');
            }
          } catch (e) {
            log(`Error handling popup: ${e.message}`);
          }
        }
      }
    }, 2000);
    
    await retry(async () => {
      await Promise.race([
        popup.waitForFunction(() => {
          return document.readyState === 'complete' && 
                 !document.querySelector('body[style*="display: none"]') &&
                 document.body.offsetHeight > 0;
        }, { timeout: 30000 }),
        
        popup.waitForSelector('iframe, .dashboard, #menu, .nav, [class*="menu"]', { 
          timeout: 30000,
          state: 'visible'
        }),
        
        (async () => {
          await popup.waitForLoadState('networkidle', { timeout: 20000 });
          await popup.waitForTimeout(10000); // Additional wait after network is idle
          return true;
        })()
      ]);
      
      log('Dashboard loaded using one of the waiting strategies');
    }, 2, 5000, async (error) => {
      log(`Error waiting for dashboard: ${error.message}`);
      await popup.screenshot({ path: `../screenshots/dashboard_error_${Date.now()}.png` });
      
      const html = await popup.content();
      fs.writeFileSync(`./logs/dashboard_error_${Date.now()}.html`, html);
    });
    
    clearInterval(popupCheckInterval);
    
    await popup.screenshot({ path: '../screenshots/dashboard_loaded.png' });
    
    const dashboardHtml = await popup.content();
    fs.writeFileSync('./logs/dashboard.html', dashboardHtml);
    
    log('Step 5: Looking for invoice-related elements in the dashboard');
    
    const iframes = await popup.$$('iframe');
    log(`Found ${iframes.length} iframes in the dashboard`);
    
    let invoiceFrame = null;
    let invoiceElements = [];
    
    for (let i = 0; i < iframes.length; i++) {
      try {
        const frame = await iframes[i].contentFrame();
        if (frame) {
          log(`Exploring iframe ${i}`);
          await frame.screenshot({ path: `../screenshots/iframe_${i}.png` }).catch(() => {});
          
          const frameElements = await frame.$$eval(
            'a, button, div, span, li, table',
            elements => elements.map(el => ({
              tag: el.tagName,
              id: el.id,
              class: el.className,
              text: el.innerText.trim().substring(0, 50),
              href: el.href || '',
              onclick: el.getAttribute('onclick') || ''
            }))
          ).catch(() => []);
          
          const relevantElements = frameElements.filter(el => 
            (el.text && (
              el.text.toLowerCase().includes('factura') ||
              el.text.toLowerCase().includes('invoice') ||
              el.text.toLowerCase().includes('dmce')
            )) ||
            (el.id && (
              el.id.toLowerCase().includes('factura') ||
              el.id.toLowerCase().includes('invoice') ||
              el.id.toLowerCase().includes('dmce')
            )) ||
            (el.class && (
              el.class.toLowerCase().includes('factura') ||
              el.class.toLowerCase().includes('invoice') ||
              el.class.toLowerCase().includes('dmce')
            ))
          );
          
          if (relevantElements.length > 0) {
            log(`Found ${relevantElements.length} potentially invoice-related elements in iframe ${i}`);
            invoiceElements = [...invoiceElements, ...relevantElements];
            invoiceFrame = frame;
          }
        }
      } catch (error) {
        log(`Error exploring iframe ${i}: ${error.message}`);
      }
    }
    
    fs.writeFileSync('./logs/invoice_elements.json', JSON.stringify(invoiceElements, null, 2));
    
    log('Step 6: Attempting to navigate to invoice functionality');
    
    if (invoiceElements.length > 0 && invoiceFrame) {
      log('Found invoice-related elements, attempting to interact');
      
      for (let i = 0; i < Math.min(invoiceElements.length, 3); i++) {
        const element = invoiceElements[i];
        log(`Attempting to click on element: ${element.tag} - ${element.text}`);
        
        try {
          const elementSelector = element.id ? `#${element.id}` : 
                                 element.class ? `.${element.class.split(' ')[0]}` : 
                                 `${element.tag}:has-text("${element.text}")`;
          
          await invoiceFrame.click(elementSelector).catch(() => {});
          await popup.waitForTimeout(3000);
          await popup.screenshot({ path: `../screenshots/after_click_${i}.png` });
          
          log(`Current URL after click: ${popup.url()}`);
        } catch (error) {
          log(`Error clicking element ${i}: ${error.message}`);
        }
      }
    } else {
      log('No invoice elements found in iframes, checking main page');
      
      const mainPageElements = await popup.$$eval(
        'a, button, div, span, li, table',
        elements => elements.map(el => ({
          tag: el.tagName,
          id: el.id,
          class: el.className,
          text: el.innerText.trim().substring(0, 50),
          href: el.href || '',
          onclick: el.getAttribute('onclick') || ''
        }))
      );
      
      const relevantMainElements = mainPageElements.filter(el => 
        (el.text && (
          el.text.toLowerCase().includes('factura') ||
          el.text.toLowerCase().includes('invoice') ||
          el.text.toLowerCase().includes('dmce')
        )) ||
        (el.id && (
          el.id.toLowerCase().includes('factura') ||
          el.id.toLowerCase().includes('invoice') ||
          el.id.toLowerCase().includes('dmce')
        )) ||
        (el.class && (
          el.class.toLowerCase().includes('factura') ||
          el.class.toLowerCase().includes('invoice') ||
          el.class.toLowerCase().includes('dmce')
        ))
      );
      
      if (relevantMainElements.length > 0) {
        log(`Found ${relevantMainElements.length} potentially invoice-related elements in main page`);
        fs.writeFileSync('./logs/main_page_invoice_elements.json', JSON.stringify(relevantMainElements, null, 2));
        
        for (let i = 0; i < Math.min(relevantMainElements.length, 3); i++) {
          const element = relevantMainElements[i];
          log(`Attempting to click on main page element: ${element.tag} - ${element.text}`);
          
          try {
            const elementSelector = element.id ? `#${element.id}` : 
                                   element.class ? `.${element.class.split(' ')[0]}` : 
                                   `${element.tag}:has-text("${element.text}")`;
            
            await popup.click(elementSelector).catch(() => {});
            await popup.waitForTimeout(3000);
            await popup.screenshot({ path: `../screenshots/after_main_click_${i}.png` });
            
            log(`Current URL after click: ${popup.url()}`);
          } catch (error) {
            log(`Error clicking main page element ${i}: ${error.message}`);
          }
        }
      } else {
        log('No invoice-related elements found in main page');
      }
    }
    
    log('Step 7: Trying direct navigation to potential invoice URLs');
    
    const potentialUrls = [
      '/TFBFTZ/factura/list.cl?language=es',
      '/TFBFTZ/invoice/list.cl?language=es',
      '/TFBFTZ/facturas/list.cl?language=es',
      '/TFBFTZ/invoices/list.cl?language=es',
      '/TFBFTZ/dmce/list.cl?language=es',
      '/TFBFTZ/dmce/factura.cl?language=es'
    ];
    
    for (const urlPath of potentialUrls) {
      const fullUrl = 'https://dmce2.zonalibredecolon.gob.pa' + urlPath;
      log(`Trying URL: ${fullUrl}`);
      
      try {
        const response = await popup.goto(fullUrl, { timeout: 10000 });
        log(`Status: ${response.status()}, URL: ${popup.url()}`);
        
        if (response.status() === 200) {
          log(`SUCCESS: URL returned 200 OK`);
          await popup.screenshot({ path: `../screenshots/url_success_${urlPath.replace(/\//g, '_').replace(/\?/g, '_')}.png` });
          
          const tables = await popup.$$eval('table', tables => 
            tables.map((table, i) => ({
              index: i,
              id: table.id,
              class: table.className,
              rows: table.rows.length
            }))
          );
          
          log(`Tables found: ${JSON.stringify(tables)}`);
          
          if (tables.length > 0) {
            log(`POTENTIAL INVOICE PAGE: Contains tables`);
            break; // Found a potential invoice page, stop trying other URLs
          }
        }
      } catch (e) {
        log(`Error navigating to ${fullUrl}: ${e.message}`);
      }
      
      await popup.waitForTimeout(1000);
    }
    
    log('Step 8: Capturing final dashboard state');
    await popup.screenshot({ path: '../screenshots/final_dashboard_state.png' });
    
    const finalHtml = await popup.content();
    fs.writeFileSync('./logs/final_page.html', finalHtml);
    
    log('Exploration complete');
    
  } catch (error) {
    log(`Fatal error during automation: ${error.message}`);
    log(error.stack);
    
    if (popup) {
      await popup.screenshot({ path: '../screenshots/error_state.png' });
      log('Current URL at error: ' + popup.url());
      
      const html = await popup.content();
      fs.writeFileSync('./logs/error_page.html', html);
    } else if (page) {
      await page.screenshot({ path: '../screenshots/error_state.png' });
    }
  } finally {
    await context.tracing.stop({ path: 'trace.zip' });
    log('Trace saved to trace.zip');
    
    const evidence = {
      timestamp: new Date().toISOString(),
      videos: fs.existsSync('./videos') ? fs.readdirSync('./videos').map(file => `./videos/${file}`) : [],
      screenshots: fs.existsSync('./screenshots') ? fs.readdirSync('./screenshots').map(file => `./screenshots/${file}`) : [],
      logs: fs.existsSync('./logs') ? fs.readdirSync('./logs').map(file => `./logs/${file}`) : [],
      trace: 'trace.zip'
    };
    
    fs.writeFileSync('./evidence.json', JSON.stringify(evidence, null, 2));
    log('Evidence collected and saved to evidence.json');
    
    await browser.close();
    log('Browser closed');
  }
})();
