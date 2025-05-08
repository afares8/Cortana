import json
import os
from datetime import datetime
from typing import Optional

from app.schemas.system_settings import SystemSettingsSchema

SETTINGS_FILE = "app/data/system_settings.json"

class SystemSettingsService:
    @staticmethod
    def get_settings() -> SystemSettingsSchema:
        """Get system settings from file or create default if not exists"""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings_data = json.load(f)
                return SystemSettingsSchema(**settings_data)
        else:
            return SystemSettingsSchema()
    
    @staticmethod
    def update_settings(settings: SystemSettingsSchema, user_id: Optional[str] = None) -> SystemSettingsSchema:
        """Update system settings"""
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        
        settings.last_updated = datetime.utcnow()
        settings.updated_by = user_id
        
        with open(SETTINGS_FILE, "w") as f:
            f.write(settings.json(indent=2))
        
        return settings
