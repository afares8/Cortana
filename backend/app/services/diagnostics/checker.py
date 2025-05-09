import logging
import os
import psutil
import platform
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from app.services.diagnostics.docker_monitor import get_container_status, check_model_container_health

logger = logging.getLogger(__name__)

async def check_system_resources() -> Dict[str, Any]:
    """
    Check system resources like CPU, memory, and disk usage.
    
    Returns:
        Dict[str, Any]: System resource information
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = "healthy"
        warnings = []
        
        if cpu_percent > 90:
            status = "error"
            warnings.append("CPU usage critical (>90%)")
        elif cpu_percent > 75:
            status = "warning"
            warnings.append("CPU usage high (>75%)")
            
        if memory.percent > 90:
            status = "error"
            warnings.append("Memory usage critical (>90%)")
        elif memory.percent > 75:
            status = "warning"
            warnings.append("Memory usage high (>75%)")
            
        if disk.percent > 90:
            status = "error"
            warnings.append("Disk usage critical (>90%)")
        elif disk.percent > 75:
            status = "warning"
            warnings.append("Disk usage high (>75%)")
            
        return {
            "component": "system_resources",
            "status": status,
            "description": "System resources check",
            "timestamp": datetime.utcnow(),
            "details": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "platform": platform.platform(),
                "processor": platform.processor(),
                "warnings": warnings
            }
        }
    except Exception as e:
        logger.error(f"Error checking system resources: {e}")
        return {
            "component": "system_resources",
            "status": "error",
            "description": "System resources check failed",
            "timestamp": datetime.utcnow(),
            "error_details": {
                "error": str(e)
            }
        }

async def check_docker_services() -> List[Dict[str, Any]]:
    """
    Check the status of all Docker services.
    
    Returns:
        List[Dict[str, Any]]: List of Docker service statuses
    """
    try:
        containers = await get_container_status()
        results = []
        
        for container in containers:
            status = "healthy"
            if container["health_status"] == "error":
                status = "error"
            elif container["health_status"] == "warning":
                status = "warning"
                
            results.append({
                "component": f"docker_{container['name']}",
                "status": status,
                "description": f"Docker container: {container['name']}",
                "timestamp": datetime.utcnow(),
                "details": container
            })
            
        return results
    except Exception as e:
        logger.error(f"Error checking Docker services: {e}")
        return [{
            "component": "docker_services",
            "status": "error",
            "description": "Docker services check failed",
            "timestamp": datetime.utcnow(),
            "error_details": {
                "error": str(e)
            }
        }]

async def check_ai_service() -> Dict[str, Any]:
    """
    Check the AI service status.
    
    Returns:
        Dict[str, Any]: AI service status
    """
    try:
        status, error_message = await check_model_container_health()
        
        result = {
            "component": "ai_service",
            "status": status,
            "description": "AI service status check",
            "timestamp": datetime.utcnow(),
            "details": {
                "service_type": "Mistral 7B"
            }
        }
        
        if error_message:
            result["error_details"] = {"error": error_message}
            
        return result
    except Exception as e:
        logger.error(f"Error checking AI service: {e}")
        return {
            "component": "ai_service",
            "status": "error",
            "description": "AI service check failed",
            "timestamp": datetime.utcnow(),
            "error_details": {
                "error": str(e)
            }
        }

async def check_database() -> Dict[str, Any]:
    """
    Check the database status.
    
    Returns:
        Dict[str, Any]: Database status
    """
    try:
        db_path = os.path.join("app", "data")
        if not os.path.exists(db_path):
            return {
                "component": "database",
                "status": "error",
                "description": "Database directory not found",
                "timestamp": datetime.utcnow(),
                "error_details": {
                    "error": f"Directory not found: {db_path}"
                }
            }
            
        test_file_path = os.path.join(db_path, ".diagnostics_test")
        try:
            with open(test_file_path, "w") as f:
                f.write("test")
            os.remove(test_file_path)
            
            return {
                "component": "database",
                "status": "healthy",
                "description": "Database check",
                "timestamp": datetime.utcnow(),
                "details": {
                    "db_path": db_path,
                    "is_writable": True
                }
            }
        except Exception as e:
            return {
                "component": "database",
                "status": "warning",
                "description": "Database directory not writable",
                "timestamp": datetime.utcnow(),
                "error_details": {
                    "error": str(e)
                }
            }
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        return {
            "component": "database",
            "status": "error",
            "description": "Database check failed",
            "timestamp": datetime.utcnow(),
            "error_details": {
                "error": str(e)
            }
        }

async def run_all_checks() -> List[Dict[str, Any]]:
    """
    Run all diagnostic checks.
    
    Returns:
        List[Dict[str, Any]]: List of all check results
    """
    try:
        resources_check = await check_system_resources()
        docker_checks = await check_docker_services()
        ai_check = await check_ai_service()
        db_check = await check_database()
        
        results = [resources_check, ai_check, db_check] + docker_checks
        return results
    except Exception as e:
        logger.error(f"Error running all checks: {e}")
        return [{
            "component": "diagnostics",
            "status": "error",
            "description": "Error running diagnostic checks",
            "timestamp": datetime.utcnow(),
            "error_details": {
                "error": str(e)
            }
        }]
