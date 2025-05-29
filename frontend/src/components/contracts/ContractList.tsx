import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '../../components/ui/table';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Loader2, Plus, Search, Filter, AlertTriangle, Calendar } from 'lucide-react';
import { format, parseISO, isAfter, addDays } from 'date-fns';
import { useTranslation } from 'react-i18next';

interface Contract {
  id: number;
  title: string;
  client_id: number;
  client_name: string;
  contract_type: string;
  start_date: string;
  expiration_date: string;
  responsible_lawyer: string;
  status: string;
  file_path: string;
  created_at: string;
}

interface Client {
  id: number;
  name: string;
  contact_email: string;
  kyc_verified: boolean;
  created_at: string;
}

interface ContractListProps {
  getContracts: () => Promise<Contract[]>;
  getClients: () => Promise<Client[]>;
  basePath: string;
  module?: 'legal' | 'general';
}

const ContractList: React.FC<ContractListProps> = ({ 
  getContracts, 
  getClients, 
  basePath,
  module = 'general'
}) => {
  const { t } = useTranslation();
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [clientFilter, setClientFilter] = useState<number | ''>('');
  const navigate = useNavigate();
  // const location = useLocation(); // Uncomment if needed for future routing features

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [contractsData, clientsData] = await Promise.all([
          getContracts(),
          getClients()
        ]);
        setContracts(contractsData);
        setClients(clientsData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setClients([
          { id: 1, name: 'Acme Corporation', contact_email: 'contact@acme.com', kyc_verified: true, created_at: '2023-01-15T10:30:00Z' },
          { id: 2, name: 'TechStart Inc', contact_email: 'legal@techstart.io', kyc_verified: true, created_at: '2023-03-10T09:15:00Z' },
          { id: 3, name: 'Global Fragrances Ltd', contact_email: 'info@globalfragrances.com', kyc_verified: false, created_at: '2023-05-22T16:40:00Z' }
        ]);
        
        setContracts([
          {
            id: 1,
            title: 'Manufacturing Agreement',
            client_id: 1,
            client_name: 'Acme Corporation',
            contract_type: 'Service Agreement',
            start_date: '2023-02-15T00:00:00Z',
            expiration_date: '2024-02-15T00:00:00Z',
            responsible_lawyer: 'Jane Smith',
            status: 'active',
            file_path: '/uploads/contracts/contract_1.pdf',
            created_at: '2023-02-10T14:30:00Z'
          },
          {
            id: 2,
            title: 'Software License Agreement',
            client_id: 2,
            client_name: 'TechStart Inc',
            contract_type: 'License',
            start_date: '2023-04-01T00:00:00Z',
            expiration_date: '2025-04-01T00:00:00Z',
            responsible_lawyer: 'Michael Johnson',
            status: 'active',
            file_path: '/uploads/contracts/contract_2.pdf',
            created_at: '2023-03-25T11:45:00Z'
          },
          {
            id: 3,
            title: 'Non-Disclosure Agreement',
            client_id: 3,
            client_name: 'Global Fragrances Ltd',
            contract_type: 'NDA',
            start_date: '2023-06-01T00:00:00Z',
            expiration_date: '2023-12-01T00:00:00Z',
            responsible_lawyer: 'Sarah Williams',
            status: 'expired',
            file_path: '/uploads/contracts/contract_3.pdf',
            created_at: '2023-05-28T09:20:00Z'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [getContracts, getClients]);

  const filteredContracts = contracts.filter(contract => {
    const matchesSearch = contract.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         contract.responsible_lawyer.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = typeFilter === '' || 
                       contract.contract_type.toLowerCase() === typeFilter.toLowerCase();
    
    const matchesStatus = statusFilter === '' || 
                         contract.status.toLowerCase() === statusFilter.toLowerCase();
    
    const matchesClient = clientFilter === '' || 
                         contract.client_id === clientFilter;
    
    return matchesSearch && matchesType && matchesStatus && matchesClient;
  });

  const contractTypes = Array.from(new Set(contracts.map(contract => contract.contract_type)));
  const statuses = Array.from(new Set(contracts.map(contract => contract.status)));

  const getStatusBadge = (status: string, expirationDate?: string) => {
    if (status === 'active') {
      if (expirationDate) {
        const expDate = parseISO(expirationDate);
        const now = new Date();
        const thirtyDaysFromNow = addDays(now, 30);
        
        if (isAfter(expDate, thirtyDaysFromNow)) {
          return <Badge variant="outline" className="bg-green-100 text-green-800 hover:bg-green-100">{t('contracts.status.active', 'Active')}</Badge>;
        } else {
          return (
            <div className="flex items-center gap-1">
              <Badge variant="outline" className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">{t('contracts.status.expiringSoon', 'Expiring Soon')}</Badge>
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
            </div>
          );
        }
      }
      return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">{t('contracts.status.active', 'Active')}</Badge>;
    } else if (status === 'expired') {
      return <Badge variant="outline" className="bg-red-100 text-red-800 hover:bg-red-100">{t('contracts.status.expired', 'Expired')}</Badge>;
    } else if (status === 'draft') {
      return <Badge variant="outline">{t('contracts.status.draft', 'Draft')}</Badge>;
    } else if (status === 'terminated') {
      return <Badge variant="outline" className="bg-gray-100 text-gray-800 hover:bg-gray-100">{t('contracts.status.terminated', 'Terminated')}</Badge>;
    } else {
      return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getNewContractPath = () => {
    if (module === 'legal') {
      return `${basePath}/new`;
    } else {
      return `${basePath}/upload`;
    }
  };

  const getContractDetailPath = (contractId: number) => {
    return `${basePath}/${contractId}`;
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">{t('contracts.title', 'Contract Management')}</h1>
          <p className="text-gray-500">{t('contracts.subtitle', 'Manage your legal contracts and agreements')}</p>
        </div>
        <Button 
          onClick={() => navigate(getNewContractPath())}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          {module === 'legal' 
            ? t('contracts.addNew', 'Add New Contract') 
            : t('contracts.upload', 'Upload New Contract')}
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>{t('common.filters', 'Filters')}</CardTitle>
          <CardDescription>{t('contracts.filterDescription', 'Search and filter contracts')}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <Input
                  type="text"
                  placeholder={t('contracts.searchPlaceholder', 'Search by title or lawyer...')}
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            
            <div>
              <div className="relative">
                <Filter className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <select
                  className="w-full pl-8 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <option value="">{t('contracts.allTypes', 'All Contract Types')}</option>
                  {contractTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <div className="relative">
                <Filter className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <select
                  className="w-full pl-8 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">{t('contracts.allStatuses', 'All Statuses')}</option>
                  {statuses.map((status) => (
                    <option key={status} value={status}>
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <div className="relative">
                <Filter className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <select
                  className="w-full pl-8 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={clientFilter}
                  onChange={(e) => setClientFilter(e.target.value ? parseInt(e.target.value) : '')}
                >
                  <option value="">{t('contracts.allClients', 'All Clients')}</option>
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>
                      {client.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('contracts.columns.title', 'Title')}</TableHead>
                  <TableHead>{t('contracts.columns.client', 'Client')}</TableHead>
                  <TableHead>{t('contracts.columns.type', 'Type')}</TableHead>
                  <TableHead>{t('contracts.columns.dates', 'Dates')}</TableHead>
                  <TableHead>{t('contracts.columns.status', 'Status')}</TableHead>
                  <TableHead>{t('contracts.columns.responsible', 'Responsible')}</TableHead>
                  <TableHead className="text-right">{t('common.actions', 'Actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredContracts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                      {t('contracts.noContractsFound', 'No contracts found. Try adjusting your filters or add a new contract.')}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredContracts.map((contract) => (
                    <TableRow key={contract.id} className="cursor-pointer hover:bg-gray-50" onClick={() => navigate(getContractDetailPath(contract.id))}>
                      <TableCell className="font-medium">{contract.title}</TableCell>
                      <TableCell>{contract.client_name}</TableCell>
                      <TableCell>{contract.contract_type}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4 text-gray-500" />
                          <span>{format(parseISO(contract.start_date), 'MMM d, yyyy')}</span>
                        </div>
                        {contract.expiration_date && (
                          <div className="flex items-center gap-1 text-sm text-gray-500">
                            <span>{t('contracts.expires', 'Expires')}: {format(parseISO(contract.expiration_date), 'MMM d, yyyy')}</span>
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(contract.status, contract.expiration_date)}
                      </TableCell>
                      <TableCell>{contract.responsible_lawyer}</TableCell>
                      <TableCell className="text-right">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(getContractDetailPath(contract.id));
                          }}
                        >
                          {t('common.view', 'View')}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ContractList;
