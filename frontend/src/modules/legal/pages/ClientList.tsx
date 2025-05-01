import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '../../../components/ui/table';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { getClients } from '../api/legalApi';
import { Client } from '../types';
import { Loader2, Plus, Search, Filter } from 'lucide-react';

const ClientList: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [industryFilter, setIndustryFilter] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchClients = async () => {
      try {
        setLoading(true);
        const data = await getClients();
        setClients(data);
      } catch (error) {
        console.error('Error fetching clients:', error);
        setClients([
          {
            id: 1,
            name: 'Acme Corporation',
            contact_email: 'contact@acme.com',
            contact_phone: '+1 555-123-4567',
            address: '123 Business Ave, Suite 100, New York, NY 10001',
            industry: 'Manufacturing',
            kyc_verified: true,
            notes: 'Long-term client since 2020',
            created_at: '2023-01-15T10:30:00Z',
            updated_at: '2023-06-20T14:45:00Z'
          },
          {
            id: 2,
            name: 'TechStart Inc',
            contact_email: 'legal@techstart.io',
            contact_phone: '+1 555-987-6543',
            address: '456 Innovation Blvd, San Francisco, CA 94107',
            industry: 'Technology',
            kyc_verified: true,
            notes: 'Startup client with rapid growth',
            created_at: '2023-03-10T09:15:00Z',
            updated_at: '2023-07-05T11:20:00Z'
          },
          {
            id: 3,
            name: 'Global Fragrances Ltd',
            contact_email: 'info@globalfragrances.com',
            contact_phone: '+1 555-456-7890',
            address: '789 Perfume Lane, Miami, FL 33101',
            industry: 'Perfumery',
            kyc_verified: false,
            notes: 'Pending KYC verification documents',
            created_at: '2023-05-22T16:40:00Z',
            updated_at: undefined
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchClients();
  }, []);

  const filteredClients = clients.filter(client => {
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         client.contact_email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesIndustry = industryFilter === '' || 
                           client.industry?.toLowerCase() === industryFilter.toLowerCase();
    
    return matchesSearch && matchesIndustry;
  });

  const industries = Array.from(new Set(clients.map(client => client.industry).filter(Boolean) as string[]));

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Client Registry</h1>
          <p className="text-gray-500">Manage your legal clients</p>
        </div>
        <Button 
          onClick={() => navigate('/legal/clients/new')}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          Add New Client
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Search and filter clients</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <Input
                  type="text"
                  placeholder="Search by name or email..."
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="w-full md:w-1/3">
              <div className="relative">
                <Filter className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <select
                  className="w-full pl-8 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={industryFilter}
                  onChange={(e) => setIndustryFilter(e.target.value)}
                >
                  <option value="">All Industries</option>
                  {industries.map((industry) => (
                    <option key={industry} value={industry}>
                      {industry}
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
                  <TableHead>Name</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Industry</TableHead>
                  <TableHead>KYC Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredClients.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                      No clients found. Try adjusting your filters or add a new client.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredClients.map((client) => (
                    <TableRow key={client.id} className="cursor-pointer hover:bg-gray-50" onClick={() => navigate(`/legal/clients/${client.id}`)}>
                      <TableCell className="font-medium">{client.name}</TableCell>
                      <TableCell>
                        <div>{client.contact_email}</div>
                        <div className="text-sm text-gray-500">{client.contact_phone}</div>
                      </TableCell>
                      <TableCell>{client.industry || 'N/A'}</TableCell>
                      <TableCell>
                        {client.kyc_verified ? (
                          <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Verified</Badge>
                        ) : (
                          <Badge variant="outline" className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Pending</Badge>
                        )}
                      </TableCell>
                      <TableCell>{new Date(client.created_at).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/legal/clients/${client.id}`);
                          }}
                        >
                          View
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

export default ClientList;
