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
import { AlertCircle, Loader2, Save, ArrowLeft, ShieldAlert } from 'lucide-react';
import { Toast, ToastProvider, ToastViewport, ToastTitle, ToastDescription } from '../../../../components/ui/toast';
import { createClient } from '../../api/legalApi';
import { ClientCreate } from '../../types';
import { useTranslation } from 'react-i18next';
import { API_BASE_URL } from '../../../../constants';

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
  const [clientType, setClientType] = useState('individual');
  const [country, setCountry] = useState('PA');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [riskLevel, setRiskLevel] = useState<string | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<string | null>(null);
  
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
    
    if (loading) {
      console.log('Form submission already in progress, preventing duplicate submission');
      return; // Prevent multiple submissions
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const clientData: ClientCreate = {
        name,
        contact_email: contactEmail,
        contact_phone: contactPhone,
        address,
        industry,
        kyc_verified: kycVerified,
        notes,
        client_type: clientType,
        country: country
      };
      
      console.log('Submitting client data:', clientData);
      
      const response = await createClient(clientData);
      console.log('Client created successfully:', response);
      
      try {
        const riskEvalResponse = await fetch(`${API_BASE_URL}/compliance/risk-evaluation`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            client_id: response.id,
            client_data: {
              client_type: clientType,
              country: country,
              industry: industry || 'other',
              channel: 'presencial'
            }
          })
        });
        
        if (riskEvalResponse.ok) {
          const riskData = await riskEvalResponse.json();
          setRiskLevel(riskData.risk_level);
          console.log('Risk evaluation completed:', riskData);
        }
        
        const verifyResponse = await fetch(`${API_BASE_URL}/legal/verify-client`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            client_id: response.id,
            name: name,
            country: country
          })
        });
        
        if (verifyResponse.ok) {
          const verificationData = await verifyResponse.json();
          setVerificationStatus(verificationData.status || 'completed');
          console.log('Client verification completed:', verificationData);
        }
      } catch (complianceErr) {
        console.error('Error during compliance checks:', complianceErr);
      }
      
      setName('');
      setIndustry('');
      setContactEmail('');
      setContactPhone('');
      setAddress('');
      setKycVerified(false);
      setNotes('');
      
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
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  <Label htmlFor="client-type">{t('Client Type')}</Label>
                  <Select value={clientType} onValueChange={setClientType} disabled={loading}>
                    <SelectTrigger id="client-type">
                      <SelectValue placeholder={t('Select client type')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="individual">{t('Individual')}</SelectItem>
                      <SelectItem value="empresa">{t('Company')}</SelectItem>
                      <SelectItem value="gobierno">{t('Government')}</SelectItem>
                      <SelectItem value="ong">{t('NGO')}</SelectItem>
                      <SelectItem value="pep">{t('PEP')}</SelectItem>
                      <SelectItem value="fideicomiso">{t('Trust')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="country">{t('Country')}</Label>
                <Select value={country} onValueChange={setCountry} disabled={loading}>
                  <SelectTrigger id="country">
                    <SelectValue placeholder={t('Select country')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="PA">{t('Panama')}</SelectItem>
                    <SelectItem value="US">{t('United States')}</SelectItem>
                    <SelectItem value="CO">{t('Colombia')}</SelectItem>
                    <SelectItem value="VE">{t('Venezuela')}</SelectItem>
                    <SelectItem value="MX">{t('Mexico')}</SelectItem>
                    <SelectItem value="BR">{t('Brazil')}</SelectItem>
                    <SelectItem value="AR">{t('Argentina')}</SelectItem>
                    <SelectItem value="CL">{t('Chile')}</SelectItem>
                    <SelectItem value="PE">{t('Peru')}</SelectItem>
                    <SelectItem value="EC">{t('Ecuador')}</SelectItem>
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
            <ToastDescription className="space-y-2">
              <div>{t('Client created successfully')}</div>
              {riskLevel && (
                <div className={`p-1 rounded text-sm ${
                  riskLevel === 'HIGH' ? 'bg-red-100 text-red-800' :
                  riskLevel === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  <ShieldAlert className="h-4 w-4 inline mr-1" />
                  {t('Risk Level')}: {riskLevel}
                </div>
              )}
              {verificationStatus && (
                <div className="bg-blue-100 text-blue-800 p-1 rounded text-sm">
                  {t('Verification Status')}: {verificationStatus}
                </div>
              )}
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default NewClient;
