import { useTranslation } from 'react-i18next';
import { SystemSettings } from '../../../lib/api/systemApi';
import { Switch } from '../../../components/ui/switch';
import { Label } from '../../../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';

interface MenuLayoutTabProps {
  settings: SystemSettings;
  updateSettings: (settings: Partial<SystemSettings>) => void;
}

const MenuLayoutTab = ({ settings, updateSettings }: MenuLayoutTabProps) => {
  const { t } = useTranslation();
  
  const handleModuleToggle = (module: string, enabled: boolean) => {
    if (!settings.menu_layout.modules[module]) return;
    
    const updatedModules = {
      ...settings.menu_layout.modules,
      [module]: {
        ...settings.menu_layout.modules[module],
        enabled
      }
    };
    
    updateSettings({
      menu_layout: {
        ...settings.menu_layout,
        modules: updatedModules
      }
    });
  };
  
  const handleDarkModeToggle = (enabled: boolean) => {
    updateSettings({
      menu_layout: {
        ...settings.menu_layout,
        dark_mode: enabled
      }
    });
  };
  
  const modules = [
    { id: 'legal', label: t('settings.modules.legal') },
    { id: 'compliance', label: t('settings.modules.compliance') },
    { id: 'accounting', label: t('settings.modules.accounting') },
    { id: 'traffic', label: t('settings.modules.traffic') },
    { id: 'ai', label: t('settings.modules.ai') },
    { id: 'users', label: t('settings.modules.users') }
  ];
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.menuLayout')}</CardTitle>
        <CardDescription>{t('settings.menuLayoutDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.enableModules')}</h3>
          <div className="grid gap-4">
            {modules.map((module) => (
              <div key={module.id} className="flex items-center justify-between">
                <Label htmlFor={`module-${module.id}`}>{module.label}</Label>
                <Switch
                  id={`module-${module.id}`}
                  checked={settings.menu_layout.modules[module.id]?.enabled ?? true}
                  onCheckedChange={(checked) => handleModuleToggle(module.id, checked)}
                />
              </div>
            ))}
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.appearance')}</h3>
          <div className="flex items-center justify-between">
            <Label htmlFor="dark-mode">{t('settings.darkMode')}</Label>
            <Switch
              id="dark-mode"
              checked={settings.menu_layout.dark_mode}
              onCheckedChange={handleDarkModeToggle}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default MenuLayoutTab;
