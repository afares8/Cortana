import os
import logging

logger = logging.getLogger(__name__)

def ensure_storage_directories():
    """
    Ensures that all required storage directories for the accounting module exist.
    This is called during application startup to prepare the environment.
    """
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
    
    required_dirs = [
        os.path.join(base_dir, "storage", "forms"),
        os.path.join(base_dir, "storage", "attachments"),
        os.path.join(base_dir, "static", "templates"),
    ]
    
    for directory in required_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Storage directory ensured: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
    
    logger.info("All accounting storage directories verified")
