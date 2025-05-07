const { firefox } = require('playwright');
const { randomInt } = require('crypto');
const fs = require('fs');
const { getDMCECredentials } = require('./credential_handler');

/**
 * DMCE Portal Automation Script
 * 
 * This script automates the login process for the DMCE portal using Firefox in private browsing mode.
 * It successfully logs in but requires manual exploration to identify the correct navigation path
 * to invoice functionality.
 */
(async () => {
  if (!fs.existsSync('./videos')) fs.mkdirSync('./videos', { recursive: true });
  if (!fs.existsSync('./screenshots')) fs.mkdirSync('./screenshots', { recursive: true });
  if (!fs.existsSync('./logs')) fs.mkdirSync('./logs', { recursive: true });
  
  console.log('Starting DMCE portal automation');
  
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
        path: '../screenshots/initial_page.png',
        timeout: 5000 
      });
    } catch (error) {
      console.log(`Warning: Screenshot timeout for initial_page.png: ${error.message}`);
    }

    console.log('Step 2: Opening login popup');
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
        path: '../screenshots/login_popup.png',
        timeout: 5000 
      });
    } catch (error) {
      console.log(`Warning: Screenshot timeout for login_popup.png: ${error.message}`);
    }

    console.log('Step 3: Extracting form fields and submitting credentials');
    
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
        path: '../screenshots/post_login.png',
        timeout: 5000 
      });
    } catch (error) {
      console.log(`Warning: Screenshot timeout for post_login.png: ${error.message}`);
    }
    
    if (popup.url().includes('login_error')) {
      throw new Error('Login failed: ' + popup.url());
    }
    
    console.log('Step 4: Waiting for dashboard to load');
    
    await popup.waitForFunction(() => {
      return document.readyState === 'complete' && 
             !document.querySelector('body[style*="display: none"]') &&
             document.body.offsetHeight > 0;
    }, { timeout: 30000 });
    
    console.log('Dashboard loaded');
    
    try {
      await popup.screenshot({ 
        path: '../screenshots/dashboard_loaded.png',
        timeout: 5000 
      });
    } catch (error) {
      console.log(`Warning: Screenshot timeout for dashboard_loaded.png: ${error.message}`);
    }
    
    console.log('Step 5: Dashboard exploration complete');
    console.log('NOTE: Manual exploration required to identify invoice functionality');
    console.log('The script successfully logs in but cannot locate invoice functionality');
    console.log('Please refer to final_dmce_report.md for detailed findings');
    
  } catch (error) {
    console.error('Error during automation:', error);
    
    if (popup) {
      try {
        await popup.screenshot({ 
          path: '../screenshots/error_state.png',
          timeout: 5000 
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
          path: '../screenshots/error_state.png',
          timeout: 5000 
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
