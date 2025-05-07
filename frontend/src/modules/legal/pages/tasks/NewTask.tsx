import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
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
import { Popover, PopoverContent, PopoverTrigger } from '../../../../components/ui/popover';
import { Calendar } from '../../../../components/ui/calendar';
import { format } from 'date-fns';
import { AlertCircle, Loader2, Save, ArrowLeft, CalendarIcon } from 'lucide-react';
import { Toast, ToastProvider, ToastViewport, ToastTitle, ToastDescription } from '../../../../components/ui/toast';
import { createTask, getClients } from '../../api/legalApi';
import { Client } from '../../types';
import { useTranslation } from 'react-i18next';
import { cn } from '../../../../lib/utils';

interface TaskCreate {
  title: string;
  description?: string;
  client_id: number;
  assigned_to?: number;
  priority: string;
  status: string;
  due_date?: string;
}

const NewTask: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [clientId, setClientId] = useState<string>('');
  const [assignedTo, setAssignedTo] = useState<string>('');
  const [priority, setPriority] = useState<string>('medium');
  const [status, setStatus] = useState<string>('pending');
  const [dueDate, setDueDate] = useState<Date | undefined>(undefined);
  const [isDueDateOpen, setIsDueDateOpen] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const { data: clients = [], isLoading: isLoadingClients } = useQuery({
    queryKey: ['clients'],
    queryFn: getClients
  });
  
  const users = [
    { id: '1', name: 'John Doe' },
    { id: '2', name: 'Jane Smith' },
    { id: '3', name: 'Robert Johnson' }
  ];
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title) {
      setError(t('Please enter a task title'));
      return;
    }
    
    if (!clientId) {
      setError(t('Please select a client'));
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const taskData: TaskCreate = {
        title,
        description,
        client_id: parseInt(clientId),
        assigned_to: assignedTo ? parseInt(assignedTo) : undefined,
        priority,
        status,
        due_date: dueDate?.toISOString()
      };
      
      const response = await createTask(taskData);
      
      setSuccess(true);
      setTimeout(() => {
        navigate(`/legal/tasks/${response.id}`);
      }, 1500);
    } catch (err) {
      console.error('Error creating task:', err);
      setError(t('Failed to create task. Please try again later.'));
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
            onClick={() => navigate('/legal/tasks')}
            className="mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('Back')}
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{t('New Task')}</h1>
            <p className="text-gray-500">{t('Create a new task')}</p>
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
              <CardTitle>{t('Task Information')}</CardTitle>
              <CardDescription>{t('Enter the task details below')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="title">{t('Title')}</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder={t('Enter task title')}
                  disabled={loading}
                />
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="description">{t('Description')}</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder={t('Enter task description')}
                  disabled={loading}
                />
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="client">{t('Client')}</Label>
                <Select value={clientId} onValueChange={setClientId} disabled={loading || isLoadingClients}>
                  <SelectTrigger id="client">
                    <SelectValue placeholder={t('Select a client')} />
                  </SelectTrigger>
                  <SelectContent>
                    {isLoadingClients ? (
                      <div className="flex justify-center py-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    ) : (
                      clients.map((client: Client) => (
                        <SelectItem key={client.id} value={client.id.toString()}>
                          {client.name}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="assigned-to">{t('Assigned To')}</Label>
                <Select value={assignedTo} onValueChange={setAssignedTo} disabled={loading}>
                  <SelectTrigger id="assigned-to">
                    <SelectValue placeholder={t('Select a user')} />
                  </SelectTrigger>
                  <SelectContent>
                    {users.map(user => (
                      <SelectItem key={user.id} value={user.id}>
                        {user.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="priority">{t('Priority')}</Label>
                  <Select value={priority} onValueChange={setPriority} disabled={loading}>
                    <SelectTrigger id="priority">
                      <SelectValue placeholder={t('Select priority')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">{t('Low')}</SelectItem>
                      <SelectItem value="medium">{t('Medium')}</SelectItem>
                      <SelectItem value="high">{t('High')}</SelectItem>
                      <SelectItem value="urgent">{t('Urgent')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="status">{t('Status')}</Label>
                  <Select value={status} onValueChange={setStatus} disabled={loading}>
                    <SelectTrigger id="status">
                      <SelectValue placeholder={t('Select status')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">{t('Pending')}</SelectItem>
                      <SelectItem value="in_progress">{t('In Progress')}</SelectItem>
                      <SelectItem value="completed">{t('Completed')}</SelectItem>
                      <SelectItem value="cancelled">{t('Cancelled')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="due-date">{t('Due Date')}</Label>
                <Popover open={isDueDateOpen} onOpenChange={setIsDueDateOpen}>
                  <PopoverTrigger asChild>
                    <Button
                      id="due-date"
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !dueDate && "text-muted-foreground"
                      )}
                      disabled={loading}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {dueDate ? format(dueDate, "PPP") : t('Select due date')}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={dueDate}
                      onSelect={(date) => {
                        setDueDate(date);
                        setIsDueDateOpen(false);
                      }}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
              
              <div className="flex justify-end gap-2 mt-6">
                <Button 
                  variant="outline" 
                  onClick={() => navigate('/legal/tasks')}
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
                      {t('Create Task')}
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
              {t('Task created successfully')}
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default NewTask;
