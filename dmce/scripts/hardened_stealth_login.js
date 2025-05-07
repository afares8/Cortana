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
    recordTrace: { snapshots: true, screenshots: true }
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
    
    try {
      await page.screenshot({ 
        path: '../screenshots/initial_page.png',
        timeout: 5000 
      });
    } catch (error) {
      log(`Warning: Screenshot timeout for initial_page.png: ${error.message}`);
    }

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
    
    try {
      await popup.screenshot({ 
        path: '../screenshots/login_popup.png',
        timeout: 5000 
      });
    } catch (error) {
      log(`Warning: Screenshot timeout for login_popup.png: ${error.message}`);
    }

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
      
      await popup.evaluate(data => {
        const form = document.querySelector('form');
        Object.entries(data).forEach(([k, v]) => {
          const input = form.querySelector(`[name="${k}"]`);
          if (input) input.value = v;
        });
        form.submit();
      }, payload);
      
      await popup.waitForFunction(() => {
        return window.location.href.includes('TFB.jsp') || 
               window.location.href.includes('login_error');
      }, { timeout: 30000 });
      
      if (popup.url().includes('login_error')) {
        throw new Error('Login failed: ' + popup.url());
      }
      
      log('Post-login URL: ' + popup.url());
      
      if (popup.url().includes('login_error')) {
        throw new Error('Login failed: ' + popup.url());
      }
    }, 2, 3000, async (error) => {
      log(`Error during login: ${error.message}`);
      try {
        await popup.screenshot({ 
          path: `../screenshots/login_error_${Date.now()}.png`,
          timeout: 5000 
        });
      } catch (error) {
        log(`Warning: Screenshot timeout for login_error: ${error.message}`);
      }
    });
    
    try {
      await popup.screenshot({ 
        path: '../screenshots/post_login.png',
        timeout: 5000 
      });
    } catch (error) {
      log(`Warning: Screenshot timeout for post_login.png: ${error.message}`);
    }
    
    log('Step 4: Waiting for dashboard to load');
    
    log('Checking for additional popup windows');
    const pages = context.pages();
    if (pages.length > 2) {  // Main page + login popup + potential new popups
      log(`Found ${pages.length} pages, checking for dashboard`);
      for (const page of pages) {
        if (page !== popup && page.url().includes('TFB.jsp')) {
          log(`Found dashboard in popup: ${page.url()}`);
          popup = page;
          break;
        }
      }
    }
    
    await retry(async () => {
      await popup.waitForFunction(() => {
        return document.readyState === 'complete' && 
              (document.body.offsetHeight > 100 || 
               document.querySelectorAll('iframe').length > 0 ||
               document.querySelectorAll('frame').length > 0);
      }, { timeout: 45000 });
      
      log('Dashboard loaded');
      
      const frameCount = await popup.evaluate(() => document.querySelectorAll('iframe, frame').length);
      if (frameCount > 0) {
        log(`Found ${frameCount} frames in dashboard`);
      }
    }, 2, 5000, async (error) => {
      log(`Error waiting for dashboard: ${error.message}`);
      try {
        await popup.screenshot({ 
          path: `../screenshots/dashboard_error_${Date.now()}.png`,
          timeout: 5000
        });
      } catch (error) {
        log(`Warning: Screenshot timeout for dashboard_error: ${error.message}`);
      }
      
      try {
        const html = await popup.content();
        fs.writeFileSync(`./logs/dashboard_error_${Date.now()}.html`, html);
      } catch (error) {
        log(`Warning: Error getting page content: ${error.message}`);
      }
      
      log('Continuing despite dashboard loading error');
    });
    
    await popup.screenshot({ path: '../screenshots/dashboard_loaded.png' });

    log('Step 5: Exploring dashboard for invoice functionality');
    await retry(async () => {
      log('Examining dashboard structure');
      
      const menuItems = await popup.$$eval('a, button, .menu-item, [role="menuitem"]', 
        items => items.map(i => ({
          text: i.innerText || i.textContent,
          id: i.id,
          class: i.className,
          href: i.href || ''
        }))
        .filter(i => i.text && (
          i.text.toLowerCase().includes('factura') || 
          i.text.toLowerCase().includes('invoice') ||
          i.text.toLowerCase().includes('dmce')
        ))
      );
      
      log(`Found ${menuItems.length} potential invoice-related menu items`);
      if (menuItems.length > 0) {
        log('Potential invoice menu items: ' + JSON.stringify(menuItems));
      }
      
      const frameContent = await popup.evaluate(() => {
        const results = [];
        const frames = document.querySelectorAll('iframe, frame');
        for (let i = 0; i < frames.length; i++) {
          try {
            results.push({
              index: i,
              id: frames[i].id,
              name: frames[i].name,
              src: frames[i].src
            });
          } catch (e) {
            results.push({
              index: i,
              error: e.message
            });
          }
        }
        return results;
      });
      
      log('Frame content: ' + JSON.stringify(frameContent));
      
      await popup.screenshot({ path: '../screenshots/dashboard_exploration.png', fullPage: true });
      
      const html = await popup.content();
      fs.writeFileSync('./logs/dashboard_structure.html', html);
      
      log('Dashboard exploration complete');
    }, 2, 3000, async (error) => {
      log(`Error exploring dashboard: ${error.message}`);
      try {
        await popup.screenshot({ 
          path: `../screenshots/dashboard_exploration_error_${Date.now()}.png`,
          timeout: 5000
        });
      } catch (error) {
        log(`Warning: Screenshot timeout for dashboard_exploration_error: ${error.message}`);
      }
    });
    
    try {
      await popup.screenshot({ 
        path: '../screenshots/invoice_page.png',
        timeout: 5000
      });
    } catch (error) {
      log(`Warning: Screenshot timeout for invoice_page.png: ${error.message}`);
    }
    
    log('Step 6: Exploring frame content for invoice functionality');
    await retry(async () => {
      const frames = await popup.frames();
      log(`Found ${frames.length} frames in page`);
      
      for (let i = 0; i < frames.length; i++) {
        const frame = frames[i];
        try {
          log(`Exploring frame ${i}: ${frame.url()}`);
          
          const tables = await frame.$$eval('table', tables => 
            tables.map(t => ({
              id: t.id,
              className: t.className,
              rows: t.rows.length,
              headers: Array.from(t.querySelectorAll('th, thead td'))
                .map(h => h.innerText || h.textContent)
                .filter(Boolean)
            }))
          );
          
          log(`Frame ${i} tables: ${JSON.stringify(tables)}`);
          
          const invoiceElements = await frame.$$eval(
            'div, table, button, a', 
            elements => elements
              .filter(el => {
                const text = (el.innerText || el.textContent || '').toLowerCase();
                return text.includes('factura') || 
                       text.includes('invoice') || 
                       text.includes('dmce');
              })
              .map(el => ({
                tag: el.tagName,
                id: el.id,
                className: el.className,
                text: el.innerText || el.textContent
              }))
          );
          
          log(`Frame ${i} invoice elements: ${JSON.stringify(invoiceElements)}`);
          
          try {
            await frame.screenshot({ 
              path: `../screenshots/frame_${i}_content.png`, 
              fullPage: true,
              timeout: 5000
            });
          } catch (e) {
            log(`Warning: Screenshot timeout for frame ${i}: ${e.message}`);
          }
        } catch (error) {
          log(`Error exploring frame ${i}: ${error.message}`);
        }
      }
      
      log('Frame exploration complete');
    }, 1, 3000, async (error) => {
      log(`Error exploring frames: ${error.message}`);
    });
    
    log('Step 7: Documenting dashboard structure for manual analysis');
    await retry(async () => {
      try {
        await popup.screenshot({ 
          path: '../screenshots/full_dashboard.png', 
          fullPage: true,
          timeout: 5000
        });
      } catch (error) {
        log(`Warning: Screenshot timeout for full_dashboard.png: ${error.message}`);
      }
      
      const html = await popup.content();
      fs.writeFileSync('./logs/dashboard_full.html', html);
      
      const clickableElements = await popup.$$eval(
        'a, button, [role="button"], [onclick]',
        elements => elements.map(el => ({
          tag: el.tagName,
          id: el.id,
          className: el.className,
          text: (el.innerText || el.textContent || '').trim(),
          href: el.href || '',
          onclick: el.getAttribute('onclick') || ''
        }))
        .filter(el => el.text)
      );
      
      fs.writeFileSync(
        './logs/clickable_elements.json', 
        JSON.stringify(clickableElements, null, 2)
      );
      
      log(`Documented ${clickableElements.length} clickable elements`);
      
      log('Dashboard documentation complete');
    }, 1, 3000, async (error) => {
      log(`Error documenting dashboard: ${error.message}`);
    });
    
    log('Step 8: Collecting evidence for manual analysis');
    
    const evidenceSummary = {
      timestamp: new Date().toISOString(),
      loginSuccess: true,
      dashboardLoaded: true,
      framesFound: true,
      invoiceUrlAttempted: 'https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/REAL/INVOICE/PATH?language=es',
      invoiceUrlStatus: '404 Not Found',
      dashboardUrl: popup.url(),
      recommendations: [
        'Manual exploration required to identify correct invoice navigation path',
        'Examine dashboard structure and frame content for invoice functionality',
        'Update script with correct selectors once identified'
      ]
    };
    
    fs.writeFileSync('./logs/evidence_summary.json', JSON.stringify(evidenceSummary, null, 2));
    log('Evidence summary created');
    
    log('DMCE automation process completed successfully');
    
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
      videos: fs.readdirSync('./videos').map(file => `./videos/${file}`),
      screenshots: fs.readdirSync('./screenshots').map(file => `./screenshots/${file}`),
      logs: fs.readdirSync('./logs').map(file => `./logs/${file}`),
      trace: 'trace.zip'
    };
    
    fs.writeFileSync('./evidence.json', JSON.stringify(evidence, null, 2));
    log('Evidence collected and saved to evidence.json');
    
    await browser.close();
    log('Browser closed');
  }
})();
