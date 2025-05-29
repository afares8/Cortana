import axios from 'axios';

const API_BASE_URL = '/api/v1';

export enum LanguageMode {
  AUTO_DETECT = 'auto_detect',
  FORCE_SPANISH = 'force_spanish'
}

export enum AIModel {
  MISTRAL_7B = 'mistral_7b',
  OPEN_HERMES = 'open_hermes'
}

export enum DueDiligenceLevel {
  SIMPLIFIED = 'simplified',
  BASIC = 'basic',
  ENHANCED = 'enhanced'
}

export enum BrowserType {
  FIREFOX = 'firefox',
  CHROMIUM = 'chromium'
}

export enum BrowserMode {
  HEADLESS = 'headless',
  MANUAL_FALLBACK = 'manual_fallback'
}

export interface GeneralSettings {
  system_name: string;
  logo_url: string | null;
  default_language: string;
  timezone: string;
}

export interface ModuleConfig {
  enabled: boolean;
  order: number;
}

export interface MenuLayoutSettings {
  modules: {
    [key: string]: ModuleConfig;
  };
  dark_mode: boolean;
}

export interface AISettings {
  language_mode: LanguageMode;
  fallback_mode: boolean;
  model: AIModel;
  max_tokens: number;
  debug_mode: boolean;
  health_check_schedule: string;
}

export interface ComplianceSettings {
  sanctions_sources: {
    ofac: boolean;
    un: boolean;
    eu: boolean;
    open_sanctions: boolean;
  };
  uaf_report_automation: boolean;
  default_due_diligence: DueDiligenceLevel;
  document_retention_months: number;
  basel_fatf_update_schedule: string;
}

export interface PasswordPolicy {
  min_length: number;
  require_symbols: boolean;
  require_numbers: boolean;
}

export interface SecuritySettings {
  enforce_2fa: boolean;
  session_timeout_minutes: number;
  max_failed_logins: number;
  password_policy: PasswordPolicy;
  production_auth_mode: boolean;
}

export interface DMCESettings {
  enable_automation: boolean;
  default_customs_company: string | null;
  browser: BrowserType;
  browser_mode: BrowserMode;
  login_timeout_seconds: number;
}

export interface IntegrationSettings {
  sap_endpoint: string | null;
  sap_api_key: string | null;
  risk365_endpoint: string | null;
  risk365_auth: string | null;
  webhooks: string[];
  slack_webhook: string | null;
}

export interface SystemSettings {
  general: GeneralSettings;
  menu_layout: MenuLayoutSettings;
  ai: AISettings;
  compliance: ComplianceSettings;
  security: SecuritySettings;
  dmce: DMCESettings;
  integrations: IntegrationSettings;
  last_updated: string;
  updated_by: string | null;
}

export const systemApi = {
  /**
   * Get system settings
   * @returns Promise with system settings
   */
  getSettings: async (): Promise<SystemSettings> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/system/settings`, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch system settings:', error);
      throw error;
    }
  },

  /**
   * Update system settings
   * @param settings Updated system settings
   * @returns Promise with updated system settings
   */
  updateSettings: async (settings: SystemSettings): Promise<SystemSettings> => {
    try {
      const response = await axios.put(`${API_BASE_URL}/system/settings`, settings, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to update system settings:', error);
      throw error;
    }
  }
};

export default systemApi;
