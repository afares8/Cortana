require('dotenv').config({ path: './config/.env' });

/**
 * Get DMCE credentials from environment variables
 * @returns {Object} Object containing username and password
 */
function getDMCECredentials() {
  const username = process.env.DMCE_USER;
  const password = process.env.DMCE_PASS;
  
  if (!username || !password) {
    throw new Error('DMCE credentials not found in environment variables. Please set DMCE_USER and DMCE_PASS in config/.env file.');
  }
  
  return { username, password };
}

/**
 * Get DMCE declaration data from environment variables
 * @returns {Object} Object containing all declaration form data
 */
function getDMCEDeclarationData() {
  const requiredVars = [
    'DMCE_INVOICE_ID',
    'DMCE_DATE',
    'DMCE_CUSTOMER_CODE',
    'DMCE_GOODS_DESCRIPTION',
    'DMCE_QUANTITY',
    'DMCE_WEIGHT_KG',
    'DMCE_VOLUME_M3',
    'DMCE_TRANSPORT_TYPE',
    'DMCE_HS_CODE',
    'DMCE_ORIGIN_COUNTRY',
    'DMCE_DESTINATION_COUNTRY',
    'DMCE_DECLARED_VALUE',
    'DMCE_VALUE_CURRENCY'
  ];
  
  const missingVars = requiredVars.filter(varName => !process.env[varName]);
  if (missingVars.length > 0) {
    throw new Error(`Missing required DMCE environment variables: ${missingVars.join(', ')}. Please set these in config/.env file.`);
  }
  
  if (process.env.DMCE_TRANSPORT_TYPE === 'AIR') {
    const airVars = ['DMCE_FLIGHT_NUMBER', 'DMCE_CARRIER_NAME'];
    const missingAirVars = airVars.filter(varName => !process.env[varName]);
    if (missingAirVars.length > 0) {
      throw new Error(`Missing required AIR transport variables: ${missingAirVars.join(', ')}. Please set these in config/.env file.`);
    }
  }
  
  return {
    invoiceId: process.env.DMCE_INVOICE_ID,
    date: process.env.DMCE_DATE,
    customerCode: process.env.DMCE_CUSTOMER_CODE,
    
    goodsDescription: process.env.DMCE_GOODS_DESCRIPTION,
    quantity: process.env.DMCE_QUANTITY,
    weightKg: process.env.DMCE_WEIGHT_KG,
    volumeM3: process.env.DMCE_VOLUME_M3,
    
    transportType: process.env.DMCE_TRANSPORT_TYPE,
    flightNumber: process.env.DMCE_FLIGHT_NUMBER,
    carrierName: process.env.DMCE_CARRIER_NAME,
    
    hsCode: process.env.DMCE_HS_CODE,
    originCountry: process.env.DMCE_ORIGIN_COUNTRY,
    destinationCountry: process.env.DMCE_DESTINATION_COUNTRY,
    declaredValue: process.env.DMCE_DECLARED_VALUE,
    valueCurrency: process.env.DMCE_VALUE_CURRENCY,
    
    commercialInvoicePath: process.env.DMCE_COMMERCIAL_INVOICE_PATH,
    packingListPath: process.env.DMCE_PACKING_LIST_PATH,
    
    downloadDir: process.env.DMCE_DOWNLOAD_DIR || './downloads'
  };
}

/**
 * Validate that all required environment variables are set
 * @returns {boolean} True if all required variables are set
 */
function validateDMCEEnvironment() {
  try {
    getDMCECredentials();
    getDMCEDeclarationData();
    return true;
  } catch (error) {
    console.error('DMCE environment validation failed:', error.message);
    return false;
  }
}

module.exports = {
  getDMCECredentials,
  getDMCEDeclarationData,
  validateDMCEEnvironment
};
