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
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Separator } from '../../../components/ui/separator';
import { Badge } from '../../../components/ui/badge';
import { getTask, updateTask, deleteTask } from '../api/legalApi';
import { Task, TaskUpdate } from '../types';
import { format, parseISO } from 'date-fns';
import { Loader2, ArrowLeft, Save, Trash2, FileText, MessageSquare, Clock, Calendar } from 'lucide-react';

const TaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [formData, setFormData] = useState<TaskUpdate>({});
  const [activeTab, setActiveTab] = useState<string>('details');

  useEffect(() => {
    const fetchTask = async () => {
      if (!id || id === 'new') return;
      
      try {
        setLoading(true);
        const data = await getTask(parseInt(id));
        setTask(data);
        setFormData({
          title: data.title,
          description: data.description,
          status: data.status,
          priority: data.priority,
          assigned_to: data.assigned_to,
          due_date: data.due_date,
          related_contract_id: data.related_contract_id,
          related_client_id: data.related_client_id
        });
      } catch (error) {
        console.error('Error fetching task:', error);
        const mockTask: Task = {
          id: parseInt(id),
          title: 'Review Manufacturing Agreement',
          description: 'Review and provide feedback on the manufacturing agreement with Acme Corporation',
          status: 'pending',
          priority: 'high',
          assigned_to: 'Jane Smith',
          due_date: '2023-08-15T00:00:00Z',
          related_contract_id: 1,
          related_client_id: 1,
          created_at: '2023-07-10T14:30:00Z',
          updated_at: '2023-07-10T14:30:00Z',
          ai_generated: false
        };
        setTask(mockTask);
        setFormData({
          title: mockTask.title,
          description: mockTask.description,
          status: mockTask.status,
          priority: mockTask.priority,
          assigned_to: mockTask.assigned_to,
          due_date: mockTask.due_date,
          related_contract_id: mockTask.related_contract_id,
          related_client_id: mockTask.related_client_id
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [id]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      if (id === 'new') {
        console.log('Creating new task:', formData);
        navigate('/legal/tasks');
      } else {
        console.log('Updating task:', formData);
        await updateTask(parseInt(id || '0'), formData);
        if (task) {
          setTask({
            ...task,
            ...formData,
            updated_at: new Date().toISOString()
          });
        }
      }
    } catch (error) {
      console.error('Error saving task:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    
    try {
      setSaving(true);
      await deleteTask(parseInt(id || '0'));
      navigate('/legal/tasks');
    } catch (error) {
      console.error('Error deleting task:', error);
    } finally {
      setSaving(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Pending</Badge>;
      case 'in_progress':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">In Progress</Badge>;
      case 'completed':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Completed</Badge>;
      case 'cancelled':
        return <Badge variant="outline" className="bg-gray-100 text-gray-800 hover:bg-gray-100">Cancelled</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">Urgent</Badge>;
      case 'high':
        return <Badge className="bg-orange-100 text-orange-800 hover:bg-orange-100">High</Badge>;
      case 'medium':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">Medium</Badge>;
      case 'low':
        return <Badge variant="outline" className="bg-gray-100 text-gray-800 hover:bg-gray-100">Low</Badge>;
      default:
        return <Badge variant="outline">{priority}</Badge>;
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
          onClick={() => navigate('/legal/tasks')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Tasks
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {id === 'new' ? 'New Task' : task?.title}
          </h1>
          {task && (
            <p className="text-gray-500">
              Task ID: {task.id} • Created: {new Date(task.created_at).toLocaleDateString()}
            </p>
          )}
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="details">
            <FileText className="h-4 w-4 mr-2" />
            Task Details
          </TabsTrigger>
          <TabsTrigger value="comments">
            <MessageSquare className="h-4 w-4 mr-2" />
            Comments
          </TabsTrigger>
          <TabsTrigger value="history">
            <Clock className="h-4 w-4 mr-2" />
            History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <Card>
            <CardHeader>
              <CardTitle>{id === 'new' ? 'Create New Task' : 'Edit Task Details'}</CardTitle>
              <CardDescription>
                {id === 'new' 
                  ? 'Add a new task to your workflow' 
                  : 'Update the information for this task'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Task Title</Label>
                    <Input 
                      id="title" 
                      name="title" 
                      value={formData.title || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter task title"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea 
                      id="description" 
                      name="description" 
                      value={formData.description || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter task description"
                      rows={4}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="assigned_to">Assigned To</Label>
                    <Input 
                      id="assigned_to" 
                      name="assigned_to" 
                      value={formData.assigned_to || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter assignee name"
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select
                      value={formData.status || ''}
                      onValueChange={(value) => handleSelectChange('status', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="priority">Priority</Label>
                    <Select
                      value={formData.priority || ''}
                      onValueChange={(value) => handleSelectChange('priority', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="urgent">Urgent</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="due_date">Due Date</Label>
                    <div className="relative">
                      <Calendar className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                      <Input 
                        id="due_date" 
                        name="due_date" 
                        type="date"
                        className="pl-8"
                        value={formData.due_date ? format(parseISO(formData.due_date), 'yyyy-MM-dd') : ''} 
                        onChange={(e) => {
                          const date = e.target.value;
                          if (date) {
                            setFormData(prev => ({ 
                              ...prev, 
                              due_date: `${date}T00:00:00Z` 
                            }));
                          } else {
                            setFormData(prev => ({ 
                              ...prev, 
                              due_date: undefined 
                            }));
                          }
                        }} 
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="related_contract_id">Related Contract ID</Label>
                    <Input 
                      id="related_contract_id" 
                      name="related_contract_id" 
                      type="number"
                      value={formData.related_contract_id || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter related contract ID"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="related_client_id">Related Client ID</Label>
                    <Input 
                      id="related_client_id" 
                      name="related_client_id" 
                      type="number"
                      value={formData.related_client_id || ''} 
                      onChange={handleInputChange} 
                      placeholder="Enter related client ID"
                    />
                  </div>
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
                Delete Task
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
                    {id === 'new' ? 'Create Task' : 'Save Changes'}
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="comments">
          <Card>
            <CardHeader>
              <CardTitle>Comments</CardTitle>
              <CardDescription>
                Discussion and notes related to this task
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {id === 'new' ? (
                  <div className="text-center py-8 text-gray-500">
                    Save the task first to add comments
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="text-center py-8 text-gray-500">
                      No comments yet. Be the first to add a comment.
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-2">
                      <Label htmlFor="new-comment">Add Comment</Label>
                      <Textarea 
                        id="new-comment" 
                        placeholder="Type your comment here..."
                        rows={3}
                      />
                      <Button className="mt-2">
                        Post Comment
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Task History</CardTitle>
              <CardDescription>
                Timeline of changes and updates to this task
              </CardDescription>
            </CardHeader>
            <CardContent>
              {id === 'new' ? (
                <div className="text-center py-8 text-gray-500">
                  Save the task first to view history
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="relative pl-6 border-l-2 border-gray-200">
                    <div className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full bg-primary"></div>
                    <div className="mb-4">
                      <p className="text-sm text-gray-500">
                        {task?.updated_at && task.updated_at !== task.created_at 
                          ? format(parseISO(task.updated_at), 'MMM d, yyyy h:mm a')
                          : ''}
                      </p>
                      <p className="font-medium">Task Updated</p>
                      <p className="text-sm text-gray-600">Status changed to {task?.status}</p>
                    </div>
                  </div>
                  
                  <div className="relative pl-6 border-l-2 border-gray-200">
                    <div className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full bg-primary"></div>
                    <div>
                      <p className="text-sm text-gray-500">
                        {task?.created_at ? format(parseISO(task.created_at), 'MMM d, yyyy h:mm a') : ''}
                      </p>
                      <p className="font-medium">Task Created</p>
                      <p className="text-sm text-gray-600">
                        {task?.ai_generated 
                          ? 'Automatically generated by AI'
                          : 'Manually created by user'}
                      </p>
                    </div>
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

export default TaskDetail;
