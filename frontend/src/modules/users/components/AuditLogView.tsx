import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { Badge } from "../../../components/ui/badge";
import { format } from "date-fns";
import { AuditRecord } from '../types';
import { useTranslation } from 'react-i18next';

interface AuditLogViewProps {
  auditLogs: AuditRecord[];
  title?: string;
  maxItems?: number;
}

const AuditLogView: React.FC<AuditLogViewProps> = ({ 
  auditLogs, 
  title = 'Audit Trail', 
  maxItems 
}) => {
  const { t } = useTranslation();
  const displayLogs = maxItems ? auditLogs.slice(0, maxItems) : auditLogs;
  
  const getActionColor = (action: string): string => {
    switch (action.toLowerCase()) {
      case 'create':
        return 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100';
      case 'update':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100';
      case 'delete':
        return 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100';
      case 'login':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-100';
      case 'logout':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100';
    }
  };
  
  const getEntityColor = (entityType: string): string => {
    switch (entityType.toLowerCase()) {
      case 'user':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100';
      case 'role':
        return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-800 dark:text-indigo-100';
      case 'permission':
        return 'bg-pink-100 text-pink-800 dark:bg-pink-800 dark:text-pink-100';
      case 'client':
        return 'bg-cyan-100 text-cyan-800 dark:bg-cyan-800 dark:text-cyan-100';
      case 'contract':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-800 dark:text-amber-100';
      case 'workflow':
        return 'bg-lime-100 text-lime-800 dark:bg-lime-800 dark:text-lime-100';
      case 'task':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-100';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100';
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t(title)}</CardTitle>
      </CardHeader>
      <CardContent>
        {displayLogs.length === 0 ? (
          <p className="text-center text-muted-foreground py-4">{t('No audit logs available')}</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('Timestamp')}</TableHead>
                <TableHead>{t('User')}</TableHead>
                <TableHead>{t('Action')}</TableHead>
                <TableHead>{t('Entity')}</TableHead>
                <TableHead>{t('Details')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {displayLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="whitespace-nowrap">
                    {format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm')}
                  </TableCell>
                  <TableCell>{log.user_name}</TableCell>
                  <TableCell>
                    <Badge className={getActionColor(log.action)}>
                      {t(log.action.charAt(0).toUpperCase() + log.action.slice(1))}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getEntityColor(log.entity_type)}>
                      {t(log.entity_type.charAt(0).toUpperCase() + log.entity_type.slice(1))}
                    </Badge>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">{log.details}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
};

export default AuditLogView;
