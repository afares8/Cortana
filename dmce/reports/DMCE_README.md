# DMCE Portal Automation

This component of the Cortana application automates the DMCE (Declaración de Movimiento Comercial Electrónico) portal login and invoice automation process using Playwright with Firefox in private browsing mode.

## Prerequisites

- Node.js (v14 or higher)
- Firefox browser

## Installation

```bash
npm install
```

This will install the required dependencies:
- playwright
- playwright-extra
- playwright-extra-plugin-stealth

## Configuration

Set your DMCE credentials as environment variables:

```bash
export DMCE_USER="your_username"
export DMCE_PASS="your_password"
```

Alternatively, the script will use the default test credentials if environment variables are not set.

## Usage

```bash
node updated_stealth_login.js
```

## Important Notes

Before running the script, you need to update the following placeholders in `updated_stealth_login.js`:

1. **Invoice URL**: Replace the placeholder URL with the correct invoice page URL:
   ```javascript
   // Replace this:
   await popup.goto('https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/REAL/INVOICE/PATH?language=es');
   
   // With the actual URL found during manual exploration, for example:
   await popup.goto('https://dmce2.zonalibredecolon.gob.pa/TFBFTZ/invoice/list.cl?language=es');
   ```

2. **Invoice List Selector**: Replace the placeholder selector with the correct invoice table selector:
   ```javascript
   // Replace this:
   await popup.waitForSelector('table.invoice-table tbody tr');
   
   // With the actual selector found during manual exploration, for example:
   await popup.waitForSelector('#invoiceGrid table tbody tr');
   ```

3. **Invoice ID Extraction**: Update the selector and attribute for extracting invoice IDs:
   ```javascript
   // Replace this:
   const invoiceIds = await popup.$$eval(
     'table.invoice-table tbody tr',
     rows => rows.slice(0, 3).map(r => r.getAttribute('data-invoice-id') || r.id || r.innerText)
   );
   
   // With the actual selector and attribute found during manual exploration, for example:
   const invoiceIds = await popup.$$eval(
     '#invoiceGrid table tbody tr',
     rows => rows.slice(0, 3).map(r => r.getAttribute('data-row-id'))
   );
   ```

4. **Automation Button Selector**: Replace the placeholder selector with the correct button selector:
   ```javascript
   // Replace this:
   await popup.click('#automate-all-btn');
   
   // With the actual selector found during manual exploration, for example:
   await popup.click('button.automation-trigger');
   ```

5. **Completion Indicator Selector**: Replace the placeholder selector with the correct completion indicator:
   ```javascript
   // Replace this:
   await popup.waitForSelector('#automation-complete');
   
   // With the actual selector found during manual exploration, for example:
   await popup.waitForSelector('.success-message');
   ```

## Output Files

The script generates the following output files:

- **Videos**: Recorded in the `./videos/` directory
- **Trace**: Saved as `trace.zip` for debugging
- **Screenshots**: Captured at key steps of the automation process
- **Error Page**: HTML content saved as `error_page.html` if an error occurs

## Troubleshooting

If the script fails:

1. Check the error message in the console output
2. Examine the screenshots to see where the process failed
3. Review the trace file for detailed execution information
4. Verify that the selectors and URLs have been correctly updated
5. Ensure the DMCE portal is accessible and your credentials are valid

## Manual URL and Selector Discovery

If you need to manually discover the correct URL and selectors:

1. Log in to the DMCE portal with your credentials
2. Open browser DevTools (F12) and go to the Network tab
3. Clear the network log and enable "Preserve log"
4. Navigate to the invoice section through the UI
5. Note the URL in the address bar and any network requests
6. Use the Elements tab to inspect the invoice list and automation buttons
7. Update the script with the correct URL and selectors

## Testing with Sample Data

Use your staging dataset for testing:
- Ideally, use a small set of 'test' invoices in your DMCE environment (e.g., IDs 1001, 1002, 1003) that are in a "pending" state
- If no dedicated test data exists, automate against the first 2-3 invoices that show up in the list
- Consider implementing cleanup functionality to restore original status or delete test entries

## Firefox Compatibility

The DMCE portal works reliably in Mozilla Firefox, specifically in Private Browsing mode. The script is configured to:
- Use Firefox with private browsing mode
- Avoid headless mode to prevent detection
- Set appropriate locale and timezone settings for Panama
