import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { getCompanies } from '../api/accountingApi';
import { Trash2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

interface UserCompanyAccess {
  id: number;
  user_id: number;
  company_id: number;
  permissions: 'read' | 'write';
  user_email?: string;
  user_name?: string;
  company_name?: string;
}

const UserCompanyAccessPage: React.FC = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<number | null>(null);
  const [selectedPermission, setSelectedPermission] = useState<'read' | 'write'>('read');

  const { data: users = [] } = useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/auth/users`);
      return response.data;
    }
  });

  const { data: companies = [] } = useQuery({
    queryKey: ['companies'],
    queryFn: () => getCompanies()
  });

  const { data: accesses = [], isLoading: isLoadingAccesses } = useQuery<UserCompanyAccess[]>({
    queryKey: ['user-company-accesses'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/accounting/user-company-access`);
      return response.data;
    }
  });

  const createAccessMutation = useMutation({
    mutationFn: async (data: { user_id: number; company_id: number; permissions: string }) => {
      const response = await axios.post(`${API_BASE}/accounting/user-company-access`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-company-accesses'] });
      setSelectedUser(null);
      setSelectedCompany(null);
      setSelectedPermission('read');
    }
  });

  const deleteAccessMutation = useMutation({
    mutationFn: async (accessId: number) => {
      const response = await axios.delete(`${API_BASE}/accounting/user-company-access/${accessId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-company-accesses'] });
    }
  });

  const handleAddAccess = () => {
    if (selectedUser && selectedCompany) {
      createAccessMutation.mutate({
        user_id: selectedUser.id,
        company_id: selectedCompany,
        permissions: selectedPermission
      });
    }
  };

  const handleDeleteAccess = (accessId: number) => {
    if (confirm(t('artur.confirmDeleteAccess', 'Are you sure you want to delete this access?'))) {
      deleteAccessMutation.mutate(accessId);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">{t('accounting.userAccessManagement', 'User Access Management')}</h1>

      {/* Add Access Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">{t('accounting.addCompanyAccess', 'Add Company Access')}</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('common.labels.user', 'User')}</label>
            <select
              className="w-full px-3 py-2 border rounded-md"
              value={selectedUser?.id || ''}
              onChange={(e) => {
                const userId = parseInt(e.target.value);
                const user = users.find(u => u.id === userId) || null;
                setSelectedUser(user);
              }}
            >
              <option value="">{t('accounting.selectUser', 'Select a user...')}</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.full_name} ({user.email})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('common.labels.company', 'Company')}</label>
            <select
              className="w-full px-3 py-2 border rounded-md"
              value={selectedCompany || ''}
              onChange={(e) => setSelectedCompany(parseInt(e.target.value))}
            >
              <option value="">{t('accounting.selectCompany', 'Select a company...')}</option>
              {companies.map(company => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('accounting.permission', 'Permission')}</label>
            <select
              className="w-full px-3 py-2 border rounded-md"
              value={selectedPermission}
              onChange={(e) => setSelectedPermission(e.target.value as 'read' | 'write')}
            >
              <option value="read">{t('accounting.readOnly', 'Read Only')}</option>
              <option value="write">{t('accounting.readWrite', 'Read & Write')}</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              onClick={handleAddAccess}
            >
              {t('accounting.addAccess', 'Add Access')}
            </button>
          </div>
        </div>
      </div>

      {/* Access List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('common.labels.user', 'User')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('common.labels.company', 'Company')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('accounting.permission', 'Permission')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('common.labels.actions', 'Actions')}</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {isLoadingAccesses ? (
              <tr>
                <td colSpan={4} className="px-6 py-4 text-center">{t('common.messages.loading', 'Loading...')}</td>
              </tr>
            ) : accesses.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-4 text-center">{t('accounting.noAccessRecords', 'No access records found')}</td>
              </tr>
            ) : (
              accesses.map(access => (
                <tr key={access.id}>
                  <td className="px-6 py-4 whitespace-nowrap">{access.user_name || `User #${access.user_id}`}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{access.company_name || `Company #${access.company_id}`}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs ${access.permissions === 'write' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
                      {access.permissions === 'write' ? t('accounting.readWrite', 'Read & Write') : t('accounting.readOnly', 'Read Only')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      className="text-red-600 hover:text-red-900 flex items-center"
                      onClick={() => handleDeleteAccess(access.id)}
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      {t('common.labels.delete', 'Delete')}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserCompanyAccessPage;
