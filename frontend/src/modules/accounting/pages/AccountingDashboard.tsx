import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { 
  getObligations, 
  getCompanies, 
  getTaxTypes, 
  getAlerts,
  getObligationsExportUrl,
  getTemplateUrl,
  getObligationStats
} from '../api/accountingApi';
import ObligationTable from '../components/ObligationTable';
import AIAnalysisPanel from '../components/AIAnalysisPanel';
import AlertBanner from '../components/AlertBanner';
import { PlusCircle, BarChart3, Calendar, DollarSign, Download, PieChart, TrendingUp } from 'lucide-react';

const AccountingDashboard: React.FC = () => {
  const { t } = useTranslation();
  // Will be used in future phases for adding new obligations
  const [showAddModal, setShowAddModal] = useState<boolean>(false);

  const { 
    data: obligations = [], 
    isLoading: isLoadingObligations,
    refetch: refetchObligations
  } = useQuery({
    queryKey: ['obligations'],
    queryFn: () => getObligations()
  });

  const { 
    data: companies = []
  } = useQuery({
    queryKey: ['companies'],
    queryFn: () => getCompanies()
  });

  const { 
    data: taxTypes = []
  } = useQuery({
    queryKey: ['taxTypes'],
    queryFn: () => getTaxTypes()
  });
  
  const {
    data: alerts = { upcoming: [], overdue: [] },
    isLoading: isLoadingAlerts,
    refetch: refetchAlerts
  } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => getAlerts()
  });
  
  const {
    data: stats,
    isLoading: isLoadingStats
  } = useQuery({
    queryKey: ['obligationStats'],
    queryFn: () => getObligationStats()
  });

  const pendingObligations = obligations.filter(o => o.status === 'pending').length;
  const overdueObligations = obligations.filter(o => o.status === 'overdue').length;
  const completedObligations = obligations.filter(o => o.status === 'completed').length;
  
  const today = new Date();
  const thirtyDaysFromNow = new Date();
  thirtyDaysFromNow.setDate(today.getDate() + 30);
  
  useEffect(() => {
    if (companies.length > 0 && taxTypes.length > 0) {
      console.log(`Loaded ${companies.length} companies and ${taxTypes.length} tax types`);
      refetchAlerts();
    }
  }, [companies, taxTypes, refetchAlerts]);
  
  const upcomingObligations = obligations.filter(o => {
    const dueDate = new Date(o.next_due_date);
    return dueDate >= today && dueDate <= thirtyDaysFromNow && o.status !== 'completed';
  });

  const handleMakePayment = (obligationId: number) => {
    console.log(`Make payment for obligation ${obligationId}`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('accounting.dashboard.title')}</h1>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
          onClick={() => setShowAddModal(true)}
        >
          <PlusCircle className="h-5 w-5" />
          <span>{t('accounting.obligations.add')}</span>
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 text-blue-600 mr-4">
              <Calendar className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{t('accounting.obligations.statuses.pending')}</p>
              <p className="text-xl font-semibold">{pendingObligations}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-red-100 text-red-600 mr-4">
              <Calendar className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{t('accounting.obligations.statuses.overdue')}</p>
              <p className="text-xl font-semibold">{overdueObligations}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 text-green-600 mr-4">
              <DollarSign className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{t('accounting.obligations.statuses.paid')}</p>
              <p className="text-xl font-semibold">{completedObligations}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100 text-purple-600 mr-4">
              <BarChart3 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{t('accounting.dashboard.upcomingObligations')} (30 days)</p>
              <p className="text-xl font-semibold">{upcomingObligations.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alert Banner */}
      {!isLoadingAlerts && <AlertBanner upcoming={alerts.upcoming} overdue={alerts.overdue} />}

      {/* Obligations Table */}
      <ObligationTable
        obligations={obligations}
        isLoading={isLoadingObligations}
        onRefresh={refetchObligations}
        onMakePayment={handleMakePayment}
      />

      {/* Export Tool */}
      <div className="mt-8 mb-4">
        <h2 className="text-xl font-bold mb-4">{t('accounting.documents.title')}</h2>
        
        <div className="flex flex-wrap gap-4">
          <div>
            <h3 className="text-md font-semibold mb-2">{t('accounting.documents.download')}</h3>
            <a
              href={getObligationsExportUrl({
                company_id: undefined,
                format: 'excel'
              })}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center gap-2"
              download
            >
              <Download className="h-5 w-5" />
              <span>{t('accounting.documents.download')}</span>
            </a>
          </div>
          
          <div>
            <h3 className="text-md font-semibold mb-2">{t('accounting.documents.template')}</h3>
            <div className="flex flex-col gap-2">
              <select
                className="px-3 py-2 border rounded-md"
                onChange={(e) => {
                  if (e.target.value) {
                    window.open(getTemplateUrl(e.target.value), '_blank');
                  }
                }}
                defaultValue=""
              >
                <option value="" disabled>{t('common.messages.noData')}</option>
                <option value="itbms_report">{t('accounting.documents.templates.itbms')}</option>
                <option value="css_planilla">{t('accounting.documents.templates.css')}</option>
                <option value="municipal_declaration">{t('accounting.documents.templates.municipal')}</option>
                <option value="dgi_income_tax">{t('accounting.documents.templates.isr')}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Visualization */}
      <div className="mt-8 mb-6">
        <h2 className="text-xl font-bold mb-4">{t('accounting.stats.title', 'Obligation Statistics')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Trend Analysis Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <TrendingUp className="h-6 w-6 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold">{t('accounting.stats.trends', 'Payment Trends')}</h3>
            </div>
            {isLoadingStats ? (
              <div className="h-64 flex items-center justify-center bg-gray-50 rounded-md">
                <p className="text-gray-500 text-sm">
                  {t('accounting.stats.loadingData', 'Loading trend data...')}
                </p>
              </div>
            ) : stats ? (
              <div className="h-64 p-4 bg-gray-50 rounded-md overflow-auto">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">{t('accounting.stats.totalObligations', 'Total Obligations')}:</span>
                    <span className="text-sm">{stats.total_obligations}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">{t('accounting.stats.totalPaid', 'Total Paid')}:</span>
                    <span className="text-sm">{stats.total_paid}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">{t('accounting.stats.totalAmount', 'Total Amount')}:</span>
                    <span className="text-sm">${stats.total_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">{t('accounting.stats.paidAmount', 'Paid Amount')}:</span>
                    <span className="text-sm">${stats.paid_amount.toFixed(2)}</span>
                  </div>
                  
                  <h4 className="text-sm font-semibold mt-4">{t('accounting.stats.monthlyTrends', 'Monthly Trends')}</h4>
                  {stats.by_month.map((month, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-xs">{month.month}</span>
                      <div className="flex-1 mx-2">
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500" 
                            style={{ width: `${(month.paid / month.count) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                      <span className="text-xs">{month.paid}/{month.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center bg-gray-50 rounded-md">
                <p className="text-gray-500 text-sm">
                  {t('accounting.stats.noData', 'No data available')}
                </p>
              </div>
            )}
          </div>
          
          {/* Distribution Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <PieChart className="h-6 w-6 text-purple-600 mr-2" />
              <h3 className="text-lg font-semibold">{t('accounting.stats.distribution', 'Obligation Distribution')}</h3>
            </div>
            {isLoadingStats ? (
              <div className="h-64 flex items-center justify-center bg-gray-50 rounded-md">
                <p className="text-gray-500 text-sm">
                  {t('accounting.stats.loadingData', 'Loading distribution data...')}
                </p>
              </div>
            ) : stats ? (
              <div className="h-64 p-4 bg-gray-50 rounded-md overflow-auto">
                <h4 className="text-sm font-semibold mb-2">{t('accounting.stats.byCompany', 'By Company')}</h4>
                <div className="space-y-3">
                  {stats.by_company.map((company, index) => (
                    <div key={index}>
                      <div className="flex justify-between text-xs">
                        <span>{company.company_name}</span>
                        <span>{company.paid}/{company.count}</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden mt-1">
                        <div 
                          className="h-full bg-purple-500" 
                          style={{ width: `${(company.paid / company.count) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center bg-gray-50 rounded-md">
                <p className="text-gray-500 text-sm">
                  {t('accounting.stats.noData', 'No data available')}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Analysis Panel */}
      <AIAnalysisPanel companies={companies} title={t('accounting.ai.title')} />

      {/* Add Obligation Modal */}
      {showAddModal && (
        <div className="hidden">
          {/* Modal content will be implemented in future phases */}
          {/* Using showAddModal here to prevent unused variable warning */}
        </div>
      )}
    </div>
  );
};

export default AccountingDashboard;
