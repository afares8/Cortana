from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, AnyHttpUrl, validator

class DueDiligenceLevel(str, Enum):
    SIMPLIFIED = "simplified"
    BASIC = "basic"
    ENHANCED = "enhanced"

class BrowserType(str, Enum):
    FIREFOX = "firefox"
    CHROMIUM = "chromium"

class BrowserMode(str, Enum):
    HEADLESS = "headless"
    MANUAL_FALLBACK = "manual_fallback"

class LanguageMode(str, Enum):
    AUTO_DETECT = "auto_detect"
    FORCE_SPANISH = "force_spanish"

class AIModel(str, Enum):
    MISTRAL_7B = "mistral_7b"
    OPEN_HERMES = "open_hermes"

class ModuleConfig(BaseModel):
    enabled: bool = True
    order: int = 0

class PasswordPolicy(BaseModel):
    min_length: int = 8
    require_symbols: bool = True
    require_numbers: bool = True

class GeneralSettings(BaseModel):
    system_name: str = "Cortana"
    logo_url: Optional[str] = None
    default_language: str = "es"
    timezone: str = "America/Panama"

class MenuLayoutSettings(BaseModel):
    modules: Dict[str, ModuleConfig] = Field(
        default_factory=lambda: {
            "legal": ModuleConfig(enabled=True, order=1),
            "compliance": ModuleConfig(enabled=True, order=2),
            "accounting": ModuleConfig(enabled=True, order=3),
            "traffic": ModuleConfig(enabled=True, order=4),
            "ai": ModuleConfig(enabled=True, order=5),
            "users": ModuleConfig(enabled=True, order=6)
        }
    )
    dark_mode: bool = False

class AISettings(BaseModel):
    language_mode: LanguageMode = LanguageMode.AUTO_DETECT
    fallback_mode: bool = True
    model: AIModel = AIModel.MISTRAL_7B
    max_tokens: int = 500
    debug_mode: bool = False
    health_check_schedule: str = "0 0 * * *"  # Daily at midnight

class ComplianceSettings(BaseModel):
    sanctions_sources: Dict[str, bool] = Field(
        default_factory=lambda: {
            "ofac": True,
            "un": True,
            "eu": False,
            "open_sanctions": True
        }
    )
    uaf_report_automation: bool = True
    default_due_diligence: DueDiligenceLevel = DueDiligenceLevel.BASIC
    document_retention_months: int = 60
    basel_fatf_update_schedule: str = "0 0 1 * *"  # Monthly on the 1st

class SecuritySettings(BaseModel):
    enforce_2fa: bool = False
    session_timeout_minutes: int = 60
    max_failed_logins: int = 5
    password_policy: PasswordPolicy = Field(default_factory=PasswordPolicy)

class DMCESettings(BaseModel):
    enable_automation: bool = True
    default_customs_company: Optional[str] = None
    browser: BrowserType = BrowserType.FIREFOX
    browser_mode: BrowserMode = BrowserMode.MANUAL_FALLBACK
    login_timeout_seconds: int = 30

class IntegrationSettings(BaseModel):
    sap_endpoint: Optional[AnyHttpUrl] = None
    sap_api_key: Optional[str] = None
    risk365_endpoint: Optional[AnyHttpUrl] = None
    risk365_auth: Optional[str] = None
    webhooks: List[AnyHttpUrl] = []
    slack_webhook: Optional[AnyHttpUrl] = None

class SystemSettingsSchema(BaseModel):
    general: GeneralSettings = Field(default_factory=GeneralSettings)
    menu_layout: MenuLayoutSettings = Field(default_factory=MenuLayoutSettings)
    ai: AISettings = Field(default_factory=AISettings)
    compliance: ComplianceSettings = Field(default_factory=ComplianceSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    dmce: DMCESettings = Field(default_factory=DMCESettings)
    integrations: IntegrationSettings = Field(default_factory=IntegrationSettings)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "general": {
                    "system_name": "Cortana",
                    "logo_url": None,
                    "default_language": "es",
                    "timezone": "America/Panama"
                },
                "menu_layout": {
                    "modules": {
                        "legal": {"enabled": True, "order": 1},
                        "compliance": {"enabled": True, "order": 2}
                    },
                    "dark_mode": False
                }
            }
        }
