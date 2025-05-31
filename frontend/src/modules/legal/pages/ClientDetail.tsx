import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Textarea } from '../../../components/ui/textarea';
import { Checkbox } from '../../../components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Separator } from '../../../components/ui/separator';
import { getClient, updateClient, deleteClient } from '../api/legalApi';
import { Client, ClientUpdate } from '../types';
import { Loader2, ArrowLeft, Save, Trash2, FileText, ClipboardList, ShieldAlert, FileDown } from 'lucide-react';
import { API_BASE_URL } from '../../../constants';
import { useTranslation } from 'react-i18next';

const ClientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [client, setClient] = useState<Client | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [formData, setFormData] = useState<ClientUpdate>({});
  const [activeTab, setActiveTab] = useState<string>('details');
  const [generatingReport, setGeneratingReport] = useState<boolean>(false);

  useEffect(() => {
    const fetchClient = async () => {
      if (!id || id === 'new') return;
      
      try {
        setLoading(true);
        const data = await getClient(parseInt(id));
        setClient(data);
        setFormData({
          name: data.name,
          contact_email: data.contact_email,
          contact_phone: data.contact_phone,
          address: data.address,
          industry: data.industry,
          kyc_verified: data.kyc_verified,
          notes: data.notes
        });
      } catch (error) {
        console.error('Error fetching client:', error);
        const mockClient: Client = {
          id: parseInt(id),
          name: 'Acme Corporation',
          contact_email: 'contact@acme.com',
          contact_phone: '+1 555-123-4567',
          address: '123 Business Ave, Suite 100, New York, NY 10001',
          industry: 'Manufacturing',
          kyc_verified: true,
          notes: 'Long-term client since 2020',
          created_at: '2023-01-15T10:30:00Z',
          updated_at: '2023-06-20T14:45:00Z'
        };
        setClient(mockClient);
        setFormData({
          name: mockClient.name,
          contact_email: mockClient.contact_email,
          contact_phone: mockClient.contact_phone,
          address: mockClient.address,
          industry: mockClient.industry,
          kyc_verified: mockClient.kyc_verified,
          notes: mockClient.notes
        });
      } finally {
        setLoading(false);
      }
    };

    fetchClient();
  }, [id]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (checked: boolean) => {
    setFormData(prev => ({ ...prev, kyc_verified: checked }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      if (id === 'new') {
        console.log('Creating new client:', formData);
        navigate('/legal/clients');
      } else {
        console.log('Updating client:', formData);
        await updateClient(parseInt(id || '0'), formData);
        if (client) {
          setClient({
            ...client,
            ...formData,
            updated_at: new Date().toISOString()
          });
        }
      }
    } catch (error) {
      console.error('Error saving client:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this client?')) return;
    
    try {
      setSaving(true);
      await deleteClient(parseInt(id || '0'));
      navigate('/legal/clients');
    } catch (error) {
      console.error('Error deleting client:', error);
    } finally {
      setSaving(false);
    }
  };
  
  const generateUAFReport = async (clientId: number) => {
    try {
      setGeneratingReport(true);
      
      const response = await fetch(`${API_BASE_URL}/compliance/uaf-reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: clientId,
          start_date: new Date(Date.now() - 30*24*60*60*1000).toISOString(), // Last 30 days
          end_date: new Date().toISOString()
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate UAF report');
      }
      
      const report = await response.json();
      
      if (report.id) {
        window.open(`${API_BASE_URL}/compliance/reports/${report.id}/download`, '_blank');
      }
      
    } catch (error) {
      console.error('Error generating UAF report:', error);
    } finally {
      setGeneratingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <Button 
          variant="outline" 
          size="sm" 
          className="mr-4"
          onClick={() => navigate('/legal/clients')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Clients
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {id === 'new' ? 'New Client' : client?.name}
          </h1>
          {client && (
            <p className="text-gray-500">
              Client ID: {client.id} • Created: {new Date(client.created_at).toLocaleDateString()}
            </p>
          )}
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="details">
            <FileText className="h-4 w-4 mr-2" />
            Client Details
          </TabsTrigger>
          <TabsTrigger value="contracts">
            <ClipboardList className="h-4 w-4 mr-2" />
            Related Contracts
          </TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <Card>
            <CardHeader>
              <CardTitle>{id === 'new' ? 'Create New Client' : 'Edit Client Details'}</CardTitle>
              <CardDescription>
                {id === 'new' 
                  ? 'Add a new client to your legal registry' 
                  : 'Update the information for this client'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Client Name</Label>
                    <Input 
                      id="name" 
                      name="name" 
                      value={formData.name || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter client name"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="contact_email">Email Address</Label>
                    <Input 
                      id="contact_email" 
                      name="contact_email" 
                      type="email" 
                      value={formData.contact_email || ''} 
                      onChange={handleInputChange} 
                      placeholder="contact@example.com"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="contact_phone">Phone Number</Label>
                    <Input 
                      id="contact_phone" 
                      name="contact_phone" 
                      value={formData.contact_phone || ''} 
                      onChange={handleInputChange} 
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="industry">{t('Industry')}</Label>
                    <Input 
                      id="industry" 
                      name="industry" 
                      value={formData.industry || ''} 
                      onChange={handleInputChange} 
                      placeholder={t('e.g. Technology, Manufacturing, etc.')}
                    />
                  </div>
                  
                  {/* Add Risk Level Display */}
                  {client && client.risk_level && (
                    <div className="space-y-2">
                      <Label htmlFor="risk-level">{t('legal.riskLevel')}</Label>
                      <div className={`p-2 rounded flex items-center ${
                        client.risk_level === 'HIGH' ? 'bg-red-100 text-red-800' :
                        client.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        <ShieldAlert className="h-4 w-4 mr-2" />
                        {client.risk_level || t('Not Assessed')}
                        {client.risk_score && ` (${client.risk_score})`}
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="address">Address</Label>
                    <Textarea 
                      id="address" 
                      name="address" 
                      value={formData.address || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter client address"
                      rows={3}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="notes">Notes</Label>
                    <Textarea 
                      id="notes" 
                      name="notes" 
                      value={formData.notes || ''} 
                      onChange={handleInputChange} 
                      placeholder="Additional notes about this client"
                      rows={3}
                    />
                  </div>
                  
                  <div className="flex items-center space-x-2 pt-4">
                    <Checkbox 
                      id="kyc_verified" 
                      checked={formData.kyc_verified || false} 
                      onCheckedChange={handleCheckboxChange}
                    />
                    <Label htmlFor="kyc_verified" className="font-normal">
                      {t('KYC Verification Completed')}
                    </Label>
                  </div>
                  
                  {/* Add PEP/Sanctions Verification Status */}
                  {client && (client.verification_status || client.verification_result) && (
                    <div className="space-y-2 mt-4">
                      <Label htmlFor="verification-status">{t('Verification Status')}</Label>
                      <div className="space-y-2">
                        <div className={`p-2 rounded ${
                          client.verification_result?.pep_status === 'match' ? 'bg-red-100 text-red-800' :
                          client.verification_result?.pep_status === 'no_match' ? 'bg-green-100 text-green-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {t('PEP Check')}: {client.verification_result?.pep_status || t('Pending')}
                        </div>
                        <div className={`p-2 rounded ${
                          client.verification_result?.sanctions_status === 'match' ? 'bg-red-100 text-red-800' :
                          client.verification_result?.sanctions_status === 'no_match' ? 'bg-green-100 text-green-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {t('Sanctions Check')}: {client.verification_result?.sanctions_status || t('Pending')}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Generate UAF Button - only for high-risk clients */}
                  {client && client.risk_level === 'HIGH' && (
                    <div className="mt-4">
                      <Button 
                        onClick={() => generateUAFReport(client.id)}
                        disabled={generatingReport}
                        className="w-full"
                      >
                        {generatingReport ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            {t('Generating...')}
                          </>
                        ) : (
                          <>
                            <FileDown className="h-4 w-4 mr-2" />
                            {t('Generate UAF Report')}
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button 
                variant="destructive" 
                onClick={handleDelete}
                disabled={id === 'new' || saving}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Client
              </Button>
              <Button 
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    {id === 'new' ? 'Create Client' : 'Save Changes'}
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="contracts">
          <Card>
            <CardHeader>
              <CardTitle>Related Contracts</CardTitle>
              <CardDescription>
                Contracts associated with {client?.name || 'this client'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {id === 'new' ? (
                <div className="text-center py-8 text-gray-500">
                  Save the client first to add contracts
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Active Contracts</h3>
                    <Button 
                      size="sm" 
                      onClick={() => navigate(`/legal/contracts/new?client_id=${id}`)}
                    >
                      Add Contract
                    </Button>
                  </div>
                  
                  <Separator />
                  
                  <div className="py-4 text-center text-gray-500">
                    No active contracts found for this client.
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ClientDetail;
