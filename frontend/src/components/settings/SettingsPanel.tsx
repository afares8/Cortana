import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Loader2 } from 'lucide-react';
import { systemApi, SystemSettings } from '../../lib/api/systemApi';

import GeneralSettingsTab from './tabs/GeneralSettingsTab';
import MenuLayoutTab from './tabs/MenuLayoutTab';
import AISettingsTab from './tabs/AISettingsTab';
import ComplianceSettingsTab from './tabs/ComplianceSettingsTab';
import SecuritySettingsTab from './tabs/SecuritySettingsTab';
import DMCESettingsTab from './tabs/DMCESettingsTab';
import IntegrationsTab from './tabs/IntegrationsTab';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsPanel = ({ isOpen, onClose }: SettingsPanelProps) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [activeTab, setActiveTab] = useState('general');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const loadSettings = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await systemApi.getSettings();
      setSettings(data);
    } catch (err: Error | unknown) {
      console.error('Failed to load settings:', err);
      setError(t('settings.errors.loadFailed'));
      
      if (typeof err === 'object' && err !== null && 'response' in err && 
          err.response && typeof err.response === 'object' && 'status' in err.response && 
          err.response.status === 403) {
        onClose();
        navigate('/dashboard');
      }
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen, t, navigate]);
  
  const handleSave = async () => {
    if (!settings) return;
    
    setSaving(true);
    setError(null);
    
    try {
      await systemApi.updateSettings(settings);
      onClose();
    } catch (err: Error | unknown) {
      console.error('Failed to save settings:', err);
      setError(t('settings.errors.saveFailed'));
    } finally {
      setSaving(false);
    }
  };
  
  const updateSettings = (partialSettings: Partial<SystemSettings>) => {
    if (!settings) return;
    
    setSettings({
      ...settings,
      ...partialSettings,
    });
  };
  
  if (loading) {
    return (
      <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
        <DialogContent className="max-w-4xl">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
            <span className="ml-2 text-gray-500">{t('common.loading')}</span>
          </div>
        </DialogContent>
      </Dialog>
    );
  }
  
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t('settings.title')}</DialogTitle>
          <DialogDescription>{t('settings.description')}</DialogDescription>
        </DialogHeader>
        
        {error && (
          <Alert variant="destructive" className="mt-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {settings && (
          <>
            <Tabs defaultValue="general" value={activeTab} onValueChange={setActiveTab} className="mt-6">
              <TabsList className="grid grid-cols-7">
                <TabsTrigger value="general">{t('settings.tabs.general')}</TabsTrigger>
                <TabsTrigger value="menu">{t('settings.tabs.menuLayout')}</TabsTrigger>
                <TabsTrigger value="ai">{t('settings.tabs.ai')}</TabsTrigger>
                <TabsTrigger value="compliance">{t('settings.tabs.compliance')}</TabsTrigger>
                <TabsTrigger value="security">{t('settings.tabs.security')}</TabsTrigger>
                <TabsTrigger value="dmce">{t('settings.tabs.dmce')}</TabsTrigger>
                <TabsTrigger value="integrations">{t('settings.tabs.integrations')}</TabsTrigger>
              </TabsList>
              
              <TabsContent value="general">
                <GeneralSettingsTab 
                  settings={settings} 
                  updateSettings={updateSettings} 
                />
              </TabsContent>
              
              <TabsContent value="menu">
                <MenuLayoutTab 
                  settings={settings} 
                  updateSettings={updateSettings} 
                />
              </TabsContent>
              
              <TabsContent value="ai">
                <AISettingsTab 
                  settings={settings} 
                  updateSettings={updateSettings} 
                />
              </TabsContent>
              
              <TabsContent value="compliance">
                <ComplianceSettingsTab 
                  settings={settings} 
                  updateSettings={updateSettings} 
                />
              </TabsContent>
              
              <TabsContent value="security">
                <SecuritySettingsTab 
                  settings={settings} 
                  updateSettings={updateSettings} 
                />
              </TabsContent>
              
              <TabsContent value="dmce">
                <DMCESettingsTab 
                  settings={settings} 
                  updateSettings={updateSettings} 
                />
              </TabsContent>
              
              <TabsContent value="integrations">
                <IntegrationsTab 
                  settings={settings} 
                  updateSettings={updateSettings} 
                />
              </TabsContent>
            </Tabs>
            
            <div className="flex justify-end space-x-2 mt-6">
              <Button variant="outline" onClick={onClose}>
                {t('common.cancel')}
              </Button>
              <Button 
                onClick={handleSave} 
                disabled={saving}
              >
                {saving ? t('common.saving') : t('common.saveChanges')}
              </Button>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default SettingsPanel;
