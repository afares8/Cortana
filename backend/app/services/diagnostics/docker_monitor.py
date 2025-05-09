import logging
import subprocess
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

async def get_container_status() -> List[Dict[str, Any]]:
    """
    Get the status of all Docker containers.
    
    Returns:
        List[Dict[str, Any]]: List of container status information
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Image}}|{{.RunningFor}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
                
            parts = line.split('|')
            if len(parts) < 4:
                continue
                
            name, status, image, running_for = parts[:4]
            
            health_status = "healthy"
            if "unhealthy" in status.lower():
                health_status = "error"
            elif "starting" in status.lower() or "restarting" in status.lower():
                health_status = "warning"
            
            containers.append({
                "name": name,
                "status": status,
                "health_status": health_status,
                "image": image,
                "running_for": running_for,
            })
        
        return containers
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting container status: {e}")
        logger.error(f"STDERR: {e.stderr}")
        return [{
            "name": "docker",
            "status": "Error running docker command",
            "health_status": "error",
            "image": "N/A",
            "running_for": "N/A",
            "error": str(e),
        }]
    except Exception as e:
        logger.error(f"Unexpected error getting container status: {e}")
        return [{
            "name": "docker",
            "status": "Unexpected error",
            "health_status": "error",
            "image": "N/A",
            "running_for": "N/A",
            "error": str(e),
        }]

async def get_container_logs(container_name: str, lines: int = 50) -> str:
    """
    Get the logs for a specific container.
    
    Args:
        container_name: Name of the container
        lines: Number of lines to retrieve
        
    Returns:
        str: Container logs
    """
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(lines), container_name],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting logs for container {container_name}: {e}")
        return f"Error getting logs: {e.stderr}"
    except Exception as e:
        logger.error(f"Unexpected error getting logs for container {container_name}: {e}")
        return f"Unexpected error getting logs: {str(e)}"

async def check_model_container_health() -> Tuple[str, Optional[str]]:
    """
    Check the health of the AI model container.
    
    Returns:
        Tuple[str, Optional[str]]: (status, error_message)
    """
    try:
        containers = await get_container_status()
        ai_containers = [c for c in containers if "ai-service" in c["name"].lower() or "mistral" in c["name"].lower()]
        
        if not ai_containers:
            return "error", "AI service container not found"
            
        container = ai_containers[0]
        if container["health_status"] == "error":
            logs = await get_container_logs(container["name"])
            return "error", f"AI service container is unhealthy: {logs}"
        elif container["health_status"] == "warning":
            return "warning", "AI service container is in transitional state"
        else:
            return "healthy", None
            
    except Exception as e:
        logger.error(f"Error checking model container health: {e}")
        return "error", f"Error checking model container health: {str(e)}"
