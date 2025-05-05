import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  getObligations, 
  getCompanies, 
  getTaxTypes, 
  getAlerts,
  getObligationsExportUrl,
  getTemplateUrl
} from '../api/accountingApi';
import ObligationTable from '../components/ObligationTable';
import AIAnalysisPanel from '../components/AIAnalysisPanel';
import AlertBanner from '../components/AlertBanner';
import { PlusCircle, BarChart3, Calendar, DollarSign, Download } from 'lucide-react';

const AccountingDashboard: React.FC = () => {
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
        <h1 className="text-2xl font-bold">Accounting Dashboard</h1>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
          onClick={() => setShowAddModal(true)}
        >
          <PlusCircle className="h-5 w-5" />
          <span>Add Obligation</span>
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
              <p className="text-sm text-gray-500">Pending</p>
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
              <p className="text-sm text-gray-500">Overdue</p>
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
              <p className="text-sm text-gray-500">Completed</p>
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
              <p className="text-sm text-gray-500">Upcoming (30 days)</p>
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
        <h2 className="text-xl font-bold mb-4">Export & Reports</h2>
        
        <div className="flex flex-wrap gap-4">
          <div>
            <h3 className="text-md font-semibold mb-2">Export Current View</h3>
            <a
              href={getObligationsExportUrl({
                company_id: undefined,
                format: 'excel'
              })}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center gap-2"
              download
            >
              <Download className="h-5 w-5" />
              <span>Download Excel</span>
            </a>
          </div>
          
          <div>
            <h3 className="text-md font-semibold mb-2">Download Templates</h3>
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
                <option value="" disabled>Select a template...</option>
                <option value="itbms_report">ITBMS Report</option>
                <option value="css_planilla">CSS Planilla</option>
                <option value="municipal_declaration">Municipal Declaration</option>
                <option value="dgi_income_tax">DGI Income Tax</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* AI Analysis Panel */}
      <AIAnalysisPanel companies={companies} />

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
