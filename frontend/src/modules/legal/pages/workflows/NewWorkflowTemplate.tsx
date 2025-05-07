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
import { Alert } from '../../../../components/ui/alert';
import { AlertCircle, Loader2, Save, ArrowLeft, Plus, Trash2 } from 'lucide-react';
import { Toast, ToastProvider, ToastViewport, ToastTitle, ToastDescription } from '../../../../components/ui/toast';
import { createWorkflowTemplate } from '../../api/legalApi';
import { ApprovalStep } from '../../types';
import { useTranslation } from 'react-i18next';

interface WorkflowTemplateCreate {
  name: string;
  description?: string;
  steps: ApprovalStep[];
}

const NewWorkflowTemplate: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [steps, setSteps] = useState<Partial<ApprovalStep>[]>([
    { step_id: '1', role: '', is_approved: false }
  ]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const addStep = () => {
    setSteps([
      ...steps,
      { step_id: `${steps.length + 1}`, role: '', is_approved: false }
    ]);
  };
  
  const removeStep = (index: number) => {
    if (steps.length > 1) {
      const newSteps = steps.filter((_, i) => i !== index);
      const updatedSteps = newSteps.map((step, i) => ({
        ...step,
        step_id: `${i + 1}`
      }));
      setSteps(updatedSteps);
    }
  };
  
  const updateStep = (index: number, field: keyof ApprovalStep, value: string) => {
    const newSteps = [...steps];
    newSteps[index] = {
      ...newSteps[index],
      [field]: value
    };
    setSteps(newSteps);
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name) {
      setError(t('Please enter a workflow name'));
      return;
    }
    
    if (steps.some(step => !step.role)) {
      setError(t('All steps must have a role assigned'));
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const templateData: WorkflowTemplateCreate = {
        name,
        description,
        steps: steps as ApprovalStep[]
      };
      
      const response = await createWorkflowTemplate(templateData);
      
      setSuccess(true);
      setTimeout(() => {
        navigate(`/legal/workflows/${response.id}`);
      }, 1500);
    } catch (err) {
      console.error('Error creating workflow template:', err);
      setError(t('Failed to create workflow template. Please try again later.'));
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
            onClick={() => navigate('/legal/workflows')}
            className="mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('Back')}
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{t('New Workflow Template')}</h1>
            <p className="text-gray-500">{t('Create a reusable workflow template')}</p>
          </div>
        </div>
        
        {error && (
          <Alert className="mb-6">
            <AlertCircle className="h-4 w-4 mr-2" />
            {error}
          </Alert>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>{t('Template Information')}</CardTitle>
                <CardDescription>{t('Basic details about this workflow template')}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="name">{t('Name')}</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={t('Enter workflow template name')}
                    disabled={loading}
                  />
                </div>
                
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="description">{t('Description')}</Label>
                  <Textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder={t('Enter workflow description')}
                    disabled={loading}
                  />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>{t('Workflow Steps')}</CardTitle>
                <CardDescription>{t('Define the approval steps in this workflow')}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {steps.map((step, index) => (
                  <div key={index} className="border p-4 rounded-md">
                    <div className="flex justify-between items-center mb-4">
                      <h4 className="font-medium">{t('Step')} {index + 1}</h4>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeStep(index)}
                        disabled={steps.length === 1 || loading}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="grid w-full items-center gap-1.5">
                        <Label htmlFor={`step-role-${index}`}>{t('Approver Role')}</Label>
                        <Input
                          id={`step-role-${index}`}
                          value={step.role}
                          onChange={(e) => updateStep(index, 'role', e.target.value)}
                          placeholder={t('Enter approver role (e.g., Legal Director)')}
                          disabled={loading}
                        />
                      </div>
                      
                      <div className="grid w-full items-center gap-1.5">
                        <Label htmlFor={`step-approver-email-${index}`}>{t('Approver Email (Optional)')}</Label>
                        <Input
                          id={`step-approver-email-${index}`}
                          value={step.approver_email || ''}
                          onChange={(e) => updateStep(index, 'approver_email', e.target.value)}
                          placeholder={t('Enter approver email address')}
                          disabled={loading}
                        />
                      </div>
                      
                      <div className="grid w-full items-center gap-1.5">
                        <Label htmlFor={`step-comments-${index}`}>{t('Comments (Optional)')}</Label>
                        <Textarea
                          id={`step-comments-${index}`}
                          value={step.comments || ''}
                          onChange={(e) => updateStep(index, 'comments', e.target.value)}
                          placeholder={t('Enter any comments or instructions for this step')}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                ))}
                
                <Button
                  type="button"
                  variant="outline"
                  onClick={addStep}
                  className="w-full"
                  disabled={loading}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {t('Add Step')}
                </Button>
              </CardContent>
            </Card>
            
            <div className="flex justify-end gap-2 mt-6">
              <Button 
                variant="outline" 
                onClick={() => navigate('/legal/workflows')}
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
                    {t('Create Workflow Template')}
                  </>
                )}
              </Button>
            </div>
          </div>
        </form>
        
        {success && (
          <Toast>
            <ToastTitle>{t('Success')}</ToastTitle>
            <ToastDescription>
              {t('Workflow template created successfully')}
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default NewWorkflowTemplate;
