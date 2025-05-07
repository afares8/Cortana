# DMCE Portal Automation - Secure Credential Setup

## Overview
This document explains how to securely set up credentials for the DMCE portal automation module.

## Configuration Steps

### 1. Create Environment File
Copy the example environment file to create your own:

```bash
cp config/.env.example config/.env
```

### 2. Set Your Credentials
Edit the `.env` file to add your DMCE portal credentials:

```
DMCE_USER=your_username
DMCE_PASS=your_password
```

### 3. Security Notes
- The `.env` file is excluded from git via `.gitignore`
- Never commit credentials to the repository
- The credential handler will validate that credentials are properly set

## Usage
The automation scripts automatically load credentials from the environment file:

```bash
# Run the automation script
node stealth_traffic_login.js
```

## Troubleshooting
If you encounter credential errors:
1. Verify that `config/.env` exists
2. Confirm that DMCE_USER and DMCE_PASS are set correctly
3. Check that the credentials are valid for the DMCE portal
