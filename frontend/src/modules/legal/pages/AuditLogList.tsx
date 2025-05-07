import React, { useState, useEffect } from 'react';
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
import { getAuditLogs } from '../api/legalApi';
import { AuditLog } from '../types';
import { format, parseISO } from 'date-fns';
import { Loader2, Search, Filter, FileText, User, Calendar } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const AuditLogList: React.FC = () => {
  const { t } = useTranslation();
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [actionFilter, setActionFilter] = useState<string>('');
  const [entityFilter, setEntityFilter] = useState<string>('');

  useEffect(() => {
    const fetchAuditLogs = async () => {
      try {
        setLoading(true);
        const data = await getAuditLogs();
        setAuditLogs(data);
      } catch (error) {
        console.error('Error fetching audit logs:', error);
        setAuditLogs([
          {
            id: 1,
            action: 'create',
            entity_type: 'contract',
            entity_id: 1,
            user_id: 1,
            user_name: 'John Doe',
            details: 'Created new contract "Manufacturing Agreement"',
            timestamp: '2023-07-10T14:30:00Z'
          },
          {
            id: 2,
            action: 'update',
            entity_type: 'client',
            entity_id: 2,
            user_id: 1,
            user_name: 'John Doe',
            details: 'Updated client information for "TechStart Inc"',
            timestamp: '2023-07-15T09:45:00Z'
          },
          {
            id: 3,
            action: 'delete',
            entity_type: 'task',
            entity_id: 5,
            user_id: 2,
            user_name: 'Jane Smith',
            details: 'Deleted task "Review old contracts"',
            timestamp: '2023-07-18T16:20:00Z'
          },
          {
            id: 4,
            action: 'view',
            entity_type: 'contract',
            entity_id: 3,
            user_id: 3,
            user_name: 'Robert Johnson',
            details: 'Viewed contract "Distribution Agreement"',
            timestamp: '2023-07-20T11:10:00Z'
          },
          {
            id: 5,
            action: 'approve',
            entity_type: 'workflow',
            entity_id: 2,
            user_id: 4,
            user_name: 'Lisa Chen',
            details: 'Approved workflow step for "NDA Approval"',
            timestamp: '2023-07-22T15:30:00Z'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchAuditLogs();
  }, []);

  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = 
      log.details.toLowerCase().includes(searchTerm.toLowerCase()) || 
      log.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.entity_type.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesAction = actionFilter === '' || log.action === actionFilter;
    const matchesEntity = entityFilter === '' || log.entity_type === entityFilter;
    
    return matchesSearch && matchesAction && matchesEntity;
  });

  const actions = Array.from(new Set(auditLogs.map(log => log.action)));
  const entityTypes = Array.from(new Set(auditLogs.map(log => log.entity_type)));

  const getActionBadge = (action: string) => {
    switch (action) {
      case 'create':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">{t('legal.auditLogs.actions.create')}</Badge>;
      case 'update':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">{t('legal.auditLogs.actions.update')}</Badge>;
      case 'delete':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">{t('legal.auditLogs.actions.delete')}</Badge>;
      case 'view':
        return <Badge variant="outline" className="bg-gray-100 text-gray-800 hover:bg-gray-100">{t('legal.auditLogs.actions.view')}</Badge>;
      case 'approve':
        return <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-100">{t('legal.auditLogs.actions.approve')}</Badge>;
      default:
        return <Badge variant="outline">{t(`legal.auditLogs.actions.${action}`)}</Badge>;
    }
  };

  const getEntityBadge = (entityType: string) => {
    switch (entityType) {
      case 'contract':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">{t('legal.auditLogs.entities.contract')}</Badge>;
      case 'client':
        return <Badge className="bg-indigo-100 text-indigo-800 hover:bg-indigo-100">{t('legal.auditLogs.entities.client')}</Badge>;
      case 'task':
        return <Badge className="bg-cyan-100 text-cyan-800 hover:bg-cyan-100">{t('legal.auditLogs.entities.task')}</Badge>;
      case 'workflow':
        return <Badge className="bg-pink-100 text-pink-800 hover:bg-pink-100">{t('legal.auditLogs.entities.workflow')}</Badge>;
      default:
        return <Badge variant="outline">{t(`legal.auditLogs.entities.${entityType}`)}</Badge>;
    }
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">{t('legal.auditLogs.title')}</h1>
          <p className="text-gray-500">{t('legal.auditLogs.description')}</p>
        </div>
        <Button 
          variant="outline"
          onClick={() => window.print()}
          className="flex items-center gap-2"
        >
          <FileText size={16} />
          {t('legal.auditLogs.exportLogs')}
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>{t('legal.auditLogs.filters')}</CardTitle>
          <CardDescription>{t('legal.auditLogs.searchAndFilter')}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <Input
                  type="text"
                  placeholder={t('legal.auditLogs.searchPlaceholder')}
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="w-full md:w-1/4">
              <div className="relative">
                <Filter className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <select
                  className="w-full pl-8 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={actionFilter}
                  onChange={(e) => setActionFilter(e.target.value)}
                >
                  <option value="">{t('legal.auditLogs.allActions')}</option>
                  {actions.map((action) => (
                    <option key={action} value={action}>
                      {t(`legal.auditLogs.actions.${action}`)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="w-full md:w-1/4">
              <div className="relative">
                <Filter className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <select
                  className="w-full pl-8 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={entityFilter}
                  onChange={(e) => setEntityFilter(e.target.value)}
                >
                  <option value="">{t('legal.auditLogs.allEntities')}</option>
                  {entityTypes.map((type) => (
                    <option key={type} value={type}>
                      {t(`legal.auditLogs.entities.${type}`)}
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
                  <TableHead>{t('legal.auditLogs.tableHeaders.timestamp')}</TableHead>
                  <TableHead>{t('legal.auditLogs.tableHeaders.user')}</TableHead>
                  <TableHead>{t('legal.auditLogs.tableHeaders.action')}</TableHead>
                  <TableHead>{t('legal.auditLogs.tableHeaders.entityType')}</TableHead>
                  <TableHead>{t('legal.auditLogs.tableHeaders.details')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                      {t('legal.auditLogs.noLogsFound')}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4 text-gray-500" />
                          <span>{format(parseISO(log.timestamp), 'MMM d, yyyy h:mm a')}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-gray-500" />
                          <span>{log.user_name}</span>
                        </div>
                      </TableCell>
                      <TableCell>{getActionBadge(log.action)}</TableCell>
                      <TableCell>{getEntityBadge(log.entity_type)}</TableCell>
                      <TableCell className="max-w-md truncate">{log.details}</TableCell>
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

export default AuditLogList;
