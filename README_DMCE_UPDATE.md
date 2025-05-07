# DMCE Portal Automation for Cortana

This component of the Cortana application automates the DMCE (Declaración de Movimiento Comercial Electrónico) portal login and invoice automation process using Playwright with Firefox in private browsing mode.

## Overview

The DMCE automation module provides a headless browser solution for:
- Logging into the DMCE portal
- Navigating to invoice functionality
- Automating invoice processing

## Prerequisites

- Node.js (v14 or higher)
- Firefox browser
- Playwright

## Installation

```bash
# Install dependencies
npm install playwright playwright-extra playwright-extra-plugin-stealth
npx playwright install firefox
```

## Configuration

Set your DMCE credentials as environment variables:

```bash
export DMCE_USER="your_username"
export DMCE_PASS="your_password"
```

## Usage

```bash
# Run the automation script
node popup_handling_stealth_login.js
```

## Implementation Details

The automation script:
1. Launches Firefox in private browsing mode
2. Navigates to the DMCE login page
3. Handles popup windows and login form
4. Extracts hidden form fields for proper authentication
5. Submits credentials programmatically
6. Navigates the dashboard to find invoice functionality
7. Records video, screenshots, and trace data for debugging

## Evidence Collection

The script collects comprehensive evidence:
- Videos: Recorded in the `./videos/` directory
- Screenshots: Captured at key steps in the `./screenshots/` directory
- Logs: Console output and HTML content in the `./logs/` directory
- Trace: Playwright trace file for detailed debugging

## Current Status

The automation successfully:
- Sets up the environment with required dependencies
- Logs in to the DMCE portal with provided credentials
- Handles popup windows and dashboard loading

Further manual exploration is required to:
- Identify the correct navigation path to invoice functionality
- Determine the exact URL and selectors for invoice list
- Implement the invoice automation process

## Next Steps

1. Perform manual exploration to map the exact navigation path
2. Update the script with the correct navigation sequence
3. Implement robust error handling for each navigation step
4. Test the updated script with real invoice data

## Files

- `popup_handling_stealth_login.js`: Main automation script with popup handling
- `hardened_stealth_login.js`: Alternative script with retry mechanisms
- `dmce_automation_evidence.tar.gz`: Package containing all evidence files
- `final_dmce_report.md`: Comprehensive report of automation results
