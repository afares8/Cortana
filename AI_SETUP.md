# AI Command Center Setup Guide

This guide explains how to set up and use the AI Command Center with the Mistral 7B model in different environments.

## Environment Requirements

### GPU Environment (Recommended)
For optimal performance with the Mistral 7B model:
- NVIDIA GPU with CUDA support (RTX 3090 Ti or similar)
- CUDA 12.x installed
- nvidia-container-toolkit installed and configured
- Docker with GPU support enabled

### CPU-only Environment (Fallback)
The system will automatically use fallback mode in CPU-only environments:
- Provides pre-defined responses for common legal queries
- Clearly indicates when responses are fallbacks
- No special hardware requirements

## Using Docker Compose Profiles

The `docker-compose.yml` file now uses Docker Compose profiles to select the appropriate AI service based on your environment:

### For GPU Environments (with NVIDIA GPU)

```bash
# Set the COMPOSE_PROFILES environment variable to 'gpu'
export COMPOSE_PROFILES=gpu

# Stop any running services
docker compose down

# Start services with GPU support
docker compose up --build -d
```

### For CPU-only Environments (or when GPU is not available)

```bash
# Set the COMPOSE_PROFILES environment variable to 'cpu'
export COMPOSE_PROFILES=cpu

# Stop any running services
docker compose down

# Start services in CPU-only mode
docker compose up --build -d
```

If you don't specify a profile, the system will default to CPU mode:

```bash
# No profile specified, defaults to CPU mode
docker compose up --build -d
```

## Additional Configuration Options

You can also manually override the fallback mode by setting the `AI_FALLBACK_MODE` environment variable in `docker-compose.yml`:

```yaml
# Force fallback mode regardless of GPU availability
- AI_FALLBACK_MODE=true

# Force real model usage (requires GPU)
- AI_FALLBACK_MODE=false
```

## Verifying the Setup

1. **Check AI Service Health**
   ```bash
   curl http://localhost:8080/health
   ```
   Should return `{"status":"ok"}` if the service is running.

2. **Test the Mistral Model**
   ```bash
   curl http://localhost:8000/api/v1/test-mistral
   ```
   This will show detailed information about:
   - Whether the real model or fallback is being used
   - System hardware information
   - Connection status to the AI service
   - Recommendations based on your environment

3. **Check Container Logs**
   ```bash
   # For GPU mode
   docker compose logs ai-service-gpu
   
   # For CPU mode
   docker compose logs ai-service-cpu
   ```

## Troubleshooting

### GPU Not Detected
If you have a GPU but it's not being detected:
1. Verify NVIDIA drivers are installed: `nvidia-smi`
2. Check nvidia-container-toolkit is installed: `dpkg -l | grep nvidia-container-toolkit`
3. Ensure Docker can access GPU: `docker run --rm --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi`

### Model Loading Errors
If the AI service starts but fails to load the model:
1. Check if you have enough GPU memory (at least 16GB recommended)
2. Try a different quantization setting (e.g., change `QUANTIZE=q4_k_m` to `QUANTIZE=q8_0`)
3. Increase the container memory limit if needed

### Connection Issues
If the backend can't connect to the AI service:
1. Verify the correct AI service is running based on your profile:
   - GPU mode: `docker ps | grep ai-service-gpu`
   - CPU mode: `docker ps | grep ai-service-cpu`
2. Check the AI service logs for the appropriate service
3. Ensure the URL is correct: `MISTRAL_API_URL=http://ai-service:80`
4. Verify that AI_FALLBACK_MODE is set correctly:
   - For GPU environments: `AI_FALLBACK_MODE=false`
   - For CPU environments: `AI_FALLBACK_MODE=true` or leave unset
5. Check for DNS resolution errors in the logs, which may indicate network configuration issues

### Fallback Mode Troubleshooting
If the system is unexpectedly falling back to CPU mode:
1. Check if AI_FALLBACK_MODE is explicitly set in your environment
2. Verify GPU detection is working correctly with `nvidia-smi`
3. Examine the logs for connection errors to the AI service
4. Use the test endpoint to diagnose issues: `curl http://localhost:8000/api/v1/test-mistral`
5. Run the validation script to check both endpoints:
   ```bash
   cd backend
   python -m app.scripts.test_mistral_integration
   ```
6. Ensure all required Python dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

## Recent Updates

### May 2025
- Improved health-check logic to better handle DNS resolution errors and prevent unnecessary fallback to CPU mode
- Added detailed logging for connection attempts and failures to aid in troubleshooting
- Enhanced error handling in Spanish language pipeline to avoid triggering fallback mode unnecessarily
- Added test script (`app.scripts.test_mistral_integration`) to validate Mistral AI integration
- Updated CI configuration to include smoke tests for Mistral endpoints
