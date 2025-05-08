import React from 'react';
import { useTranslation } from 'react-i18next';
import { SystemSettings, BrowserType, BrowserMode } from '../../../lib/api/systemApi';
import { Switch } from '../../../components/ui/switch';
import { Label } from '../../../components/ui/label';
import { Input } from '../../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';

interface DMCESettingsTabProps {
  settings: SystemSettings;
  updateSettings: (settings: Partial<SystemSettings>) => void;
}

const DMCESettingsTab = ({ settings, updateSettings }: DMCESettingsTabProps) => {
  const { t } = useTranslation();
  
  const handleEnableAutomationToggle = (enabled: boolean) => {
    updateSettings({
      dmce: {
        ...settings.dmce,
        enable_automation: enabled
      }
    });
  };
  
  const handleBrowserChange = (value: string) => {
    updateSettings({
      dmce: {
        ...settings.dmce,
        browser: value as BrowserType
      }
    });
  };
  
  const handleBrowserModeChange = (value: string) => {
    updateSettings({
      dmce: {
        ...settings.dmce,
        browser_mode: value as BrowserMode
      }
    });
  };
  
  const handleLoginTimeoutChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (isNaN(value)) return;
    
    updateSettings({
      dmce: {
        ...settings.dmce,
        login_timeout_seconds: value
      }
    });
  };
  
  const handleDefaultCustomsCompanyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      dmce: {
        ...settings.dmce,
        default_customs_company: e.target.value || null
      }
    });
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.dmce')}</CardTitle>
        <CardDescription>{t('settings.dmceDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.dmceGeneralSettings')}</h3>
          <div className="flex items-center justify-between">
            <Label htmlFor="enable-automation">{t('settings.enableAutomation')}</Label>
            <Switch
              id="enable-automation"
              checked={settings.dmce.enable_automation}
              onCheckedChange={handleEnableAutomationToggle}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="default-customs-company">{t('settings.defaultCustomsCompany')}</Label>
            <Input
              id="default-customs-company"
              value={settings.dmce.default_customs_company || ''}
              onChange={handleDefaultCustomsCompanyChange}
              placeholder={t('settings.defaultCustomsCompanyPlaceholder')}
            />
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.browserSettings')}</h3>
          <div className="space-y-2">
            <Label htmlFor="browser-type">{t('settings.browserType')}</Label>
            <Select 
              value={settings.dmce.browser} 
              onValueChange={handleBrowserChange}
            >
              <SelectTrigger id="browser-type">
                <SelectValue placeholder={t('settings.selectBrowserType')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={BrowserType.FIREFOX}>{t('settings.browserTypes.firefox')}</SelectItem>
                <SelectItem value={BrowserType.CHROMIUM}>{t('settings.browserTypes.chromium')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="browser-mode">{t('settings.browserMode')}</Label>
            <Select 
              value={settings.dmce.browser_mode} 
              onValueChange={handleBrowserModeChange}
            >
              <SelectTrigger id="browser-mode">
                <SelectValue placeholder={t('settings.selectBrowserMode')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={BrowserMode.HEADLESS}>{t('settings.browserModes.headless')}</SelectItem>
                <SelectItem value={BrowserMode.MANUAL_FALLBACK}>{t('settings.browserModes.manualFallback')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="login-timeout">{t('settings.loginTimeout')}</Label>
            <Input
              id="login-timeout"
              type="number"
              value={settings.dmce.login_timeout_seconds}
              onChange={handleLoginTimeoutChange}
              min={10}
              max={120}
              step={5}
            />
            <p className="text-sm text-gray-500">{t('settings.loginTimeoutHelp')}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default DMCESettingsTab;
