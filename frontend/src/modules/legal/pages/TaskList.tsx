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
import { getTasks } from '../api/legalApi';
import { Task } from '../types';
import { 
  Loader2, 
  Plus, 
  Search, 
  Filter, 
  Calendar, 
  Clock, 
  AlertTriangle,
  User
} from 'lucide-react';
import { format, parseISO, isBefore, addDays } from 'date-fns';

const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [assigneeFilter, setAssigneeFilter] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const data = await getTasks();
        setTasks(data);
      } catch (error) {
        console.error('Error fetching tasks:', error);
        setTasks([
          {
            id: 1,
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
          },
          {
            id: 2,
            title: 'Send NDA Reminder',
            description: 'Send a reminder to TechStart Inc about signing the NDA',
            status: 'completed',
            priority: 'medium',
            assigned_to: 'Michael Johnson',
            due_date: '2023-07-20T00:00:00Z',
            related_contract_id: 2,
            related_client_id: 2,
            created_at: '2023-07-05T09:15:00Z',
            updated_at: '2023-07-18T11:30:00Z',
            ai_generated: false
          },
          {
            id: 3,
            title: 'Prepare Contract Renewal',
            description: 'Prepare renewal documents for the distribution agreement with Global Fragrances',
            status: 'pending',
            priority: 'low',
            assigned_to: 'Sarah Williams',
            due_date: '2023-09-01T00:00:00Z',
            related_contract_id: 3,
            related_client_id: 3,
            created_at: '2023-07-15T16:45:00Z',
            updated_at: '2023-07-15T16:45:00Z',
            ai_generated: false
          },
          {
            id: 4,
            title: 'Urgent: Review Pricing Terms',
            description: 'Review and approve updated pricing terms for Acme Corporation',
            status: 'pending',
            priority: 'urgent',
            assigned_to: 'Jane Smith',

            due_date: '2023-07-25T00:00:00Z',
            related_contract_id: 1,
            related_client_id: 1,
            created_at: '2023-07-20T10:00:00Z',
            updated_at: '2023-07-20T10:00:00Z',
            ai_generated: false
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = 
      task.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
      task.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.assigned_to?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === '' || task.status === statusFilter;
    const matchesPriority = priorityFilter === '' || task.priority === priorityFilter;
    const matchesAssignee = assigneeFilter === '' || task.assigned_to === assigneeFilter;
    
    return matchesSearch && matchesStatus && matchesPriority && matchesAssignee;
  });

  const statuses = Array.from(new Set(tasks.map(task => task.status)));
  const priorities = Array.from(new Set(tasks.map(task => task.priority)));
  const assignees = Array.from(new Set(tasks.map(task => task.assigned_to).filter(Boolean) as string[]));

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Pending</Badge>;
      case 'in_progress':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">In Progress</Badge>;
      case 'completed':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Completed</Badge>;
      case 'cancelled':
        return <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">Cancelled</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">Urgent</Badge>;
      case 'high':
        return <Badge className="bg-orange-100 text-orange-800 hover:bg-orange-100">High</Badge>;
      case 'medium':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Medium</Badge>;
      case 'low':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Low</Badge>;
      default:
        return <Badge variant="secondary">{priority}</Badge>;
    }
  };

  const getDueDateStatus = (dueDate: string, status: string) => {
    if (status === 'completed' || status === 'cancelled') {
      return null;
    }
    
    const now = new Date();
    const due = parseISO(dueDate);
    
    if (isBefore(due, now)) {
      return (
        <div className="flex items-center gap-1 text-red-600">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-xs">Overdue</span>
        </div>
      );
    } else if (isBefore(due, addDays(now, 3))) {
      return (
        <div className="flex items-center gap-1 text-yellow-600">
          <Clock className="h-4 w-4" />
          <span className="text-xs">Due Soon</span>
        </div>
      );
    }
    
    return null;
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Task Management</h1>
          <p className="text-gray-500">Manage and track legal tasks and deadlines</p>
        </div>
        <Button 
          onClick={() => navigate('/legal/tasks/new')}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          Create New Task
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Search and filter tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <Input
                  type="text"
                  placeholder="Search tasks..."
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
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  {statuses.map((status) => (
                    <option key={status} value={status}>
                      {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
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
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                >
                  <option value="">All Priorities</option>
                  {priorities.map((priority) => (
                    <option key={priority} value={priority}>
                      {priority.charAt(0).toUpperCase() + priority.slice(1)}
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
                  value={assigneeFilter}
                  onChange={(e) => setAssigneeFilter(e.target.value)}
                >
                  <option value="">All Assignees</option>
                  {assignees.map((assignee) => (
                    <option key={assignee} value={assignee}>
                      {assignee}
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
                  <TableHead>Task</TableHead>
                  <TableHead>Assignee</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Related To</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTasks.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                      No tasks found. Try adjusting your filters or create a new task.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredTasks.map((task) => (
                    <TableRow key={task.id} className="cursor-pointer hover:bg-gray-50" onClick={() => navigate(`/legal/tasks/${task.id}`)}>
                      <TableCell>
                        <div className="font-medium">{task.title}</div>
                        {task.description && (
                          <div className="text-sm text-gray-500 truncate max-w-xs">
                            {task.description}
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-gray-500" />
                          <span>{task.assigned_to}</span>
                        </div>
                      </TableCell>
                      <TableCell>{getPriorityBadge(task.priority)}</TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4 text-gray-500" />
                            <span>{task.due_date ? format(parseISO(task.due_date), 'MMM d, yyyy') : 'No date set'}</span>
                          </div>
                          {task.due_date ? getDueDateStatus(task.due_date, task.status) : null}
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(task.status)}</TableCell>
                      <TableCell>
                        {task.related_contract_id && (
                          <div className="text-sm">
                            <span className="text-gray-500">Contract:</span> #{task.related_contract_id}
                          </div>
                        )}
                        {task.related_client_id && (
                          <div className="text-sm">
                            <span className="text-gray-500">Client:</span> #{task.related_client_id}
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/legal/tasks/${task.id}`);
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

export default TaskList;
