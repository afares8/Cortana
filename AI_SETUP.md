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
The system will automatically detect if GPU is not available and use fallback mode:
- Provides pre-defined responses for common legal queries
- Clearly indicates when responses are fallbacks
- No special hardware requirements

## Configuration Options

The `docker-compose.yml` file is designed to work in both GPU and non-GPU environments:

1. **Auto-detection (Default)**
   - The system automatically detects if GPU is available
   - Uses the real model when GPU is present
   - Falls back to CPU mode when GPU is not available

2. **Manual Override**
   - You can manually set fallback mode by uncommenting and setting the `AI_FALLBACK_MODE` environment variable in `docker-compose.yml`:
     ```yaml
     # Force fallback mode regardless of GPU availability
     - AI_FALLBACK_MODE=true
     
     # Force real model usage (requires GPU)
     - AI_FALLBACK_MODE=false
     ```

## Starting the Services

```bash
# Stop any running services
docker compose down

# Start services with the updated configuration
docker compose up --build -d
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
   docker compose logs ai-service
   ```
   Monitor for any errors or warnings in the AI service.

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
1. Verify the AI service is running: `docker ps | grep ai-service`
2. Check the AI service logs: `docker compose logs ai-service`
3. Ensure the URL is correct: `MISTRAL_API_URL=http://ai-service:80`
