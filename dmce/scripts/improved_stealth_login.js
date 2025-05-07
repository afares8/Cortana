const { firefox } = require('playwright');
const { randomInt } = require('crypto');
const fs = require('fs');

(async () => {
  if (!fs.existsSync('./videos')) {
    fs.mkdirSync('./videos');
  }

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
    await page.screenshot({ path: 'initial_page.png' });

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
    await popup.screenshot({ path: 'login_popup.png' });

    console.log('Step 3: Extracting form fields and submitting credentials');
    
    const hiddenData = await popup.$$eval('form input[type="hidden"]', els =>
      els.reduce((m, e) => ({ ...m, [e.name]: e.value }), {})
    );
    
    console.log('Hidden form fields:', Object.keys(hiddenData));
    
    const payload = {
      ...hiddenData,
      j_username: process.env.DMCE_USER || "crandonzlpr",
      j_password: process.env.DMCE_PASS || "perfumes"
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
    await popup.screenshot({ path: 'post_login.png' });
    
    if (popup.url().includes('login_error')) {
      throw new Error('Login failed: ' + popup.url());
    }
    
    await popup.waitForSelector('body', { timeout: 20000 });
    console.log('Dashboard loaded');

    console.log('Step 4: Exploring dashboard to find invoice section');
    
    const links = await popup.$$eval('a', anchors => 
      anchors.map(a => ({ 
        href: a.href, 
        text: a.innerText.trim(),
        id: a.id,
        class: a.className
      }))
    );
    
    const invoiceLinks = links.filter(link => 
      link.text.toLowerCase().includes('factura') || 
      link.text.toLowerCase().includes('invoice') ||
      link.href.toLowerCase().includes('factura') ||
      link.href.toLowerCase().includes('invoice')
    );
    
    console.log('Potential invoice links:', invoiceLinks);
    
    let invoiceUrl = '';
    
    if (invoiceLinks.length > 0) {
      invoiceUrl = invoiceLinks[0].href;
      console.log('Navigating to invoice URL:', invoiceUrl);
      
      await popup.goto(invoiceUrl, { 
        timeout: 30000,
        waitUntil: 'networkidle' 
      });
    } else {
      const possiblePaths = [
        '/TFBFTZ/facturas/list.cl',
        '/TFBFTZ/invoice/list.cl',
        '/TFBFTZ/invoices.cl',
        '/TFBFTZ/factura/list.cl'
      ];
      
      for (const path of possiblePaths) {
        const fullUrl = 'https://dmce2.zonalibredecolon.gob.pa' + path;
        console.log('Trying fallback URL:', fullUrl);
        
        try {
          await popup.goto(fullUrl, { 
            timeout: 15000,
            waitUntil: 'networkidle' 
          });
          
          invoiceUrl = fullUrl;
          console.log('Found working invoice URL:', invoiceUrl);
          break;
        } catch (e) {
          console.log('URL failed:', fullUrl, e.message);
        }
      }
    }
    
    if (!invoiceUrl) {
      throw new Error('Could not find invoice section URL');
    }
    
    await popup.screenshot({ path: 'invoice_page.png' });
    
    console.log('Step 5: Identifying invoice list elements');
    
    const tableSelectors = [
      'table.invoice-table',
      'table#invoice-list',
      'table.data-table',
      'div#invoice-list',
      'div.invoice-container',
      'table tbody tr',
      '.table-responsive table'
    ];
    
    let invoiceTableSelector = '';
    
    for (const selector of tableSelectors) {
      console.log('Trying selector:', selector);
      const exists = await popup.$(selector);
      
      if (exists) {
        invoiceTableSelector = selector;
        console.log('Found working selector:', invoiceTableSelector);
        break;
      }
    }
    
    if (!invoiceTableSelector) {
      const tables = await popup.$$eval('table', tables => 
        tables.map((table, i) => ({
          index: i,
          id: table.id,
          class: table.className,
          rows: table.rows.length,
          headers: Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim())
        }))
      );
      
      console.log('Available tables:', tables);
      
      const containers = await popup.$$eval('div[id], div[class]', divs => 
        divs.map(div => ({
          id: div.id,
          class: div.className,
          childCount: div.children.length,
          text: div.innerText.substring(0, 100)
        }))
      );
      
      console.log('Potential containers:', containers.filter(c => 
        c.id?.toLowerCase().includes('invoice') || 
        c.class?.toLowerCase().includes('invoice') ||
        c.text?.toLowerCase().includes('factura') ||
        c.text?.toLowerCase().includes('invoice')
      ));
      
      throw new Error('Could not identify invoice list selector');
    }
    
    console.log('Step 6: Extracting invoice IDs');
    
    const rowSelector = `${invoiceTableSelector} tbody tr`;
    await popup.waitForSelector(rowSelector, { timeout: 20000 });
    
    const invoiceIds = await popup.$$eval(rowSelector, rows => 
      rows.slice(0, 3).map(row => {
        return row.getAttribute('data-invoice-id') || 
               row.getAttribute('data-id') || 
               row.getAttribute('id') || 
               row.querySelector('td')?.innerText;
      })
    );
    
    console.log('Found invoice IDs:', invoiceIds);
    
    console.log('Step 7: Finding automation button');
    
    const buttonSelectors = [
      '#automate-all-btn',
      'button:has-text("Automate")',
      'button:has-text("Automatizar")',
      'a:has-text("Automate")',
      'a:has-text("Automatizar")',
      'button.automation-btn',
      'button.btn-primary'
    ];
    
    let automationButton = null;
    
    for (const selector of buttonSelectors) {
      console.log('Trying button selector:', selector);
      automationButton = await popup.$(selector);
      
      if (automationButton) {
        console.log('Found automation button:', selector);
        break;
      }
    }
    
    if (!automationButton) {
      const buttons = await popup.$$eval('button, a.btn, input[type="button"]', btns => 
        btns.map(btn => ({
          tag: btn.tagName,
          id: btn.id,
          class: btn.className,
          text: btn.innerText.trim(),
          type: btn.type
        }))
      );
      
      console.log('Available buttons:', buttons);
      throw new Error('Could not find automation button');
    }
    
    console.log('Step 8: Clicking automation button');
    
    await popup.screenshot({ path: 'before_automation.png' });
    
    await popup.waitForTimeout(randomInt(500, 1500));
    await automationButton.click();
    
    console.log('Clicked automation button');
    
    console.log('Step 9: Waiting for automation completion');
    
    const completionSelectors = [
      '#automation-complete',
      '.success-message',
      '.alert-success',
      'div:has-text("Automation complete")',
      'div:has-text("Automatización completada")'
    ];
    
    let completionFound = false;
    
    for (const selector of completionSelectors) {
      try {
        console.log('Trying completion selector:', selector);
        await popup.waitForSelector(selector, { timeout: 10000 });
        console.log('Found completion indicator:', selector);
        completionFound = true;
        break;
      } catch (e) {
      }
    }
    
    if (!completionFound) {
      console.log('No explicit completion indicator found, waiting for network idle');
      await popup.waitForLoadState('networkidle');
      
      const finalButtons = await popup.$$eval('button, a.btn', btns => 
        btns.map(btn => ({
          id: btn.id,
          class: btn.className,
          text: btn.innerText.trim(),
          disabled: btn.disabled
        }))
      );
      
      console.log('Final button states:', finalButtons);
    }
    
    await popup.screenshot({ path: 'automation_complete.png' });
    console.log('Automation process completed');
    
  } catch (error) {
    console.error('Error during automation:', error);
    
    if (popup) {
      await popup.screenshot({ path: 'error_state.png' });
      console.log('Current URL at error:', popup.url());
      
      const html = await popup.content();
      fs.writeFileSync('error_page.html', html);
    } else {
      await page.screenshot({ path: 'error_state.png' });
    }
  } finally {
    await context.tracing.stop({ path: 'trace.zip' });
    console.log('Trace saved to trace.zip');
    
    await browser.close();
    console.log('Browser closed');
  }
})();
