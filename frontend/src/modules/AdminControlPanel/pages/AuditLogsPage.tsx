import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart3, Filter, Download, RefreshCw } from 'lucide-react';
import { AuditLog } from '../types';
import { getAuditLogs, getAuditSummary } from '../api/adminApi';

const AuditLogsPage: React.FC = () => {
  const { t } = useTranslation();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [summary, setSummary] = useState<{
    total_logs: number;
    success_count: number;
    error_count: number;
    action_type_counts: Record<string, number>;
    target_type_counts: Record<string, number>;
    recent_errors: AuditLog[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    user_id: '',
    action_type: '',
    target_type: '',
    success: '',
    start_date: '',
    end_date: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const filterParams: Record<string, any> = {};
        if (filters.user_id) filterParams.user_id = parseInt(filters.user_id);
        if (filters.action_type) filterParams.action_type = filters.action_type;
        if (filters.target_type) filterParams.target_type = filters.target_type;
        if (filters.success) filterParams.success = filters.success === 'true';
        if (filters.start_date) filterParams.start_date = filters.start_date;
        if (filters.end_date) filterParams.end_date = filters.end_date;
        
        const logsData = await getAuditLogs(filterParams);
        setLogs(logsData);
        
        const summaryData = await getAuditSummary(7); // Last 7 days
        setSummary(summaryData);
        
        setError(null);
      } catch (err) {
        setError('Failed to load audit logs');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleRefresh = () => {
    setFilters({
      user_id: '',
      action_type: '',
      target_type: '',
      success: '',
      start_date: '',
      end_date: ''
    });
  };

  const handleExport = () => {
    try {
      const headers = ['ID', 'User ID', 'Action Type', 'Target Type', 'Target ID', 'Success', 'Error Message', 'Created At'];
      const csvRows = [headers.join(',')];
      
      logs.forEach(log => {
        const row = [
          log.id,
          log.user_id || '',
          log.action_type,
          log.target_type,
          log.target_id || '',
          log.success ? 'Yes' : 'No',
          log.error_message || '',
          log.created_at
        ];
        csvRows.push(row.join(','));
      });
      
      const csvString = csvRows.join('\n');
      const dataBlob = new Blob([csvString], { type: 'text/csv' });
      const url = URL.createObjectURL(dataBlob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export logs');
      console.error(err);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <BarChart3 className="h-8 w-8 mr-3 text-blue-600" />
          <h1 className="text-2xl font-bold">Audit Logs</h1>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="bg-gray-600 text-white px-4 py-2 rounded-md flex items-center"
          >
            <Filter className="h-5 w-5 mr-2" />
            Filters
          </button>
          <button
            onClick={handleRefresh}
            className="bg-gray-600 text-white px-4 py-2 rounded-md flex items-center"
          >
            <RefreshCw className="h-5 w-5 mr-2" />
            Refresh
          </button>
          <button
            onClick={handleExport}
            className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center"
          >
            <Download className="h-5 w-5 mr-2" />
            Export
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {showFilters && (
        <div className="bg-gray-100 p-4 rounded-lg mb-6">
          <h2 className="text-lg font-semibold mb-4">Filter Logs</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">User ID</label>
              <input
                type="text"
                name="user_id"
                value={filters.user_id}
                onChange={handleFilterChange}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="User ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
              <select
                name="action_type"
                value={filters.action_type}
                onChange={handleFilterChange}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="">All Actions</option>
                <option value="function_execution">Function Execution</option>
                <option value="automation_trigger">Automation Trigger</option>
                <option value="ai_prompt">AI Prompt</option>
                <option value="ai_response">AI Response</option>
                <option value="department_change">Department Change</option>
                <option value="role_change">Role Change</option>
                <option value="template_change">Template Change</option>
                <option value="user_login">User Login</option>
                <option value="user_logout">User Logout</option>
                <option value="permission_change">Permission Change</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target Type</label>
              <select
                name="target_type"
                value={filters.target_type}
                onChange={handleFilterChange}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="">All Targets</option>
                <option value="department">Department</option>
                <option value="role">Role</option>
                <option value="function">Function</option>
                <option value="automation_rule">Automation Rule</option>
                <option value="ai_profile">AI Profile</option>
                <option value="template">Template</option>
                <option value="user">User</option>
                <option value="system">System</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                name="success"
                value={filters.success}
                onChange={handleFilterChange}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="">All Status</option>
                <option value="true">Success</option>
                <option value="false">Error</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                name="start_date"
                value={filters.start_date}
                onChange={handleFilterChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                name="end_date"
                value={filters.end_date}
                onChange={handleFilterChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
          </div>
        </div>
      )}

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Overview</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Total Logs</p>
                <p className="text-2xl font-bold">{summary.total_logs}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Success Rate</p>
                <p className="text-2xl font-bold">
                  {summary.total_logs > 0
                    ? `${Math.round((summary.success_count / summary.total_logs) * 100)}%`
                    : '0%'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Successful</p>
                <p className="text-2xl font-bold text-green-600">{summary.success_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Errors</p>
                <p className="text-2xl font-bold text-red-600">{summary.error_count}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Top Actions</h3>
            <div className="space-y-2">
              {Object.entries(summary.action_type_counts)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([action, count]) => (
                  <div key={action} className="flex justify-between items-center">
                    <span className="text-sm">{action}</span>
                    <span className="text-sm font-semibold">{count}</span>
                  </div>
                ))}
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Top Targets</h3>
            <div className="space-y-2">
              {Object.entries(summary.target_type_counts)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([target, count]) => (
                  <div key={target} className="flex justify-between items-center">
                    <span className="text-sm">{target}</span>
                    <span className="text-sm font-semibold">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : logs.length === 0 ? (
        <div className="bg-gray-100 p-8 rounded-lg text-center">
          <BarChart3 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Audit Logs Found</h2>
          <p className="text-gray-600 mb-4">
            No logs match your current filter criteria.
          </p>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Target
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{log.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {log.user_id ? `User ${log.user_id}` : 'System'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{log.action_type}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {log.target_type} {log.target_id ? `#${log.target_id}` : ''}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        log.success
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {log.success ? 'Success' : 'Error'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AuditLogsPage;
