# DMCE Portal Automation for Cortana

This component of the Cortana application automates the DMCE (Declaración de Movimiento Comercial Electrónico) portal processes using Playwright with Firefox in private browsing mode.

## Overview

The DMCE automation module provides a comprehensive browser automation solution for:
- Logging into the DMCE portal
- Creating new declarations
- Filling all required form fields
- Uploading supporting documents
- Downloading declaration PDFs

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

Set your DMCE credentials and declaration data as environment variables:

```bash
# Copy the example environment file
cp config/.env.example config/.env

# Edit the .env file with your specific values
```

## Usage

```bash
# Run the login automation script
node stealth_traffic_login.js

# Run the full process automation script
node dmce_full_process_automation.js
```

## Implementation Details

The automation scripts:
1. Launch Firefox in private browsing mode
2. Navigate to the DMCE login page
3. Handle popup windows and login form
4. Extract hidden form fields for proper authentication
5. Submit credentials programmatically
6. Navigate to "Crear Declaración"
7. Fill all form sections (A-E)
8. Upload required documents
9. Submit the declaration
10. Download the PDF
11. Record video, screenshots, and trace data for debugging

## Evidence Collection

The scripts collect comprehensive evidence:
- Videos: Recorded in the `./videos/` directory
- Screenshots: Captured at key steps in the `./screenshots/` directory
- Logs: Console output and HTML content in the `./logs/` directory
- Trace: Playwright trace file for detailed debugging
- Downloads: Declaration PDFs in the `./downloads/` directory

## Environment Variables

The full process automation requires the following environment variables:

### Credentials
- `DMCE_USER`: Your DMCE username
- `DMCE_PASS`: Your DMCE password

### Declaration Data
- `DMCE_INVOICE_ID`: Invoice ID
- `DMCE_DATE`: Declaration date
- `DMCE_CUSTOMER_CODE`: Customer code
- `DMCE_GOODS_DESCRIPTION`: Description of goods
- `DMCE_QUANTITY`: Quantity
- `DMCE_WEIGHT_KG`: Weight in kilograms
- `DMCE_VOLUME_M3`: Volume in cubic meters
- `DMCE_TRANSPORT_TYPE`: Transport type (AIR, SEA, LAND)
- `DMCE_FLIGHT_NUMBER`: Flight number (for AIR transport)
- `DMCE_CARRIER_NAME`: Carrier name (for AIR transport)
- `DMCE_HS_CODE`: HS code
- `DMCE_ORIGIN_COUNTRY`: Origin country
- `DMCE_DESTINATION_COUNTRY`: Destination country
- `DMCE_DECLARED_VALUE`: Declared value
- `DMCE_VALUE_CURRENCY`: Currency for declared value
- `DMCE_COMMERCIAL_INVOICE_PATH`: Path to commercial invoice file
- `DMCE_PACKING_LIST_PATH`: Path to packing list file
- `DMCE_DOWNLOAD_DIR`: Directory to save downloaded files

## Files

- `stealth_traffic_login.js`: Basic login automation script
- `dmce_full_process_automation.js`: Complete declaration process automation
- `credential_handler.js`: Secure credential management
- `dmce_env_example.js`: Example environment variables
- `dmce_automation_evidence.tar.gz`: Package containing all evidence files
- `final_dmce_report.md`: Comprehensive report of automation results
