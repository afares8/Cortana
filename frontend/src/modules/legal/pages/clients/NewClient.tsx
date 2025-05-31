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
import { ClientCreate, Director, UBO } from '../../types';
import { useTranslation } from 'react-i18next';
import { API_BASE_URL } from '../../../../constants';
import OCRDocumentUpload from '../../../../components/OCRDocumentUpload';

const NewClient: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [industry, setIndustry] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [passport, setPassport] = useState('');
  const [address, setAddress] = useState('');
  const [kycVerified, setKycVerified] = useState(false);
  const [notes, setNotes] = useState('');
  const [clientType, setClientType] = useState('individual');
  const [country, setCountry] = useState('PA');
  
  const [dob, setDob] = useState('');
  const [nationality, setNationality] = useState('');
  
  const [registrationNumber, setRegistrationNumber] = useState('');
  const [incorporationDate, setIncorporationDate] = useState('');
  const [incorporationCountry, setIncorporationCountry] = useState('');
  const [directors, setDirectors] = useState<Director[]>([]);
  const [ubos, setUbos] = useState<UBO[]>([]);
  
  const [documents, setDocuments] = useState<File[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [riskLevel, setRiskLevel] = useState<string | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<string | null>(null);
  
  const handleOCRDataExtracted = (data: any) => {
    if (data.name) {
      setName(data.name);
    }
    if (data.dob) {
      setDob(data.dob);
    }
    if (data.id_number) {
      setPassport(data.id_number);
    }
  };
  
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

   if (clientType === 'individual') {
     if (!dob) {
       setError(t('Date of birth is required for individual clients'));
       return;
     }
     if (!nationality) {
       setError(t('Nationality is required for individual clients'));
       return;
     }
   } else if (clientType === 'legal') {
     if (!registrationNumber) {
       setError(t('Registration number is required for legal entities'));
       return;
     }
     if (!incorporationDate) {
       setError(t('Incorporation date is required for legal entities'));
       return;
     }
     if (!incorporationCountry) {
       setError(t('Incorporation country is required for legal entities'));
       return;
     }
   }

   if (loading) {
    console.log('Form submission already in progress, preventing duplicate submission');
    return;
   }

   setLoading(true);
   setError(null);

   try {
    const clientData: ClientCreate = {
      name,
      contact_email: contactEmail,
      contact_phone: contactPhone,
      address: address || '',
      industry: industry || 'other',
      kyc_verified: kycVerified,
      notes: notes || '',
      client_type: clientType,
      country: country,
      ...(clientType === 'individual' && {
        dob: dob || undefined,
        nationality: nationality || undefined
      }),
      ...(clientType === 'legal' && {
        registration_number: registrationNumber || undefined,
        incorporation_date: incorporationDate || undefined,
        incorporation_country: incorporationCountry || undefined,
        directors: directors,
        ubos: ubos
      })
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
          full_name: name,
          passport: passport || contactPhone || "N/A",  // Use passport, fallback to phone if empty
          country: country,
          type: clientType === 'individual' ? 'natural' : 'legal'
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
    setPassport('');
    setAddress('');
    setKycVerified(false);
    setNotes('');
    setDob('');
    setNationality('');
    setRegistrationNumber('');
    setIncorporationDate('');
    setIncorporationCountry('');
    setDirectors([]);
    setUbos([]);
    setDocuments([]);

    setSuccess(true);

    setTimeout(() => {
      navigate(`/legal/clients/${response.id}`);
    }, 1500);
  } catch (err: any) {
    console.error('Error creating client:', err);
    if (err?.response?.data?.detail) {
      setError(err.response.data.detail.toString());
    } else {
      setError(t('Failed to create client. Please try again later.'));
    }
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
              <CardTitle>{t('legal.clientInfo')}</CardTitle>
              <CardDescription>{t('legal.enterClientDetails')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* OCR Document Upload */}
              <OCRDocumentUpload 
                onDataExtracted={handleOCRDataExtracted}
                disabled={loading}
              />
              
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
                      <SelectItem value="legal">{t('Legal Entity')}</SelectItem>
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
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="passport">{t('Passport/ID Number')}</Label>
                  <Input
                    id="passport"
                    value={passport}
                    onChange={(e) => setPassport(e.target.value)}
                    placeholder={t('Enter passport or ID number')}
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
              
              {/* Individual-specific fields */}
              {clientType === 'individual' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="dob">{t('Date of Birth')}</Label>
                    <Input
                      id="dob"
                      type="date"
                      value={dob}
                      onChange={(e) => setDob(e.target.value)}
                      disabled={loading}
                    />
                  </div>
                  
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="nationality">{t('Nationality')}</Label>
                    <Select value={nationality} onValueChange={setNationality} disabled={loading}>
                      <SelectTrigger id="nationality">
                        <SelectValue placeholder={t('Select nationality')} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="PA">{t('Panamanian')}</SelectItem>
                        <SelectItem value="US">{t('American')}</SelectItem>
                        <SelectItem value="CO">{t('Colombian')}</SelectItem>
                        <SelectItem value="VE">{t('Venezuelan')}</SelectItem>
                        <SelectItem value="MX">{t('Mexican')}</SelectItem>
                        <SelectItem value="BR">{t('Brazilian')}</SelectItem>
                        <SelectItem value="AR">{t('Argentinian')}</SelectItem>
                        <SelectItem value="CL">{t('Chilean')}</SelectItem>
                        <SelectItem value="PE">{t('Peruvian')}</SelectItem>
                        <SelectItem value="EC">{t('Ecuadorian')}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              {/* Legal entity-specific fields */}
              {clientType === 'legal' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="grid w-full items-center gap-1.5">
                      <Label htmlFor="registration-number">{t('Registration Number')}</Label>
                      <Input
                        id="registration-number"
                        value={registrationNumber}
                        onChange={(e) => setRegistrationNumber(e.target.value)}
                        placeholder={t('RUC or ZLC License')}
                        disabled={loading}
                      />
                    </div>
                    
                    <div className="grid w-full items-center gap-1.5">
                      <Label htmlFor="incorporation-date">{t('Incorporation Date')}</Label>
                      <Input
                        id="incorporation-date"
                        type="date"
                        value={incorporationDate}
                        onChange={(e) => setIncorporationDate(e.target.value)}
                        disabled={loading}
                      />
                    </div>
                    
                    <div className="grid w-full items-center gap-1.5">
                      <Label htmlFor="incorporation-country">{t('Incorporation Country')}</Label>
                      <Select value={incorporationCountry} onValueChange={setIncorporationCountry} disabled={loading}>
                        <SelectTrigger id="incorporation-country">
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
                  </div>

                  {/* Directors Section */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>{t('Directors')}</Label>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setDirectors([...directors, { name: '', dob: '', country: '' }])}
                        disabled={loading}
                      >
                        {t('Add Director')}
                      </Button>
                    </div>
                    {directors.map((director, index) => (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-2 p-3 border rounded">
                        <Input
                          placeholder={t('Director Name')}
                          value={director.name}
                          onChange={(e) => {
                            const newDirectors = [...directors];
                            newDirectors[index].name = e.target.value;
                            setDirectors(newDirectors);
                          }}
                          disabled={loading}
                        />
                        <Input
                          type="date"
                          placeholder={t('Date of Birth')}
                          value={director.dob}
                          onChange={(e) => {
                            const newDirectors = [...directors];
                            newDirectors[index].dob = e.target.value;
                            setDirectors(newDirectors);
                          }}
                          disabled={loading}
                        />
                        <Select
                          value={director.country}
                          onValueChange={(value) => {
                            const newDirectors = [...directors];
                            newDirectors[index].country = value;
                            setDirectors(newDirectors);
                          }}
                          disabled={loading}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder={t('Country')} />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="PA">{t('Panama')}</SelectItem>
                            <SelectItem value="US">{t('United States')}</SelectItem>
                            <SelectItem value="CO">{t('Colombia')}</SelectItem>
                            <SelectItem value="VE">{t('Venezuela')}</SelectItem>
                          </SelectContent>
                        </Select>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => setDirectors(directors.filter((_, i) => i !== index))}
                          disabled={loading}
                        >
                          {t('Remove')}
                        </Button>
                      </div>
                    ))}
                  </div>

                  {/* UBOs Section */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>{t('Ultimate Beneficial Owners (UBOs)')}</Label>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setUbos([...ubos, { name: '', dob: '', country: '', percentage_ownership: 0 }])}
                        disabled={loading}
                      >
                        {t('Add UBO')}
                      </Button>
                    </div>
                    {ubos.map((ubo, index) => (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-5 gap-2 p-3 border rounded">
                        <Input
                          placeholder={t('UBO Name')}
                          value={ubo.name}
                          onChange={(e) => {
                            const newUbos = [...ubos];
                            newUbos[index].name = e.target.value;
                            setUbos(newUbos);
                          }}
                          disabled={loading}
                        />
                        <Input
                          type="date"
                          placeholder={t('Date of Birth')}
                          value={ubo.dob}
                          onChange={(e) => {
                            const newUbos = [...ubos];
                            newUbos[index].dob = e.target.value;
                            setUbos(newUbos);
                          }}
                          disabled={loading}
                        />
                        <Select
                          value={ubo.country}
                          onValueChange={(value) => {
                            const newUbos = [...ubos];
                            newUbos[index].country = value;
                            setUbos(newUbos);
                          }}
                          disabled={loading}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder={t('Country')} />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="PA">{t('Panama')}</SelectItem>
                            <SelectItem value="US">{t('United States')}</SelectItem>
                            <SelectItem value="CO">{t('Colombia')}</SelectItem>
                            <SelectItem value="VE">{t('Venezuela')}</SelectItem>
                          </SelectContent>
                        </Select>
                        <Input
                          type="number"
                          placeholder={t('Ownership %')}
                          value={ubo.percentage_ownership}
                          onChange={(e) => {
                            const newUbos = [...ubos];
                            newUbos[index].percentage_ownership = parseFloat(e.target.value) || 0;
                            setUbos(newUbos);
                          }}
                          disabled={loading}
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => setUbos(ubos.filter((_, i) => i !== index))}
                          disabled={loading}
                        >
                          {t('Remove')}
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Document Upload Section */}
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="documents">{t('Required Documents')}</Label>
                <Input
                  id="documents"
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => {
                    if (e.target.files) {
                      setDocuments(Array.from(e.target.files));
                    }
                  }}
                  disabled={loading}
                />
                <p className="text-sm text-gray-500">
                  {t('Upload required documents (PDF, JPG, PNG). For individuals: ID/Passport. For legal entities: Incorporation documents, director IDs.')}
                </p>
                {documents.length > 0 && (
                  <div className="mt-2">
                    <p className="text-sm font-medium">{t('Selected files:')}</p>
                    <ul className="text-sm text-gray-600">
                      {documents.map((file, index) => (
                        <li key={index}>• {file.name}</li>
                      ))}
                    </ul>
                  </div>
                )}
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
              <div>{t('legal.clientCreatedSuccess')}</div>
              {riskLevel && (
                <div className={`p-1 rounded text-sm ${
                  riskLevel === 'HIGH' ? 'bg-red-100 text-red-800' :
                  riskLevel === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  <ShieldAlert className="h-4 w-4 inline mr-1" />
                  {t('legal.riskLevel')}: {riskLevel}
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
