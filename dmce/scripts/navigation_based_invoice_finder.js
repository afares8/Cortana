const { firefox } = require('playwright');
const fs = require('fs');

(async () => {
  if (!fs.existsSync('./screenshots')) {
    fs.mkdirSync('./screenshots');
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
    recordVideo: { dir: './videos/' }
  });
  
  const page = await context.newPage();
  let popup;
  
  try {
    console.log('Step 1: Logging in to DMCE portal');
    await page.goto('https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl?language=es', { 
      timeout: 30000,
      waitUntil: 'networkidle' 
    });
    
    const loginBtn = await page.waitForSelector('a.login-btn', { timeout: 20000 });
    const [popupPromise] = await Promise.all([
      page.waitForEvent('popup', { timeout: 20000 }),
      loginBtn.click()
    ]);
    
    popup = await popupPromise;
    await popup.waitForLoadState('networkidle');
    
    // Extract hidden fields
    const hiddenData = await popup.$$eval('form input[type="hidden"]', els =>
      els.reduce((m, e) => ({ ...m, [e.name]: e.value }), {})
    );
    
    const payload = {
      ...hiddenData,
      j_username: "crandonzlpr",
      j_password: "perfumes"
    };
    
    await popup.type('#j_username', payload.j_username, { delay: 100 });
    await popup.type('#j_password', payload.j_password, { delay: 100 });
    
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
    
    console.log('Step 2: Waiting for dashboard to fully load');
    // More robust waiting strategy
    await popup.waitForTimeout(10000); // Give time for initial loading
    
    // Wait for dashboard to be interactive
    await popup.waitForFunction(() => {
      return document.readyState === 'complete' && 
             document.querySelectorAll('iframe').length > 0;
    }, { timeout: 30000 });
    
    await popup.screenshot({ path: './screenshots/dashboard_loaded.png' });
    console.log('Dashboard loaded');
    
    console.log('Step 3: Exploring dashboard elements');
    // Capture all clickable elements
    const clickableElements = await popup.$$eval(
      'a, button, div[onclick], span[onclick], li[onclick], .clickable, [role="button"]', 
      elements => elements.map(el => ({
        tag: el.tagName,
        id: el.id,
        class: el.className,
        text: el.innerText.trim().substring(0, 50),
        href: el.href || '',
        onclick: el.getAttribute('onclick') || '',
        role: el.getAttribute('role') || '',
        visible: el.offsetParent !== null
      }))
    );
    
    // Filter for potentially relevant elements
    const relevantElements = clickableElements.filter(el => 
      el.visible && (
        el.text.toLowerCase().includes('factura') ||
        el.text.toLowerCase().includes('invoice') ||
        el.text.toLowerCase().includes('dmce') ||
        el.href.toLowerCase().includes('factura') ||
        el.href.toLowerCase().includes('invoice') ||
        el.href.toLowerCase().includes('dmce') ||
        el.onclick.toLowerCase().includes('factura') ||
        el.onclick.toLowerCase().includes('invoice') ||
        el.onclick.toLowerCase().includes('dmce')
      )
    );
    
    console.log('Potentially relevant elements:', relevantElements);
    fs.writeFileSync('./screenshots/relevant_elements.json', JSON.stringify(relevantElements, null, 2));
    
    // Check for iframes which might contain the actual application
    const iframes = await popup.$$('iframe');
    console.log(`Found ${iframes.length} iframes`);
    
    // Explore each iframe
    for (let i = 0; i < iframes.length; i++) {
      console.log(`Exploring iframe ${i}`);
      const frame = await iframes[i].contentFrame();
      
      if (frame) {
        await frame.screenshot({ path: `./screenshots/iframe_${i}.png` });
        
        // Look for menu items in the iframe
        const frameMenuItems = await frame.$$eval(
          'a, button, div[onclick], span[onclick], li[onclick], .clickable, [role="button"]', 
          elements => elements.map(el => ({
            tag: el.tagName,
            id: el.id,
            class: el.className,
            text: el.innerText.trim().substring(0, 50),
            href: el.href || '',
            onclick: el.getAttribute('onclick') || '',
            role: el.getAttribute('role') || '',
            visible: el.offsetParent !== null
          }))
        ).catch(e => []);
        
        // Filter for potentially relevant elements in the iframe
        const relevantFrameElements = frameMenuItems.filter(el => 
          el.visible && (
            el.text.toLowerCase().includes('factura') ||
            el.text.toLowerCase().includes('invoice') ||
            el.text.toLowerCase().includes('dmce') ||
            el.href.toLowerCase().includes('factura') ||
            el.href.toLowerCase().includes('invoice') ||
            el.href.toLowerCase().includes('dmce') ||
            el.onclick.toLowerCase().includes('factura') ||
            el.onclick.toLowerCase().includes('invoice') ||
            el.onclick.toLowerCase().includes('dmce')
          )
        );
        
        console.log(`Iframe ${i} relevant elements:`, relevantFrameElements);
        fs.writeFileSync(`./screenshots/iframe_${i}_elements.json`, JSON.stringify(relevantFrameElements, null, 2));
        
        // Try clicking on menu items or navigation elements
        const menuElements = await frame.$$('[class*="menu"], [class*="nav"], [class*="sidebar"], [role="menu"], [role="navigation"]');
        
        for (const menuElement of menuElements) {
          await menuElement.screenshot({ path: `./screenshots/menu_element_${i}.png` });
        }
      }
    }
    
    console.log('Step 4: Attempting to navigate to invoice functionality');
    // Try clicking on elements that might lead to invoice functionality
    // Start with main menu items
    const mainMenuItems = await popup.$$('[class*="menu-item"], [class*="nav-item"], [role="menuitem"]');
    
    for (let i = 0; i < mainMenuItems.length; i++) {
      const menuText = await mainMenuItems[i].innerText().catch(() => '');
      console.log(`Menu item ${i}: ${menuText}`);
      
      if (menuText) {
        await mainMenuItems[i].screenshot({ path: `./screenshots/menu_item_${i}.png` });
      }
    }
    
    // Record network requests to find potential API endpoints
    const requests = [];
    popup.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType()
      });
    });
    
    // Click around in the UI to trigger navigation
    await popup.mouse.click(100, 100);
    await popup.keyboard.press('Tab');
    await popup.keyboard.press('Enter');
    await popup.waitForTimeout(2000);
    
    await popup.mouse.click(200, 200);
    await popup.keyboard.press('Tab');
    await popup.keyboard.press('Enter');
    await popup.waitForTimeout(2000);
    
    // Save the network requests for analysis
    fs.writeFileSync('./screenshots/network_requests.json', JSON.stringify(requests, null, 2));
    
    console.log('Step 5: Final dashboard state');
    await popup.screenshot({ path: './screenshots/final_dashboard_state.png' });
    
    // Save the final page HTML for analysis
    const html = await popup.content();
    fs.writeFileSync('./screenshots/dashboard_html.html', html);
    
    console.log('Navigation exploration complete');
    
  } catch (error) {
    console.error('Error during navigation exploration:', error);
    
    if (popup) {
      await popup.screenshot({ path: './screenshots/error_state.png' });
      const html = await popup.content();
      fs.writeFileSync('./screenshots/error_page.html', html);
    }
  } finally {
    await browser.close();
    console.log('Browser closed');
  }
})();
