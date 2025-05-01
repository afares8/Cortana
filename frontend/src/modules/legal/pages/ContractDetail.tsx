import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Separator } from '../../../components/ui/separator';
import { Badge } from '../../../components/ui/badge';
import { 
  getContract, 
  updateContract, 
  deleteContract, 
  getContractVersions,
  getClients 
} from '../api/legalApi';
import { Contract, ContractUpdate, ContractVersion, Client } from '../types';
import { 
  Loader2, 
  ArrowLeft, 
  Save, 
  Trash2, 
  FileText, 
  History, 
  Calendar,
  User,
  AlertTriangle,
  Download,
  Upload,
  Clock
} from 'lucide-react';
import { format, parseISO, differenceInDays } from 'date-fns';

const ContractDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [contract, setContract] = useState<Contract | null>(null);
  const [versions, setVersions] = useState<ContractVersion[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [formData, setFormData] = useState<ContractUpdate>({});
  const [activeTab, setActiveTab] = useState<string>('details');
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);

  useEffect(() => {
    if (id === 'new') {
      const params = new URLSearchParams(location.search);
      const clientId = params.get('client_id');
      if (clientId) {
        setFormData(prev => ({ ...prev, client_id: parseInt(clientId) }));
      }
    }
  }, [id, location.search]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const clientsData = await getClients();
        setClients(clientsData);
        
        if (id === 'new') {
          setFormData({
            title: '',
            contract_type: 'Service Agreement',
            start_date: new Date().toISOString().split('T')[0],
            responsible_lawyer: '',
            status: 'draft'
          });
          return;
        }
        
        const [contractData, versionsData] = await Promise.all([
          getContract(parseInt(id || '0')),
          getContractVersions(parseInt(id || '0'))
        ]);
        
        setContract(contractData);
        setVersions(versionsData);
        
        setFormData({
          title: contractData.title,
          client_id: contractData.client_id,
          contract_type: contractData.contract_type,
          start_date: contractData.start_date.split('T')[0],
          expiration_date: contractData.expiration_date ? contractData.expiration_date.split('T')[0] : undefined,
          responsible_lawyer: contractData.responsible_lawyer,
          description: contractData.description,
          status: contractData.status
        });
      } catch (error) {
        console.error('Error fetching data:', error);
        
        if (id !== 'new') {
          const mockContract: Contract = {
            id: parseInt(id || '1'),
            title: 'Manufacturing Agreement',
            client_id: 1,
            client_name: 'Acme Corporation',
            contract_type: 'Service Agreement',
            start_date: '2023-02-15T00:00:00Z',
            expiration_date: '2024-02-15T00:00:00Z',
            responsible_lawyer: 'Jane Smith',
            description: 'Agreement for manufacturing perfume products',
            status: 'active',
            file_path: '/uploads/contracts/contract_1.pdf',
            created_at: '2023-02-10T14:30:00Z',
            updated_at: '2023-06-20T14:45:00Z'
          };
          
          const mockVersions: ContractVersion[] = [
            {
              id: 1,
              contract_id: parseInt(id || '1'),
              version: 1,
              file_path: '/uploads/contracts/contract_1_v1.pdf',
              changes_description: 'Initial version',
              created_by: 'Jane Smith',
              created_at: '2023-02-10T14:30:00Z'
            },
            {
              id: 2,
              contract_id: parseInt(id || '1'),
              version: 2,
              file_path: '/uploads/contracts/contract_1_v2.pdf',
              changes_description: 'Updated pricing terms',
              created_by: 'Jane Smith',
              created_at: '2023-04-15T09:45:00Z'
            }
          ];
          
          setContract(mockContract);
          setVersions(mockVersions);
          
          setFormData({
            title: mockContract.title,
            client_id: mockContract.client_id,
            contract_type: mockContract.contract_type,
            start_date: mockContract.start_date.split('T')[0],
            expiration_date: mockContract.expiration_date ? mockContract.expiration_date.split('T')[0] : undefined,
            responsible_lawyer: mockContract.responsible_lawyer,
            description: mockContract.description,
            status: mockContract.status
          });
        }
        
        setClients([
          { id: 1, name: 'Acme Corporation', contact_email: 'contact@acme.com', kyc_verified: true, created_at: '2023-01-15T10:30:00Z' },
          { id: 2, name: 'TechStart Inc', contact_email: 'legal@techstart.io', kyc_verified: true, created_at: '2023-03-10T09:15:00Z' },
          { id: 3, name: 'Global Fragrances Ltd', contact_email: 'info@globalfragrances.com', kyc_verified: false, created_at: '2023-05-22T16:40:00Z' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      const base64Content = btoa(content);
      setFileContent(base64Content);
      setFormData(prev => ({ 
        ...prev, 
        file_content: base64Content,
        changes_description: id === 'new' ? 'Initial version' : 'Updated contract'
      }));
    };
    reader.readAsBinaryString(file);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      if (id === 'new') {
        console.log('Creating new contract:', formData);
        navigate('/legal/contracts');
      } else {
        console.log('Updating contract:', formData);
        await updateContract(parseInt(id || '0'), formData);
        if (contract) {
          setContract({
            ...contract,
            ...formData,
            updated_at: new Date().toISOString()
          });
        }
        
        if (formData.file_content) {
          const versionsData = await getContractVersions(parseInt(id || '0'));
          setVersions(versionsData);
        }
      }
    } catch (error) {
      console.error('Error saving contract:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this contract?')) return;
    
    try {
      setSaving(true);
      await deleteContract(parseInt(id || '0'));
      navigate('/legal/contracts');
    } catch (error) {
      console.error('Error deleting contract:', error);
    } finally {
      setSaving(false);
    }
  };

  const getExpirationStatus = () => {
    if (!contract?.expiration_date) return null;
    
    const expDate = parseISO(contract.expiration_date);
    const now = new Date();
    const daysRemaining = differenceInDays(expDate, now);
    
    if (daysRemaining < 0) {
      return (
        <div className="flex items-center gap-2 text-red-600">
          <AlertTriangle size={16} />
          <span>Expired {Math.abs(daysRemaining)} days ago</span>
        </div>
      );
    } else if (daysRemaining <= 30) {
      return (
        <div className="flex items-center gap-2 text-yellow-600">
          <AlertTriangle size={16} />
          <span>Expires in {daysRemaining} days</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center gap-2 text-green-600">
          <Calendar size={16} />
          <span>Expires in {daysRemaining} days</span>
        </div>
      );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Active</Badge>;
      case 'expired':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">Expired</Badge>;
      case 'draft':
        return <Badge variant="outline">Draft</Badge>;
      case 'terminated':
        return <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">Terminated</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
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
          onClick={() => navigate('/legal/contracts')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Contracts
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {id === 'new' ? 'New Contract' : contract?.title}
          </h1>
          {contract && (
            <div className="flex items-center gap-4 text-gray-500">
              <span>ID: {contract.id}</span>
              <span>•</span>
              <span>Created: {format(parseISO(contract.created_at), 'MMM d, yyyy')}</span>
              {contract.updated_at && (
                <>
                  <span>•</span>
                  <span>Updated: {format(parseISO(contract.updated_at), 'MMM d, yyyy')}</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {contract && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <User size={16} className="text-gray-500" />
                <span className="text-gray-500">Client:</span>
                <span className="font-medium">{contract.client_name}</span>
              </div>
              <div className="flex items-center gap-2 mb-2">
                <FileText size={16} className="text-gray-500" />
                <span className="text-gray-500">Type:</span>
                <span className="font-medium">{contract.contract_type}</span>
              </div>
              <div className="flex items-center gap-2">
                <User size={16} className="text-gray-500" />
                <span className="text-gray-500">Responsible:</span>
                <span className="font-medium">{contract.responsible_lawyer}</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <Calendar size={16} className="text-gray-500" />
                <span className="text-gray-500">Start Date:</span>
                <span className="font-medium">
                  {format(parseISO(contract.start_date), 'MMM d, yyyy')}
                </span>
              </div>
              {contract.expiration_date && (
                <div className="flex items-center gap-2">
                  <Calendar size={16} className="text-gray-500" />
                  <span className="text-gray-500">Expiration Date:</span>
                  <span className="font-medium">
                    {format(parseISO(contract.expiration_date), 'MMM d, yyyy')}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <Clock size={16} className="text-gray-500" />
                <span className="text-gray-500">Status:</span>
                {getStatusBadge(contract.status)}
              </div>
              {contract.expiration_date && getExpirationStatus()}
              <div className="flex items-center gap-2 mt-2">
                <History size={16} className="text-gray-500" />
                <span className="text-gray-500">Versions:</span>
                <span className="font-medium">{versions.length}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="details">
            <FileText className="h-4 w-4 mr-2" />
            Contract Details
          </TabsTrigger>
          <TabsTrigger value="versions" disabled={id === 'new'}>
            <History className="h-4 w-4 mr-2" />
            Version History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <Card>
            <CardHeader>
              <CardTitle>{id === 'new' ? 'Create New Contract' : 'Edit Contract Details'}</CardTitle>
              <CardDescription>
                {id === 'new' 
                  ? 'Add a new contract to your legal registry' 
                  : 'Update the information for this contract'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Contract Title</Label>
                    <Input 
                      id="title" 
                      name="title" 
                      value={formData.title || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter contract title"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="client_id">Client</Label>
                    <select
                      id="client_id"
                      name="client_id"
                      value={formData.client_id || ''}
                      onChange={handleInputChange}
                      className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    >
                      <option value="">Select a client</option>
                      {clients.map(client => (
                        <option key={client.id} value={client.id}>
                          {client.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="contract_type">Contract Type</Label>
                    <select
                      id="contract_type"
                      name="contract_type"
                      value={formData.contract_type || ''}
                      onChange={handleInputChange}
                      className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    >
                      <option value="Service Agreement">Service Agreement</option>
                      <option value="NDA">Non-Disclosure Agreement</option>
                      <option value="License">License Agreement</option>
                      <option value="Employment">Employment Contract</option>
                      <option value="Purchase">Purchase Agreement</option>
                      <option value="Distribution">Distribution Agreement</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="responsible_lawyer">Responsible Lawyer</Label>
                    <Input 
                      id="responsible_lawyer" 
                      name="responsible_lawyer" 
                      value={formData.responsible_lawyer || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter responsible lawyer"
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="start_date">Start Date</Label>
                    <Input 
                      id="start_date" 
                      name="start_date" 
                      type="date" 
                      value={formData.start_date || ''} 
                      onChange={handleInputChange}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="expiration_date">Expiration Date</Label>
                    <Input 
                      id="expiration_date" 
                      name="expiration_date" 
                      type="date" 
                      value={formData.expiration_date || ''} 
                      onChange={handleInputChange}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <select
                      id="status"
                      name="status"
                      value={formData.status || ''}
                      onChange={handleInputChange}
                      className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    >
                      <option value="draft">Draft</option>
                      <option value="active">Active</option>
                      <option value="expired">Expired</option>
                      <option value="terminated">Terminated</option>
                    </select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea 
                      id="description" 
                      name="description" 
                      value={formData.description || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter contract description"
                      rows={3}
                    />
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <Label htmlFor="file">Upload Contract Document</Label>
                <div className="mt-2 flex items-center gap-4">
                  <Input 
                    id="file" 
                    type="file" 
                    accept=".pdf,.docx,.doc" 
                    onChange={handleFileChange}
                  />
                  {id !== 'new' && contract?.file_path && (
                    <Button variant="outline" className="flex items-center gap-2">
                      <Download className="h-4 w-4" />
                      Download Current Version
                    </Button>
                  )}
                </div>
                {id !== 'new' && (
                  <div className="mt-2">
                    <Label htmlFor="changes_description">Changes Description</Label>
                    <Input 
                      id="changes_description" 
                      name="changes_description" 
                      value={formData.changes_description || ''} 
                      onChange={handleInputChange} 
                      placeholder="Describe the changes in this version"
                      className="mt-1"
                    />
                  </div>
                )}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button 
                variant="destructive" 
                onClick={handleDelete}
                disabled={id === 'new' || saving}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Contract
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
                    {id === 'new' ? 'Create Contract' : 'Save Changes'}
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
              <CardDescription>
                Track changes to this contract over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              {versions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No versions found for this contract.
                </div>
              ) : (
                <div className="space-y-4">
                  {versions.map((version) => (
                    <div 
                      key={version.id} 
                      className={`p-4 border rounded-lg ${selectedVersion === version.version ? 'border-primary bg-primary/5' : 'border-border'}`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">Version {version.version}</Badge>
                            <span className="text-sm text-gray-500">
                              {format(parseISO(version.created_at), 'MMM d, yyyy h:mm a')}
                            </span>
                          </div>
                          <h3 className="font-medium mt-2">
                            {version.changes_description || 'No description provided'}
                          </h3>
                          <p className="text-sm text-gray-500 mt-1">
                            Created by: {version.created_by}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="flex items-center gap-1"
                            onClick={() => setSelectedVersion(version.version === selectedVersion ? null : version.version)}
                          >
                            {selectedVersion === version.version ? 'Hide' : 'View'}
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="flex items-center gap-1"
                          >
                            <Download className="h-4 w-4" />
                            Download
                          </Button>
                        </div>
                      </div>
                      
                      {selectedVersion === version.version && (
                        <div className="mt-4 p-4 bg-gray-50 rounded border">
                          <div className="text-center text-gray-500">
                            Document preview would appear here
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
            <CardFooter>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Upload className="h-4 w-4" />
                <span>Upload a new version using the Contract Details tab</span>
              </div>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ContractDetail;
