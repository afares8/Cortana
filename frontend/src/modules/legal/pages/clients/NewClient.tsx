import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../../../../components/ui/card';
import { Button } from '../../../../components/ui/button';
import { Input } from '../../../../components/ui/input';
import { Label } from '../../../../components/ui/label';
import { Textarea } from '../../../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../../components/ui/select';
import { Alert } from '../../../../components/ui/alert';
import { AlertCircle, Loader2, Save, ArrowLeft } from 'lucide-react';
import { Toast, ToastProvider, ToastViewport, ToastTitle, ToastDescription } from '../../../../components/ui/toast';
import { createClient } from '../../api/legalApi';
import { ClientCreate } from '../../types';
import { useTranslation } from 'react-i18next';

const NewClient: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [industry, setIndustry] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [address, setAddress] = useState('');
  const [kycVerified, setKycVerified] = useState(false);
  const [notes, setNotes] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name) {
      setError(t('Please enter a client name'));
      return;
    }
    
    if (!contactEmail) {
      setError(t('Please enter a contact email'));
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const clientData: ClientCreate = {
        name,
        contact_email: contactEmail,
        contact_phone: contactPhone,
        address,
        industry,
        kyc_verified: kycVerified,
        notes
      };
      
      const response = await createClient(clientData);
      
      setSuccess(true);
      setTimeout(() => {
        navigate(`/legal/clients/${response.id}`);
      }, 1500);
    } catch (err) {
      console.error('Error creating client:', err);
      setError(t('Failed to create client. Please try again later.'));
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <ToastProvider>
      <div className="container mx-auto py-6">
        <div className="flex items-center mb-6">
          <Button 
            variant="outline" 
            onClick={() => navigate('/legal/clients')}
            className="mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('Back')}
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{t('New Client')}</h1>
            <p className="text-gray-500">{t('Create a new client record')}</p>
          </div>
        </div>
        
        {error && (
          <Alert className="mb-6">
            <AlertCircle className="h-4 w-4 mr-2" />
            {error}
          </Alert>
        )}
        
        <form onSubmit={handleSubmit}>
          <Card>
            <CardHeader>
              <CardTitle>{t('Client Information')}</CardTitle>
              <CardDescription>{t('Enter the client details below')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="name">{t('Name')}</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t('Enter client name')}
                  disabled={loading}
                />
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="industry">{t('Industry')}</Label>
                <Select value={industry} onValueChange={setIndustry} disabled={loading}>
                  <SelectTrigger id="industry">
                    <SelectValue placeholder={t('Select client industry')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="finance">{t('Finance')}</SelectItem>
                    <SelectItem value="healthcare">{t('Healthcare')}</SelectItem>
                    <SelectItem value="technology">{t('Technology')}</SelectItem>
                    <SelectItem value="retail">{t('Retail')}</SelectItem>
                    <SelectItem value="manufacturing">{t('Manufacturing')}</SelectItem>
                    <SelectItem value="government">{t('Government')}</SelectItem>
                    <SelectItem value="education">{t('Education')}</SelectItem>
                    <SelectItem value="other">{t('Other')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="kyc-verified">{t('KYC Verified')}</Label>
                <Select value={kycVerified ? "true" : "false"} onValueChange={(value) => setKycVerified(value === "true")} disabled={loading}>
                  <SelectTrigger id="kyc-verified">
                    <SelectValue placeholder={t('Select KYC status')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">{t('Verified')}</SelectItem>
                    <SelectItem value="false">{t('Not Verified')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="contact-email">{t('Contact Email')}</Label>
                  <Input
                    id="contact-email"
                    type="email"
                    value={contactEmail}
                    onChange={(e) => setContactEmail(e.target.value)}
                    placeholder={t('Enter contact email address')}
                    disabled={loading}
                  />
                </div>
                
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="contact-phone">{t('Contact Phone')}</Label>
                  <Input
                    id="contact-phone"
                    value={contactPhone}
                    onChange={(e) => setContactPhone(e.target.value)}
                    placeholder={t('Enter contact phone number')}
                    disabled={loading}
                  />
                </div>
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="address">{t('Address')}</Label>
                <Textarea
                  id="address"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder={t('Enter address')}
                  disabled={loading}
                />
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="notes">{t('Notes')}</Label>
                <Textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder={t('Enter additional notes')}
                  disabled={loading}
                />
              </div>
              
              <div className="flex justify-end gap-2 mt-6">
                <Button 
                  variant="outline" 
                  onClick={() => navigate('/legal/clients')}
                  disabled={loading}
                >
                  {t('Cancel')}
                </Button>
                <Button 
                  type="submit" 
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {t('Creating...')}
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      {t('Create Client')}
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>
        
        {success && (
          <Toast>
            <ToastTitle>{t('Success')}</ToastTitle>
            <ToastDescription>
              {t('Client created successfully')}
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default NewClient;
