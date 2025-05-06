import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getDashboardStats } from '../lib/api';
import { DashboardStats } from '../types';
import PageLayout from '../components/layout/PageLayout';

export default function Dashboard() {
  const { t } = useTranslation();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getDashboardStats();
        setStats(data);
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
        setError('Failed to load dashboard statistics');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">{t('common.messages.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {error}
      </div>
    );
  }

  return (
    <PageLayout title="Dashboard">
      <div className="mb-8">
        <p className="text-gray-600">
          {t('dashboard.welcomeMessage')}
        </p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-700">Active Contracts</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.total_active_contracts}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-700">Expiring Soon</h3>
            <p className="text-3xl font-bold text-yellow-500">{stats.contracts_expiring_soon}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-700">Overdue</h3>
            <p className="text-3xl font-bold text-red-600">{stats.overdue_contracts}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-700">Total Contracts</h3>
            <p className="text-3xl font-bold text-gray-600">{stats.total_contracts}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">{t('dashboard.quickActions')}</h2>
          <div className="space-y-2">
            <Link 
              to="/contracts/upload" 
              className="block w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded text-center"
            >
              {t('dashboard.uploadNewContract')}
            </Link>
            <Link 
              to="/contracts" 
              className="block w-full py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded text-center"
            >
              {t('dashboard.viewAllContracts')}
            </Link>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">{t('dashboard.reminders')}</h2>
          {stats && stats.contracts_expiring_soon > 0 ? (
            <div className="text-yellow-600">
              <p>You have {stats.contracts_expiring_soon} contracts expiring in the next 30 days.</p>
              <Link to="/contracts" className="text-blue-500 hover:underline">
                {t('dashboard.viewExpiringContracts')}
              </Link>
            </div>
          ) : (
            <p className="text-gray-600">{t('dashboard.noContractsExpiringSoon')}</p>
          )}
          
          {stats && stats.overdue_contracts > 0 && (
            <div className="mt-4 text-red-600">
              <p>You have {stats.overdue_contracts} overdue contracts that need attention.</p>
              <Link to="/contracts" className="text-blue-500 hover:underline">
                {t('dashboard.viewOverdueContracts')}
              </Link>
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
