import React from 'react';
import { useTranslation } from 'react-i18next';
import { SystemSettings, LanguageMode, AIModel } from '../../../lib/api/systemApi';
import { Switch } from '../../../components/ui/switch';
import { Label } from '../../../components/ui/label';
import { Input } from '../../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';

interface AISettingsTabProps {
  settings: SystemSettings;
  updateSettings: (settings: Partial<SystemSettings>) => void;
}

const AISettingsTab = ({ settings, updateSettings }: AISettingsTabProps) => {
  const { t } = useTranslation();
  
  const handleLanguageModeChange = (value: string) => {
    updateSettings({
      ai: {
        ...settings.ai,
        language_mode: value as LanguageMode
      }
    });
  };
  
  const handleModelChange = (value: string) => {
    updateSettings({
      ai: {
        ...settings.ai,
        model: value as AIModel
      }
    });
  };
  
  const handleFallbackModeToggle = (enabled: boolean) => {
    updateSettings({
      ai: {
        ...settings.ai,
        fallback_mode: enabled
      }
    });
  };
  
  const handleDebugModeToggle = (enabled: boolean) => {
    updateSettings({
      ai: {
        ...settings.ai,
        debug_mode: enabled
      }
    });
  };
  
  const handleMaxTokensChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (isNaN(value)) return;
    
    updateSettings({
      ai: {
        ...settings.ai,
        max_tokens: value
      }
    });
  };
  
  const handleHealthCheckScheduleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      ai: {
        ...settings.ai,
        health_check_schedule: e.target.value
      }
    });
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.ai')}</CardTitle>
        <CardDescription>{t('settings.aiDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.aiLanguageSettings')}</h3>
          <div className="space-y-2">
            <Label htmlFor="language-mode">{t('settings.languageMode')}</Label>
            <Select 
              value={settings.ai.language_mode} 
              onValueChange={handleLanguageModeChange}
            >
              <SelectTrigger id="language-mode">
                <SelectValue placeholder={t('settings.selectLanguageMode')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={LanguageMode.AUTO_DETECT}>{t('settings.languageModes.autoDetect')}</SelectItem>
                <SelectItem value={LanguageMode.FORCE_SPANISH}>{t('settings.languageModes.forceSpanish')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.aiModelSettings')}</h3>
          <div className="space-y-2">
            <Label htmlFor="ai-model">{t('settings.aiModel')}</Label>
            <Select 
              value={settings.ai.model} 
              onValueChange={handleModelChange}
            >
              <SelectTrigger id="ai-model">
                <SelectValue placeholder={t('settings.selectAIModel')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={AIModel.MISTRAL_7B}>{t('settings.aiModels.mistral7b')}</SelectItem>
                <SelectItem value={AIModel.OPEN_HERMES}>{t('settings.aiModels.openHermes')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="max-tokens">{t('settings.maxTokens')}</Label>
            <Input
              id="max-tokens"
              type="number"
              value={settings.ai.max_tokens}
              onChange={handleMaxTokensChange}
              min={100}
              max={2000}
              step={100}
            />
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.aiAdvancedSettings')}</h3>
          <div className="flex items-center justify-between">
            <Label htmlFor="fallback-mode">{t('settings.fallbackMode')}</Label>
            <Switch
              id="fallback-mode"
              checked={settings.ai.fallback_mode}
              onCheckedChange={handleFallbackModeToggle}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <Label htmlFor="debug-mode">{t('settings.debugMode')}</Label>
            <Switch
              id="debug-mode"
              checked={settings.ai.debug_mode}
              onCheckedChange={handleDebugModeToggle}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="health-check-schedule">{t('settings.healthCheckSchedule')}</Label>
            <Input
              id="health-check-schedule"
              value={settings.ai.health_check_schedule}
              onChange={handleHealthCheckScheduleChange}
              placeholder="0 0 * * *"
            />
            <p className="text-sm text-gray-500">{t('settings.cronFormatHelp')}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AISettingsTab;
