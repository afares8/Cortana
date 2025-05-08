import json
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.db.init_db import system_settings_db
from app.models.settings import SystemSetting, SystemSettingInDB
from app.schemas.system_settings import SystemSettingsSchema

SETTINGS_FILE = "app/data/config.json"
logger = logging.getLogger(__name__)

class SystemSettingsService:
    @staticmethod
    def _get_from_file() -> SystemSettingsSchema:
        """Get system settings from file or create default if not exists"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as f:
                    settings_data = json.load(f)
                    return SystemSettingsSchema(**settings_data)
            else:
                return SystemSettingsSchema()
        except Exception as e:
            logger.error(f"Error loading settings from file: {str(e)}")
            return SystemSettingsSchema()
    
    @staticmethod
    def _save_to_file(settings: SystemSettingsSchema) -> None:
        """Save system settings to file as backup"""
        try:
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            
            with open(SETTINGS_FILE, "w") as f:
                f.write(settings.json(indent=2))
        except Exception as e:
            logger.error(f"Error saving settings to file: {str(e)}")
    
    @staticmethod
    def _settings_to_db_models(settings: SystemSettingsSchema) -> List[SystemSetting]:
        """Convert settings schema to database models"""
        models = []
        
        settings_dict = settings.dict()
        for category, category_data in settings_dict.items():
            if category in ["last_updated", "updated_by"]:
                continue
                
            if isinstance(category_data, dict):
                for key, value in category_data.items():
                    models.append(
                        SystemSetting(
                            category=category,
                            key=key,
                            value=value if isinstance(value, dict) else {"value": value}
                        )
                    )
            else:
                models.append(
                    SystemSetting(
                        category="metadata",
                        key=category,
                        value={"value": category_data}
                    )
                )
        
        return models
    
    @staticmethod
    def _db_models_to_settings(db_models: List[SystemSettingInDB]) -> SystemSettingsSchema:
        """Convert database models to settings schema"""
        settings_dict = SystemSettingsSchema().dict()
        
        for model in db_models:
            if model.category == "metadata":
                settings_dict[model.key] = model.value.get("value")
            else:
                if model.category not in settings_dict:
                    settings_dict[model.category] = {}
                
                if isinstance(model.value, dict) and "value" in model.value and len(model.value) == 1:
                    settings_dict[model.category][model.key] = model.value["value"]
                else:
                    settings_dict[model.category][model.key] = model.value
        
        return SystemSettingsSchema(**settings_dict)
    
    @staticmethod
    def get_settings() -> SystemSettingsSchema:
        """
        Get system settings from database with fallback to file.
        If database is empty, try to load from file and populate database.
        """
        try:
            db_settings = system_settings_db.get_multi()
            
            if db_settings:
                return SystemSettingsService._db_models_to_settings(db_settings)
            
            file_settings = SystemSettingsService._get_from_file()
            
            setting_models = SystemSettingsService._settings_to_db_models(file_settings)
            for model in setting_models:
                system_settings_db.create(obj_in=model)
            
            return file_settings
            
        except Exception as e:
            logger.error(f"Database error when loading settings: {str(e)}")
            return SystemSettingsService._get_from_file()
    
    @staticmethod
    def update_settings(settings: SystemSettingsSchema, user_id: Optional[str] = None) -> SystemSettingsSchema:
        """
        Update system settings in both database and file.
        If database update fails, still try to update the file.
        """
        try:
            settings.last_updated = datetime.utcnow()
            settings.updated_by = user_id
            
            setting_models = SystemSettingsService._settings_to_db_models(settings)
            
            existing_settings = system_settings_db.get_multi()
            for existing in existing_settings:
                system_settings_db.remove(id=existing.id)
            
            next_id = 1
            for model in setting_models:
                model_dict = model.dict()
                model_dict["id"] = next_id
                next_id += 1
                
                system_settings_db.create(obj_in=SystemSettingInDB(**model_dict))
            
            SystemSettingsService._save_to_file(settings)
            
            return settings
            
        except Exception as e:
            logger.error(f"Database error when updating settings: {str(e)}")
            
            SystemSettingsService._save_to_file(settings)
            
            raise e
