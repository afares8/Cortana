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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Separator } from '../../../components/ui/separator';
import { Badge } from '../../../components/ui/badge';
import { 
  getWorkflowTemplate, 
  updateWorkflowTemplate, 
  deleteWorkflowTemplate,
  getWorkflowInstance,
  updateWorkflowStep
} from '../api/legalApi';
import { WorkflowTemplate, WorkflowInstance, WorkflowStep, WorkflowTemplateUpdate } from '../types';
import { 
  Loader2, 
  ArrowLeft, 
  Save, 
  Trash2, 
  Plus, 
  X, 
  ArrowDown, 
  CheckCircle2, 
  XCircle,
  AlertTriangle,
  User,
  Mail,
  Clock
} from 'lucide-react';
import { format, parseISO } from 'date-fns';

const WorkflowDetail: React.FC = () => {
  const { type, id } = useParams<{ type: string; id: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<WorkflowTemplate | WorkflowInstance | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [formData, setFormData] = useState<WorkflowTemplateUpdate>({});
  const [newStep, setNewStep] = useState<Partial<WorkflowStep>>({
    role: '',
    approver_email: '',
    is_approved: false
  });
  const [activeTab, setActiveTab] = useState<string>('details');
  const [approvalComment, setApprovalComment] = useState<string>('');

  const isTemplate = type === 'templates';
  const isInstance = type === 'instances';

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        if (isTemplate) {
          const templateData = await getWorkflowTemplate(id || '');
          setData(templateData);
          setFormData({
            name: templateData.name,
            description: templateData.description,
            steps: [...templateData.steps]
          });
        } else if (isInstance) {
          const instanceData = await getWorkflowInstance(parseInt(id || '0'));
          setData(instanceData);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        
        if (isTemplate) {
          const mockTemplate: WorkflowTemplate = {
            id: id || 'legal-approval-standard',
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
          };
          
          setData(mockTemplate);
          setFormData({
            name: mockTemplate.name,
            description: mockTemplate.description,
            steps: [...mockTemplate.steps]
          });
        } else if (isInstance) {
          const mockInstance: WorkflowInstance = {
            id: parseInt(id || '1'),
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
          };
          
          setData(mockInstance);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, type, isTemplate, isInstance]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleNewStepChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewStep(prev => ({ ...prev, [name]: value }));
  };

  const addStep = () => {
    if (!newStep.role || !newStep.approver_email) return;
    
    const step_id = newStep.role.toLowerCase().replace(/\s+/g, '-');
    const newStepComplete: WorkflowStep = {
      step_id,
      role: newStep.role,
      approver_email: newStep.approver_email,
      is_approved: false
    };
    
    setFormData(prev => ({
      ...prev,
      steps: [...(prev.steps || []), newStepComplete]
    }));
    
    setNewStep({
      role: '',
      approver_email: '',
      is_approved: false
    });
  };

  const removeStep = (index: number) => {
    setFormData(prev => ({
      ...prev,
      steps: prev.steps?.filter((_, i) => i !== index)
    }));
  };

  const moveStepDown = (index: number) => {
    if (!formData.steps || index >= formData.steps.length - 1) return;
    
    const newSteps = [...formData.steps];
    const temp = newSteps[index];
    newSteps[index] = newSteps[index + 1];
    newSteps[index + 1] = temp;
    
    setFormData(prev => ({
      ...prev,
      steps: newSteps
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      if (isTemplate && data) {
        await updateWorkflowTemplate(data.id, formData);
        setData(prev => {
          if (prev && 'steps' in prev) {
            return {
              ...prev,
              ...formData,
              updated_at: new Date().toISOString()
            };
          }
          return prev;
        });
      }
    } catch (error) {
      console.error('Error saving workflow:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this workflow?')) return;
    
    try {
      setSaving(true);
      
      if (isTemplate && data) {
        await deleteWorkflowTemplate(data.id);
        navigate('/legal/workflows');
      }
    } catch (error) {
      console.error('Error deleting workflow:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleApproveStep = async (stepId: string, approve: boolean) => {
    if (!isInstance || !data) return;
    
    try {
      setSaving(true);
      
      await updateWorkflowStep(data.id, stepId, {
        is_approved: approve,
        comments: approvalComment
      });
      
      setData(prev => {
        if (prev && 'steps' in prev) {
          const updatedSteps = prev.steps.map(step => {
            if (step.step_id === stepId) {
              return {
                ...step,
                is_approved: approve,
                comments: approvalComment,
                approved_at: approve ? new Date().toISOString() : undefined
              };
            }
            return step;
          });
          
          let currentStepIndex = updatedSteps.findIndex(step => step.step_id === stepId);
          let nextStepId = stepId;
          let status = prev.status;
          
          if (approve) {
            if (currentStepIndex < updatedSteps.length - 1) {
              nextStepId = updatedSteps[currentStepIndex + 1].step_id;
            } else {
              status = 'approved';
            }
          } else {
            status = 'rejected';
          }
          
          return {
            ...prev,
            steps: updatedSteps,
            current_step_id: nextStepId,
            status,
            updated_at: new Date().toISOString()
          };
        }
        return prev;
      });
      
      setApprovalComment('');
    } catch (error) {
      console.error('Error updating step:', error);
    } finally {
      setSaving(false);
    }
  };

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
          onClick={() => navigate('/legal/workflows')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Workflows
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {isTemplate ? (data as WorkflowTemplate)?.name : `Approval Workflow #${(data as WorkflowInstance)?.id}`}
          </h1>
          {data && (
            <div className="flex items-center gap-4 text-gray-500">
              {isTemplate ? (
                <>
                  <span>Template ID: {(data as WorkflowTemplate).id}</span>
                  <span>•</span>
                  <span>Created: {format(parseISO(data.created_at), 'MMM d, yyyy')}</span>
                </>
              ) : (
                <>
                  <span>Contract: #{(data as WorkflowInstance).contract_id}</span>
                  <span>•</span>
                  <span>Template: {(data as WorkflowInstance).template_id}</span>
                  <span>•</span>
                  <span>Status: {getStatusBadge((data as WorkflowInstance).status)}</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {isInstance && data && (
        <div className="mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col gap-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Approval Progress</h3>
                  <div>
                    {getStatusBadge((data as WorkflowInstance).status)}
                  </div>
                </div>
                
                <div className="space-y-6">
                  {(data as WorkflowInstance).steps.map((step, index) => {
                    const isCurrentStep = step.step_id === (data as WorkflowInstance).current_step_id;
                    const isPastStep = (data as WorkflowInstance).steps.findIndex(s => s.step_id === (data as WorkflowInstance).current_step_id) > index;
                    
                    return (
                      <div 
                        key={step.step_id}
                        className={`p-4 border rounded-lg ${isCurrentStep ? 'border-primary bg-primary/5' : 'border-border'}`}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex items-start gap-3">
                            <div className="mt-1">
                              {step.is_approved ? (
                                <CheckCircle2 className="h-5 w-5 text-green-500" />
                              ) : isPastStep ? (
                                <XCircle className="h-5 w-5 text-red-500" />
                              ) : isCurrentStep ? (
                                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                              ) : (
                                <Clock className="h-5 w-5 text-gray-300" />
                              )}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <h4 className="font-medium">{step.role}</h4>
                                {isCurrentStep && (
                                  <Badge variant="outline" className="bg-yellow-50">Current Step</Badge>
                                )}
                              </div>
                              <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                                <Mail className="h-4 w-4" />
                                <span>{step.approver_email}</span>
                              </div>
                              {step.approved_at && (
                                <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                                  <Clock className="h-4 w-4" />
                                  <span>{format(parseISO(step.approved_at), 'MMM d, yyyy h:mm a')}</span>
                                </div>
                              )}
                              {step.comments && (
                                <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                                  "{step.comments}"
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {isCurrentStep && (
                            <div className="flex gap-2">
                              <Button 
                                variant="outline" 
                                size="sm"
                                className="text-red-600 border-red-200 hover:bg-red-50"
                                onClick={() => handleApproveStep(step.step_id, false)}
                                disabled={saving}
                              >
                                <XCircle className="h-4 w-4 mr-1" />
                                Reject
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm"
                                className="text-green-600 border-green-200 hover:bg-green-50"
                                onClick={() => handleApproveStep(step.step_id, true)}
                                disabled={saving}
                              >
                                <CheckCircle2 className="h-4 w-4 mr-1" />
                                Approve
                              </Button>
                            </div>
                          )}
                        </div>
                        
                        {isCurrentStep && (
                          <div className="mt-4">
                            <Label htmlFor="comment">Comment</Label>
                            <Textarea 
                              id="comment"
                              placeholder="Add your comments about this approval step"
                              className="mt-1"
                              value={approvalComment}
                              onChange={(e) => setApprovalComment(e.target.value)}
                            />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {isTemplate && (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="details">
              Template Details
            </TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <Card>
              <CardHeader>
                <CardTitle>Workflow Template Configuration</CardTitle>
                <CardDescription>
                  Configure the approval steps for this workflow template
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">Template Name</Label>
                        <Input 
                          id="name" 
                          name="name" 
                          value={formData.name || ''} 
                          onChange={handleInputChange} 
                          placeholder="Enter template name"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea 
                          id="description" 
                          name="description" 
                          value={formData.description || ''} 
                          onChange={handleInputChange} 
                          placeholder="Enter template description"
                          rows={3}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <Separator />
                  
                  <div>
                    <h3 className="text-lg font-medium mb-4">Approval Steps</h3>
                    
                    <div className="space-y-4">
                      {formData.steps?.map((step, index) => (
                        <div key={index} className="flex items-start gap-4 p-4 border rounded-lg">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge variant="outline">{index + 1}</Badge>
                              <h4 className="font-medium">{step.role}</h4>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-gray-500">
                              <Mail className="h-4 w-4" />
                              <span>{step.approver_email}</span>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            {index < (formData.steps?.length || 0) - 1 && (
                              <Button 
                                variant="ghost" 
                                size="icon"
                                onClick={() => moveStepDown(index)}
                              >
                                <ArrowDown className="h-4 w-4" />
                              </Button>
                            )}
                            <Button 
                              variant="ghost" 
                              size="icon"
                              onClick={() => removeStep(index)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                      
                      <div className="p-4 border border-dashed rounded-lg">
                        <h4 className="font-medium mb-3">Add New Step</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <div>
                            <Label htmlFor="role">Role</Label>
                            <Input 
                              id="role" 
                              name="role" 
                              value={newStep.role} 
                              onChange={handleNewStepChange} 
                              placeholder="e.g. Legal Counsel"
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="approver_email">Approver Email</Label>
                            <Input 
                              id="approver_email" 
                              name="approver_email" 
                              type="email"
                              value={newStep.approver_email} 
                              onChange={handleNewStepChange} 
                              placeholder="e.g. legal@example.com"
                              className="mt-1"
                            />
                          </div>
                        </div>
                        <Button 
                          onClick={addStep}
                          disabled={!newStep.role || !newStep.approver_email}
                          className="w-full"
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          Add Step
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button 
                  variant="destructive" 
                  onClick={handleDelete}
                  disabled={saving}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Template
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
                      Save Template
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

export default WorkflowDetail;
