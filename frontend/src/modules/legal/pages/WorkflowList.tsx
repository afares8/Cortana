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
import { getWorkflowTemplates, getWorkflowInstances } from '../api/legalApi';
import { WorkflowTemplate, WorkflowInstance } from '../types';
import { Loader2, Plus, Search, Filter, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { format, parseISO } from 'date-fns';

const WorkflowList: React.FC = () => {
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [instances, setInstances] = useState<WorkflowInstance[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'templates' | 'instances'>('templates');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [templatesData, instancesData] = await Promise.all([
          getWorkflowTemplates(),
          getWorkflowInstances()
        ]);
        setTemplates(templatesData);
        setInstances(instancesData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setTemplates([
          {
            id: 'legal-approval-standard',
            name: 'Standard Legal Approval',
            description: 'Standard approval workflow for legal documents',
            steps: [
              {
                step_id: 'legal-review',
                role: 'Legal Counsel',
                approver_email: 'legal@example.com',
                is_approved: false
              },
              {
                step_id: 'finance-review',
                role: 'Finance Director',
                approver_email: 'finance@example.com',
                is_approved: false
              },
              {
                step_id: 'ceo-approval',
                role: 'CEO',
                approver_email: 'ceo@example.com',
                is_approved: false
              }
            ],
            created_at: '2023-01-15T10:30:00Z',
            updated_at: '2023-06-20T14:45:00Z'
          },
          {
            id: 'nda-approval',
            name: 'NDA Approval Process',
            description: 'Streamlined approval for non-disclosure agreements',
            steps: [
              {
                step_id: 'legal-review',
                role: 'Legal Counsel',
                approver_email: 'legal@example.com',
                is_approved: false
              },
              {
                step_id: 'department-head',
                role: 'Department Head',
                approver_email: 'department@example.com',
                is_approved: false
              }
            ],
            created_at: '2023-02-10T09:15:00Z',
            updated_at: '2023-05-05T11:30:00Z'
          }
        ]);
        
        setInstances([
          {
            id: 1,
            template_id: 'legal-approval-standard',
            contract_id: 1,
            current_step_id: 'finance-review',
            status: 'pending',
            steps: [
              {
                step_id: 'legal-review',
                role: 'Legal Counsel',
                approver_email: 'legal@example.com',
                is_approved: true,
                approved_at: '2023-07-10T14:30:00Z',
                comments: 'Approved with minor changes'
              },
              {
                step_id: 'finance-review',
                role: 'Finance Director',
                approver_email: 'finance@example.com',
                is_approved: false
              },
              {
                step_id: 'ceo-approval',
                role: 'CEO',
                approver_email: 'ceo@example.com',
                is_approved: false
              }
            ],
            created_at: '2023-07-05T10:30:00Z',
            updated_at: '2023-07-10T14:30:00Z'
          },
          {
            id: 2,
            template_id: 'nda-approval',
            contract_id: 2,
            current_step_id: 'department-head',
            status: 'pending',
            steps: [
              {
                step_id: 'legal-review',
                role: 'Legal Counsel',
                approver_email: 'legal@example.com',
                is_approved: true,
                approved_at: '2023-07-12T11:45:00Z',
                comments: 'Approved'
              },
              {
                step_id: 'department-head',
                role: 'Department Head',
                approver_email: 'department@example.com',
                is_approved: false
              }
            ],
            created_at: '2023-07-08T09:15:00Z',
            updated_at: '2023-07-12T11:45:00Z'
          },
          {
            id: 3,
            template_id: 'legal-approval-standard',
            contract_id: 3,
            current_step_id: 'ceo-approval',
            status: 'approved',
            steps: [
              {
                step_id: 'legal-review',
                role: 'Legal Counsel',
                approver_email: 'legal@example.com',
                is_approved: true,
                approved_at: '2023-06-05T10:30:00Z',
                comments: 'Approved'
              },
              {
                step_id: 'finance-review',
                role: 'Finance Director',
                approver_email: 'finance@example.com',
                is_approved: true,
                approved_at: '2023-06-07T14:15:00Z',
                comments: 'Approved with financial adjustments'
              },
              {
                step_id: 'ceo-approval',
                role: 'CEO',
                approver_email: 'ceo@example.com',
                is_approved: true,
                approved_at: '2023-06-10T09:45:00Z',
                comments: 'Final approval granted'
              }
            ],
            created_at: '2023-06-01T08:30:00Z',
            updated_at: '2023-06-10T09:45:00Z'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredTemplates = templates.filter(template => 
    template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredInstances = instances.filter(instance => {
    const matchesSearch = 
      instance.template_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      instance.status.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === '' || instance.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Pending</Badge>;
      case 'approved':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Approved</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">Rejected</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getProgressIndicator = (instance: WorkflowInstance) => {
    const totalSteps = instance.steps.length;
    const completedSteps = instance.steps.filter(step => step.is_approved).length;
    const progress = Math.round((completedSteps / totalSteps) * 100);
    
    return (
      <div className="w-full">
        <div className="flex justify-between text-xs mb-1">
          <span>{completedSteps} of {totalSteps} steps</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary h-2 rounded-full" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Approval Workflows</h1>
          <p className="text-gray-500">Manage approval workflows for legal documents</p>
        </div>
        <Button 
          onClick={() => navigate('/legal/workflows/templates/new')}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          New Workflow Template
        </Button>
      </div>

      <div className="flex space-x-2 mb-6">
        <Button
          variant={activeTab === 'templates' ? 'default' : 'outline'}
          onClick={() => setActiveTab('templates')}
        >
          Workflow Templates
        </Button>
        <Button
          variant={activeTab === 'instances' ? 'default' : 'outline'}
          onClick={() => setActiveTab('instances')}
        >
          Active Approvals
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Search and filter workflows</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <Input
                  type="text"
                  placeholder={activeTab === 'templates' ? "Search templates..." : "Search approvals..."}
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            
            {activeTab === 'instances' && (
              <div className="w-full md:w-1/3">
                <div className="relative">
                  <Filter className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                  <select
                    className="w-full pl-8 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <option value="">All Statuses</option>
                    <option value="pending">Pending</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
              </div>
            )}
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
            {activeTab === 'templates' ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Steps</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTemplates.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                        No workflow templates found. Create a new template to get started.
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredTemplates.map((template) => (
                      <TableRow key={template.id} className="cursor-pointer hover:bg-gray-50" onClick={() => navigate(`/legal/workflows/templates/${template.id}`)}>
                        <TableCell className="font-medium">{template.name}</TableCell>
                        <TableCell>{template.description || 'No description'}</TableCell>
                        <TableCell>
                          <div className="flex flex-col gap-1">
                            <span className="text-sm font-medium">{template.steps.length} approval steps</span>
                            <div className="text-xs text-gray-500">
                              {template.steps.map(step => step.role).join(' → ')}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{format(parseISO(template.created_at), 'MMM d, yyyy')}</TableCell>
                        <TableCell className="text-right">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/legal/workflows/templates/${template.id}`);
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
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Contract</TableHead>
                    <TableHead>Template</TableHead>
                    <TableHead>Current Step</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Updated</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredInstances.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                        No approval workflows found. Start a new approval process from a contract.
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredInstances.map((instance) => {
                      const currentStep = instance.steps.find(step => step.step_id === instance.current_step_id);
                      
                      return (
                        <TableRow key={instance.id} className="cursor-pointer hover:bg-gray-50" onClick={() => navigate(`/legal/workflows/instances/${instance.id}`)}>
                          <TableCell className="font-medium">Contract #{instance.contract_id}</TableCell>
                          <TableCell>
                            {templates.find(t => t.id === instance.template_id)?.name || instance.template_id}
                          </TableCell>
                          <TableCell>
                            <div className="flex flex-col">
                              <span>{currentStep?.role || 'Unknown'}</span>
                              <span className="text-xs text-gray-500">{currentStep?.approver_email || ''}</span>
                            </div>
                          </TableCell>
                          <TableCell>{getProgressIndicator(instance)}</TableCell>
                          <TableCell>{getStatusBadge(instance.status)}</TableCell>
                          <TableCell>{format(parseISO(instance.updated_at || instance.created_at), 'MMM d, yyyy')}</TableCell>
                          <TableCell className="text-right">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/legal/workflows/instances/${instance.id}`);
                              }}
                            >
                              View
                            </Button>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default WorkflowList;
