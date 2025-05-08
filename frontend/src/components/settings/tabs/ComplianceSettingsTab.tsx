import React from 'react';
import { useTranslation } from 'react-i18next';
import { SystemSettings, DueDiligenceLevel } from '../../../lib/api/systemApi';
import { Switch } from '../../../components/ui/switch';
import { Label } from '../../../components/ui/label';
import { Input } from '../../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';

interface ComplianceSettingsTabProps {
  settings: SystemSettings;
  updateSettings: (settings: Partial<SystemSettings>) => void;
}

const ComplianceSettingsTab = ({ settings, updateSettings }: ComplianceSettingsTabProps) => {
  const { t } = useTranslation();
  
  const handleSanctionsSourceToggle = (source: string, enabled: boolean) => {
    updateSettings({
      compliance: {
        ...settings.compliance,
        sanctions_sources: {
          ...settings.compliance.sanctions_sources,
          [source]: enabled
        }
      }
    });
  };
  
  const handleUAFReportAutomationToggle = (enabled: boolean) => {
    updateSettings({
      compliance: {
        ...settings.compliance,
        uaf_report_automation: enabled
      }
    });
  };
  
  const handleDueDiligenceLevelChange = (value: string) => {
    updateSettings({
      compliance: {
        ...settings.compliance,
        default_due_diligence: value as DueDiligenceLevel
      }
    });
  };
  
  const handleDocumentRetentionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (isNaN(value)) return;
    
    updateSettings({
      compliance: {
        ...settings.compliance,
        document_retention_months: value
      }
    });
  };
  
  const handleBaselFATFScheduleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      compliance: {
        ...settings.compliance,
        basel_fatf_update_schedule: e.target.value
      }
    });
  };
  
  const sanctionsSources = [
    { id: 'ofac', label: t('settings.sanctionsSources.ofac') },
    { id: 'un', label: t('settings.sanctionsSources.un') },
    { id: 'eu', label: t('settings.sanctionsSources.eu') },
    { id: 'open_sanctions', label: t('settings.sanctionsSources.openSanctions') }
  ];
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.compliance')}</CardTitle>
        <CardDescription>{t('settings.complianceDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.sanctionsSettings')}</h3>
          <div className="grid gap-4">
            {sanctionsSources.map((source) => (
              <div key={source.id} className="flex items-center justify-between">
                <Label htmlFor={`sanctions-${source.id}`}>{source.label}</Label>
                <Switch
                  id={`sanctions-${source.id}`}
                  checked={settings.compliance.sanctions_sources[source.id as keyof typeof settings.compliance.sanctions_sources]}
                  onCheckedChange={(checked) => handleSanctionsSourceToggle(source.id, checked)}
                />
              </div>
            ))}
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.uafReportSettings')}</h3>
          <div className="flex items-center justify-between">
            <Label htmlFor="uaf-automation">{t('settings.uafReportAutomation')}</Label>
            <Switch
              id="uaf-automation"
              checked={settings.compliance.uaf_report_automation}
              onCheckedChange={handleUAFReportAutomationToggle}
            />
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.dueDiligenceSettings')}</h3>
          <div className="space-y-2">
            <Label htmlFor="due-diligence-level">{t('settings.defaultDueDiligence')}</Label>
            <Select 
              value={settings.compliance.default_due_diligence} 
              onValueChange={handleDueDiligenceLevelChange}
            >
              <SelectTrigger id="due-diligence-level">
                <SelectValue placeholder={t('settings.selectDueDiligenceLevel')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={DueDiligenceLevel.SIMPLIFIED}>{t('settings.dueDiligenceLevels.simplified')}</SelectItem>
                <SelectItem value={DueDiligenceLevel.BASIC}>{t('settings.dueDiligenceLevels.basic')}</SelectItem>
                <SelectItem value={DueDiligenceLevel.ENHANCED}>{t('settings.dueDiligenceLevels.enhanced')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="document-retention">{t('settings.documentRetention')}</Label>
            <Input
              id="document-retention"
              type="number"
              value={settings.compliance.document_retention_months}
              onChange={handleDocumentRetentionChange}
              min={12}
              max={120}
              step={6}
            />
            <p className="text-sm text-gray-500">{t('settings.documentRetentionHelp')}</p>
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.updateSchedules')}</h3>
          <div className="space-y-2">
            <Label htmlFor="basel-fatf-schedule">{t('settings.baselFATFSchedule')}</Label>
            <Input
              id="basel-fatf-schedule"
              value={settings.compliance.basel_fatf_update_schedule}
              onChange={handleBaselFATFScheduleChange}
              placeholder="0 0 1 * *"
            />
            <p className="text-sm text-gray-500">{t('settings.cronFormatHelp')}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ComplianceSettingsTab;
