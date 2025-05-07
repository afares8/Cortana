const { firefox } = require('playwright');

(async () => {
  const browser = await firefox.launch({
    headless: false,
    args: ['-private'],
  });
  const context = await browser.newContext({
    locale: 'es-PA',
    timezoneId: 'America/Panama',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
  });
  
  const page = await context.newPage();
  
  // Login first
  try {
    console.log('Logging in...');
    await page.goto('https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/cusLogin/login.cl?language=es');
    const loginBtn = await page.waitForSelector('a.login-btn');
    const [popup] = await Promise.all([
      page.waitForEvent('popup'),
      loginBtn.click()
    ]);
    
    await popup.waitForLoadState();
    
    // Extract hidden fields
    const hiddenData = await popup.$$eval('form input[type="hidden"]', els =>
      els.reduce((m, e) => ({ ...m, [e.name]: e.value }), {})
    );
    
    const payload = {
      ...hiddenData,
      j_username: "crandonzlpr",
      j_password: "perfumes"
    };
    
    await popup.type('#j_username', payload.j_username);
    await popup.type('#j_password', payload.j_password);
    
    await Promise.all([
      popup.waitForNavigation(),
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
    
    // Wait for dashboard to load
    await popup.waitForTimeout(5000);
    
    // Test potential invoice URLs
    const urlsToTest = [
      '/TFBFTZ/factura/list.cl?language=es',
      '/TFBFTZ/invoice/list.cl?language=es',
      '/TFBFTZ/facturas/list.cl?language=es',
      '/TFBFTZ/invoices/list.cl?language=es',
      '/TFBFTZ/tfbftz/factura/list.cl?language=es',
      '/TFBFTZ/factura/manage.cl?language=es',
      '/TFBFTZ/invoice/manage.cl?language=es',
      '/TFBFTZ/facturas/manage.cl?language=es',
      '/TFBFTZ/dmce/list.cl?language=es',
      '/TFBFTZ/dmce/manage.cl?language=es',
      '/TFBFTZ/dmce/factura.cl?language=es'
    ];
    
    console.log('Testing potential invoice URLs...');
    
    for (const urlPath of urlsToTest) {
      const fullUrl = 'https://dmce2.zonalibredecolon.gob.pa' + urlPath;
      console.log(`Testing URL: ${fullUrl}`);
      
      try {
        const response = await popup.goto(fullUrl, { timeout: 10000 });
        console.log(`Status: ${response.status()}, URL: ${popup.url()}`);
        
        if (response.status() === 200) {
          console.log('SUCCESS: URL returned 200 OK');
          await popup.screenshot({ path: `url_test_${urlPath.replace(/\//g, '_').replace(/\?/g, '_')}.png` });
          
          // Check for table elements that might contain invoices
          const tables = await popup.$$eval('table', tables => 
            tables.map((table, i) => ({
              index: i,
              id: table.id,
              class: table.className,
              rows: table.rows.length
            }))
          );
          
          console.log('Tables found:', tables);
          
          if (tables.length > 0) {
            console.log('POTENTIAL INVOICE PAGE: Contains tables');
          }
        }
      } catch (e) {
        console.log(`Error: ${e.message}`);
      }
      
      await popup.waitForTimeout(1000);
    }
    
    // Try to find invoice-related menu items
    console.log('Looking for invoice-related menu items...');
    await popup.goto('https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/TFB.jsp?language=es', { timeout: 30000 });
    await popup.waitForTimeout(10000);
    
    const menuItems = await popup.$$eval('a, button, .menu-item, li, div[onclick]', items => 
      items.map(item => ({
        text: item.innerText.trim(),
        href: item.href || '',
        id: item.id,
        class: item.className,
        onclick: item.getAttribute('onclick') || ''
      }))
    );
    
    const invoiceMenuItems = menuItems.filter(item => 
      item.text.toLowerCase().includes('factura') || 
      item.text.toLowerCase().includes('invoice') ||
      (item.href && item.href.toLowerCase().includes('factura')) ||
      (item.href && item.href.toLowerCase().includes('invoice')) ||
      (item.onclick && item.onclick.toLowerCase().includes('factura')) ||
      (item.onclick && item.onclick.toLowerCase().includes('invoice'))
    );
    
    console.log('Potential invoice menu items:', invoiceMenuItems);
    
    if (invoiceMenuItems.length > 0) {
      console.log('SUCCESS: Found potential invoice menu items');
      await popup.screenshot({ path: 'dashboard_with_menu_items.png' });
    }
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();
