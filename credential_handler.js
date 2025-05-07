require('dotenv').config({ path: './config/.env' });

function getDMCECredentials() {
  const username = process.env.DMCE_USER;
  const password = process.env.DMCE_PASS;
  
  if (!username || !password) {
    throw new Error('DMCE credentials not found in environment variables. Please set DMCE_USER and DMCE_PASS in config/.env file.');
  }
  
  return { username, password };
}

module.exports = {
  getDMCECredentials
};
