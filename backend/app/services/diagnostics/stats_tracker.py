import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)

LOG_FILE_PATH = os.path.join("app", "data", "diagnostics_log.json")

async def log_diagnostic_run(diagnostic_items: List[Dict[str, Any]]) -> bool:
    """
    Log a diagnostic run to the diagnostics log file.
    
    Args:
        diagnostic_items: List of diagnostic items
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        
        log_data = []
        if os.path.exists(LOG_FILE_PATH):
            try:
                with open(LOG_FILE_PATH, "r") as f:
                    log_data = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from {LOG_FILE_PATH}, creating new log")
                log_data = []
        
        serializable_items = []
        for item in diagnostic_items:
            serializable_item = item.copy()
            if "timestamp" in serializable_item and isinstance(serializable_item["timestamp"], datetime):
                serializable_item["timestamp"] = serializable_item["timestamp"].isoformat()
            serializable_item["log_id"] = str(uuid.uuid4())
            serializable_item["created_at"] = datetime.utcnow().isoformat()
            serializable_items.append(serializable_item)
        
        log_data.extend(serializable_items)
        
        if len(log_data) > 1000:
            log_data = log_data[-1000:]
        
        with open(LOG_FILE_PATH, "w") as f:
            json.dump(log_data, f, indent=2)
        
        return True
        
    except Exception as e:
        logger.error(f"Error logging diagnostic run: {e}")
        return False

async def get_diagnostic_history() -> List[Dict[str, Any]]:
    """
    Get the diagnostic history from the log file.
    
    Returns:
        List[Dict[str, Any]]: List of diagnostic log items
    """
    try:
        if not os.path.exists(LOG_FILE_PATH):
            return []
            
        with open(LOG_FILE_PATH, "r") as f:
            log_data = json.load(f)
            
        return log_data
        
    except Exception as e:
        logger.error(f"Error getting diagnostic history: {e}")
        return []

async def get_component_history(component: str) -> List[Dict[str, Any]]:
    """
    Get the diagnostic history for a specific component.
    
    Args:
        component: Name of the component
        
    Returns:
        List[Dict[str, Any]]: List of diagnostic log items for the component
    """
    try:
        history = await get_diagnostic_history()
        component_history = [item for item in history if item.get("component") == component]
        return component_history
        
    except Exception as e:
        logger.error(f"Error getting component history for {component}: {e}")
        return []

async def get_diagnostic_stats() -> Dict[str, Any]:
    """
    Get statistics about the diagnostic history.
    
    Returns:
        Dict[str, Any]: Diagnostic statistics
    """
    try:
        history = await get_diagnostic_history()
        
        if not history:
            return {
                "total_runs": 0,
                "healthy_count": 0,
                "warning_count": 0,
                "error_count": 0,
                "components_checked": [],
                "last_run": None,
                "history": {}
            }
        
        healthy_count = sum(1 for item in history if item.get("status") == "healthy")
        warning_count = sum(1 for item in history if item.get("status") == "warning")
        error_count = sum(1 for item in history if item.get("status") == "error")
        
        components = list(set(item.get("component") for item in history if "component" in item))
        
        last_run = max((datetime.fromisoformat(item["created_at"]) 
                       for item in history if "created_at" in item and isinstance(item["created_at"], str)), 
                       default=datetime.min)
        
        component_history = {}
        for component in components:
            component_items = [item for item in history if item.get("component") == component]
            component_history[component] = component_items[-10:]  # Last 10 entries
        
        return {
            "total_runs": len(set(item.get("log_id") for item in history if "log_id" in item)),
            "healthy_count": healthy_count,
            "warning_count": warning_count,
            "error_count": error_count,
            "components_checked": components,
            "last_run": last_run.isoformat() if last_run != datetime.min else None,
            "history": component_history
        }
        
    except Exception as e:
        logger.error(f"Error getting diagnostic stats: {e}")
        return {
            "total_runs": 0,
            "healthy_count": 0,
            "warning_count": 0,
            "error_count": 0,
            "components_checked": [],
            "last_run": None,
            "history": {},
            "error": str(e)
        }
