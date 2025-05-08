import React from 'react';
import { useTranslation } from 'react-i18next';
import { SystemSettings } from '../../../lib/api/systemApi';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';

interface GeneralSettingsTabProps {
  settings: SystemSettings;
  updateSettings: (settings: Partial<SystemSettings>) => void;
}

const GeneralSettingsTab = ({ settings, updateSettings }: GeneralSettingsTabProps) => {
  const { t } = useTranslation();
  
  const handleSystemNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      general: {
        ...settings.general,
        system_name: e.target.value
      }
    });
  };
  
  const handleLanguageChange = (value: string) => {
    updateSettings({
      general: {
        ...settings.general,
        default_language: value
      }
    });
  };
  
  const handleTimezoneChange = (value: string) => {
    updateSettings({
      general: {
        ...settings.general,
        timezone: value
      }
    });
  };
  
  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const logoUrl = URL.createObjectURL(file);
    
    updateSettings({
      general: {
        ...settings.general,
        logo_url: logoUrl
      }
    });
    
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.general')}</CardTitle>
        <CardDescription>{t('settings.generalDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="system-name">{t('settings.systemName')}</Label>
          <Input
            id="system-name"
            value={settings.general.system_name}
            onChange={handleSystemNameChange}
            placeholder={t('settings.systemNamePlaceholder')}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="logo-upload">{t('settings.logo')}</Label>
          <div className="flex items-center space-x-4">
            {settings.general.logo_url && (
              <img 
                src={settings.general.logo_url} 
                alt="Logo" 
                className="h-12 w-auto object-contain"
              />
            )}
            <Input
              id="logo-upload"
              type="file"
              accept="image/*"
              onChange={handleLogoUpload}
            />
          </div>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="default-language">{t('settings.defaultLanguage')}</Label>
          <Select 
            value={settings.general.default_language} 
            onValueChange={handleLanguageChange}
          >
            <SelectTrigger id="default-language">
              <SelectValue placeholder={t('settings.selectLanguage')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="en">{t('settings.languages.english')}</SelectItem>
              <SelectItem value="es">{t('settings.languages.spanish')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="timezone">{t('settings.timezone')}</Label>
          <Select 
            value={settings.general.timezone} 
            onValueChange={handleTimezoneChange}
          >
            <SelectTrigger id="timezone">
              <SelectValue placeholder={t('settings.selectTimezone')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="America/Panama">{t('settings.timezones.panama')}</SelectItem>
              <SelectItem value="America/Bogota">{t('settings.timezones.bogota')}</SelectItem>
              <SelectItem value="America/Mexico_City">{t('settings.timezones.mexicoCity')}</SelectItem>
              <SelectItem value="America/New_York">{t('settings.timezones.newYork')}</SelectItem>
              <SelectItem value="Europe/Madrid">{t('settings.timezones.madrid')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  );
};

export default GeneralSettingsTab;
