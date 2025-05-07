/**
 * DMCE Environment Variables Example
 * 
 * This file shows all the environment variables required for the DMCE full process automation.
 * Copy this file to .env and fill in the values for your specific declaration.
 */

DMCE_USER=your_username
DMCE_PASS=your_password

DMCE_INVOICE_ID=INV12345
DMCE_DATE=2025-05-07
DMCE_CUSTOMER_CODE=CUST001

DMCE_GOODS_DESCRIPTION=Electronic components
DMCE_QUANTITY=100
DMCE_WEIGHT_KG=250.5
DMCE_VOLUME_M3=1.2

DMCE_TRANSPORT_TYPE=AIR  // Options: AIR, SEA, LAND
DMCE_FLIGHT_NUMBER=AA123  // Only if TRANSPORT_TYPE is AIR
DMCE_CARRIER_NAME=American Airlines  // Only if TRANSPORT_TYPE is AIR

DMCE_HS_CODE=8517.62.00
DMCE_ORIGIN_COUNTRY=US
DMCE_DESTINATION_COUNTRY=PA
DMCE_DECLARED_VALUE=5000
DMCE_VALUE_CURRENCY=USD

DMCE_COMMERCIAL_INVOICE_PATH=/path/to/invoice.pdf
DMCE_PACKING_LIST_PATH=/path/to/packing_list.pdf

DMCE_DOWNLOAD_DIR=/path/to/download/directory
