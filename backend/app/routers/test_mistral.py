from fastapi import APIRouter, HTTPException
import logging
import os
import platform
import psutil
import subprocess
import json
from app.services.ai.mistral_client import mistral_client

logger = logging.getLogger(__name__)
router = APIRouter()

def check_gpu_details():
    """Get detailed GPU information from the system."""
    gpu_info = {
        "has_gpu": False,
        "gpu_type": "none",
        "details": "No GPU detected"
    }
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info["has_gpu"] = True
            gpu_info["gpu_type"] = "cuda"
            device_count = torch.cuda.device_count()
            devices = []
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_capability = torch.cuda.get_device_capability(i)
                devices.append({
                    "index": i,
                    "name": device_name,
                    "compute_capability": f"{device_capability[0]}.{device_capability[1]}"
                })
            gpu_info["details"] = {
                "device_count": device_count,
                "devices": devices
            }
            return gpu_info
    except (ImportError, Exception) as e:
        logger.debug(f"Could not check CUDA via torch: {e}")
    
    try:
        if platform.system() == "Linux":
            result = subprocess.run(
                ["which", "nvidia-smi"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                nvidia_smi = subprocess.run(
                    ["nvidia-smi", "--query-gpu=index,name,memory.total,driver_version,compute_capability", "--format=csv,noheader"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if nvidia_smi.returncode == 0 and nvidia_smi.stdout.strip():
                    gpu_info["has_gpu"] = True
                    gpu_info["gpu_type"] = "nvidia"
                    
                    devices = []
                    for line in nvidia_smi.stdout.strip().split('\n'):
                        parts = [part.strip() for part in line.split(',')]
                        if len(parts) >= 5:
                            devices.append({
                                "index": parts[0],
                                "name": parts[1],
                                "memory": parts[2],
                                "driver": parts[3],
                                "compute_capability": parts[4]
                            })
                    
                    gpu_info["details"] = {
                        "device_count": len(devices),
                        "devices": devices
                    }
                    return gpu_info
    except Exception as e:
        logger.debug(f"Could not check NVIDIA GPU via system commands: {e}")
    
    try:
        if platform.system() == "Linux":
            result = subprocess.run(
                ["which", "rocm-smi"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                rocm_smi = subprocess.run(
                    ["rocm-smi", "--json"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if rocm_smi.returncode == 0 and rocm_smi.stdout.strip():
                    try:
                        rocm_data = json.loads(rocm_smi.stdout)
                        if rocm_data:
                            gpu_info["has_gpu"] = True
                            gpu_info["gpu_type"] = "amd"
                            gpu_info["details"] = rocm_data
                            return gpu_info
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        logger.debug(f"Could not check AMD GPU via system commands: {e}")
    
    return gpu_info

@router.get("/test-mistral")
async def test_mistral():
    """
    Test endpoint to verify if the Mistral 7B model is responding.
    Returns the raw response from the model for a simple prompt.
    """
    try:
        system_info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "cpu_count": psutil.cpu_count(logical=False),
            "logical_cpu_count": psutil.cpu_count(logical=True),
        }
        
        gpu_info = check_gpu_details()
        system_info.update(gpu_info)
        
        container_status = "unknown"
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=ai-service", "--format", "{{.Status}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                container_status = result.stdout.strip() or "not running"
        except Exception as e:
            container_status = f"Error checking container: {str(e)}"
        
        current_fallback_mode = mistral_client.fallback_mode
        fallback_env_var = os.environ.get("AI_FALLBACK_MODE", "")
        
        logger.info(f"Attempting to connect to Mistral model at: {mistral_client.base_url}")
        logger.info(f"Current fallback mode: {current_fallback_mode}")
        
        original_fallback_mode = mistral_client.fallback_mode
        mistral_client.fallback_mode = False
        
        try:
            response = await mistral_client.generate("What is a contract?")
            
            if isinstance(response, dict):
                response_text = response.get("generated_text", "")
                is_fallback = response.get("is_fallback", False) or "fallback response" in response_text.lower()
            else:
                response_text = str(response)
                is_fallback = "fallback response" in response_text.lower()
                
            connection_error = None
        except Exception as e:
            logger.error(f"Connection error: {e}")
            response_text = f"Connection error: {str(e)}"
            response = response_text  # Keep original variable for compatibility
            is_fallback = True
            connection_error = str(e)
        finally:
            mistral_client.fallback_mode = original_fallback_mode
        
        logger.info(f"Received response from Mistral model: {response_text[:100] if isinstance(response_text, str) else 'Non-string response'}...")
        
        hardware_requirements = {
            "gpu": "Required - NVIDIA GPU with CUDA support",
            "memory": "Minimum 16GB RAM",
            "disk": "Minimum 15GB free space for model weights",
            "special_requirements": "Flash Attention v2 support required for Mistral model"
        }
        
        environment_suitable = (
            gpu_info["has_gpu"] and 
            system_info["memory_gb"] >= 16 and
            (gpu_info["gpu_type"] == "nvidia" or gpu_info["gpu_type"] == "cuda")
        )
        
        # Generate recommendations based on environment
        if environment_suitable:
            recommendation = (
                "This environment appears suitable for running the Mistral 7B model. "
                "Make sure the AI service container is running properly."
            )
        else:
            missing_requirements = []
            if not gpu_info["has_gpu"]:
                missing_requirements.append("NVIDIA GPU with CUDA support")
            elif gpu_info["gpu_type"] not in ["nvidia", "cuda"]:
                missing_requirements.append(f"NVIDIA GPU (detected {gpu_info['gpu_type']} instead)")
            
            if system_info["memory_gb"] < 16:
                missing_requirements.append(f"16GB RAM (currently {system_info['memory_gb']}GB)")
            
            recommendation = (
                f"This environment is missing required hardware: {', '.join(missing_requirements)}. "
                "Continue using fallback mode or consider deploying on GPU-enabled infrastructure."
            )
        
        return {
            "response": response,
            "is_fallback": is_fallback,
            "model_url": mistral_client.base_url,
            "connection_successful": not is_fallback,
            "connection_error": connection_error,
            "system_info": system_info,
            "hardware_requirements": hardware_requirements,
            "environment_suitable": environment_suitable,
            "ai_service_container": container_status,
            "environment_config": {
                "fallback_mode_setting_from_env": fallback_env_var,
                "current_fallback_mode": current_fallback_mode,
                "auto_detection_active": fallback_env_var == "",
                "mistral_api_url": os.environ.get("MISTRAL_API_URL", "http://ai-service:80")
            },
            "recommendation": recommendation
        }
    except Exception as e:
        logger.error(f"Error testing Mistral model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test Mistral model: {str(e)}")
