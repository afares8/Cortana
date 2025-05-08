import React from 'react';
import { useTranslation } from 'react-i18next';
import { SystemSettings } from '../../../lib/api/systemApi';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { PlusCircle, Trash2 } from 'lucide-react';

interface IntegrationsTabProps {
  settings: SystemSettings;
  updateSettings: (settings: Partial<SystemSettings>) => void;
}

const IntegrationsTab = ({ settings, updateSettings }: IntegrationsTabProps) => {
  const { t } = useTranslation();
  
  const handleSAPEndpointChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      integrations: {
        ...settings.integrations,
        sap_endpoint: e.target.value || null
      }
    });
  };
  
  const handleSAPAPIKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      integrations: {
        ...settings.integrations,
        sap_api_key: e.target.value || null
      }
    });
  };
  
  const handleRisk365EndpointChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      integrations: {
        ...settings.integrations,
        risk365_endpoint: e.target.value || null
      }
    });
  };
  
  const handleRisk365AuthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      integrations: {
        ...settings.integrations,
        risk365_auth: e.target.value || null
      }
    });
  };
  
  const handleSlackWebhookChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateSettings({
      integrations: {
        ...settings.integrations,
        slack_webhook: e.target.value || null
      }
    });
  };
  
  const handleAddWebhook = () => {
    updateSettings({
      integrations: {
        ...settings.integrations,
        webhooks: [...settings.integrations.webhooks, '']
      }
    });
  };
  
  const handleWebhookChange = (index: number, value: string) => {
    const updatedWebhooks = [...settings.integrations.webhooks];
    updatedWebhooks[index] = value;
    
    updateSettings({
      integrations: {
        ...settings.integrations,
        webhooks: updatedWebhooks
      }
    });
  };
  
  const handleRemoveWebhook = (index: number) => {
    const updatedWebhooks = [...settings.integrations.webhooks];
    updatedWebhooks.splice(index, 1);
    
    updateSettings({
      integrations: {
        ...settings.integrations,
        webhooks: updatedWebhooks
      }
    });
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.integrations')}</CardTitle>
        <CardDescription>{t('settings.integrationsDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.sapIntegration')}</h3>
          <div className="space-y-2">
            <Label htmlFor="sap-endpoint">{t('settings.sapEndpoint')}</Label>
            <Input
              id="sap-endpoint"
              value={settings.integrations.sap_endpoint || ''}
              onChange={handleSAPEndpointChange}
              placeholder="https://sap-api.example.com"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="sap-api-key">{t('settings.sapAPIKey')}</Label>
            <Input
              id="sap-api-key"
              type="password"
              value={settings.integrations.sap_api_key || ''}
              onChange={handleSAPAPIKeyChange}
              placeholder={t('settings.enterAPIKey')}
            />
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.risk365Integration')}</h3>
          <div className="space-y-2">
            <Label htmlFor="risk365-endpoint">{t('settings.risk365Endpoint')}</Label>
            <Input
              id="risk365-endpoint"
              value={settings.integrations.risk365_endpoint || ''}
              onChange={handleRisk365EndpointChange}
              placeholder="https://risk365.example.com"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="risk365-auth">{t('settings.risk365Auth')}</Label>
            <Input
              id="risk365-auth"
              type="password"
              value={settings.integrations.risk365_auth || ''}
              onChange={handleRisk365AuthChange}
              placeholder={t('settings.enterAuthToken')}
            />
          </div>
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">{t('settings.notificationIntegrations')}</h3>
          <div className="space-y-2">
            <Label htmlFor="slack-webhook">{t('settings.slackWebhook')}</Label>
            <Input
              id="slack-webhook"
              value={settings.integrations.slack_webhook || ''}
              onChange={handleSlackWebhookChange}
              placeholder="https://hooks.slack.com/services/..."
            />
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">{t('settings.webhooks')}</h3>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleAddWebhook}
              className="flex items-center"
            >
              <PlusCircle className="h-4 w-4 mr-1" />
              {t('settings.addWebhook')}
            </Button>
          </div>
          
          {settings.integrations.webhooks.map((webhook, index) => (
            <div key={index} className="flex items-center space-x-2">
              <Input
                value={webhook}
                onChange={(e) => handleWebhookChange(index, e.target.value)}
                placeholder="https://example.com/webhook"
              />
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => handleRemoveWebhook(index)}
                className="flex-shrink-0"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default IntegrationsTab;
