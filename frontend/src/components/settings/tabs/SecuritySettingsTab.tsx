import React from 'react';
import { useTranslation } from 'react-i18next';
import { SystemSettings } from '../../../lib/api/systemApi';
import { Switch } from '../../../components/ui/switch';
import { Label } from '../../../components/ui/label';
import { Input } from '../../../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';

interface SecuritySettingsTabProps {
  settings: SystemSettings;
  updateSettings: (settings: Partial<SystemSettings>) => void;
}

const SecuritySettingsTab = ({ settings, updateSettings }: SecuritySettingsTabProps) => {
  const { t } = useTranslation();
  
  const handleEnforce2FAToggle = (enabled: boolean) => {
    updateSettings({
      security: {
        ...settings.security,
        enforce_2fa: enabled
      }
    });
  };
  
  const handleSessionTimeoutChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (isNaN(value)) return;
    
    updateSettings({
      security: {
        ...settings.security,
        session_timeout_minutes: value
      }
    });
  };
  
  const handleMaxFailedLoginsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (isNaN(value)) return;
    
    updateSettings({
      security: {
        ...settings.security,
        max_failed_logins: value
      }
    });
  };
  
  const handlePasswordMinLengthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (isNaN(value)) return;
    
    updateSettings({
      security: {
        ...settings.security,
        password_policy: {
          ...settings.security.password_policy,
          min_length: value
        }
      }
    });
  };
  
  const handleRequireSymbolsToggle = (enabled: boolean) => {
    updateSettings({
      security: {
        ...settings.security,
        password_policy: {
          ...settings.security.password_policy,
          require_symbols: enabled
        }
      }
    });
  };
  
  const handleRequireNumbersToggle = (enabled: boolean) => {
    updateSettings({
      security: {
        ...settings.security,
        password_policy: {
          ...settings.security.password_policy,
          require_numbers: enabled
        }
      }
    });
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.security')}</CardTitle>
        <CardDescription>{t('settings.securityDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.authenticationSettings')}</h3>
          <div className="flex items-center justify-between">
            <Label htmlFor="enforce-2fa">{t('settings.enforce2FA')}</Label>
            <Switch
              id="enforce-2fa"
              checked={settings.security.enforce_2fa}
              onCheckedChange={handleEnforce2FAToggle}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="session-timeout">{t('settings.sessionTimeout')}</Label>
            <Input
              id="session-timeout"
              type="number"
              value={settings.security.session_timeout_minutes}
              onChange={handleSessionTimeoutChange}
              min={5}
              max={240}
              step={5}
            />
            <p className="text-sm text-gray-500">{t('settings.sessionTimeoutHelp')}</p>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="max-failed-logins">{t('settings.maxFailedLogins')}</Label>
            <Input
              id="max-failed-logins"
              type="number"
              value={settings.security.max_failed_logins}
              onChange={handleMaxFailedLoginsChange}
              min={3}
              max={10}
              step={1}
            />
            <p className="text-sm text-gray-500">{t('settings.maxFailedLoginsHelp')}</p>
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.passwordPolicy')}</h3>
          <div className="space-y-2">
            <Label htmlFor="password-min-length">{t('settings.passwordMinLength')}</Label>
            <Input
              id="password-min-length"
              type="number"
              value={settings.security.password_policy.min_length}
              onChange={handlePasswordMinLengthChange}
              min={6}
              max={16}
              step={1}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <Label htmlFor="require-symbols">{t('settings.requireSymbols')}</Label>
            <Switch
              id="require-symbols"
              checked={settings.security.password_policy.require_symbols}
              onCheckedChange={handleRequireSymbolsToggle}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <Label htmlFor="require-numbers">{t('settings.requireNumbers')}</Label>
            <Switch
              id="require-numbers"
              checked={settings.security.password_policy.require_numbers}
              onCheckedChange={handleRequireNumbersToggle}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SecuritySettingsTab;
