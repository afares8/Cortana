import os
import logging

logger = logging.getLogger(__name__)

def ensure_storage_directories():
    """
    Ensures that all required storage directories for the accounting module exist.
    This is called during application startup to prepare the environment.
    """
    required_dirs = [
        "/app/storage/forms",
        "/app/storage/attachments",
        "/app/static/templates",
    ]
    
    for directory in required_dirs:
        try:
            if os.path.exists("/app"):
                dir_path = directory
            else:
                dir_path = directory.replace("/app/", "")
            
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Storage directory ensured: {dir_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
    
    logger.info("All accounting storage directories verified")
