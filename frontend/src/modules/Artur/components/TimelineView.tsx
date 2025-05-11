import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, Filter, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import { useInterventionLogs } from '../hooks/useArturData';

interface TimelineViewProps {
  departmentId?: number;
}

const TimelineView: React.FC<TimelineViewProps> = ({ departmentId }) => {
  const [dateRange, setDateRange] = useState<{ from: string; to: string }>({ 
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], 
    to: new Date().toISOString().split('T')[0]
  });
  const [actionType, setActionType] = useState<string>("");
  const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
  
  const { data: interventions, loading, error, refetch } = useInterventionLogs({
    department_id: departmentId,
    from_date: dateRange.from,
    to_date: dateRange.to,
    action_type: actionType || undefined
  }, true); // Auto-refresh enabled
  
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>, field: 'from' | 'to') => {
    setDateRange(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };
  
  const handleActionTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setActionType(e.target.value);
  };
  
  const toggleFilter = () => {
    setIsFilterOpen(!isFilterOpen);
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };
  
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'rolled_back':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white rounded-lg shadow-md p-4 mb-6"
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Intervention Timeline</h2>
        <div className="flex items-center space-x-2">
          <button 
            onClick={refetch}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Refresh"
          >
            <RefreshCw size={18} className="text-gray-600" />
          </button>
          <button 
            onClick={toggleFilter}
            className="flex items-center space-x-1 px-3 py-2 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            <Filter size={16} />
            <span>Filter</span>
            {isFilterOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>
      
      {isFilterOpen && (
        <motion.div 
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="bg-gray-50 p-4 rounded-md mb-4"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
              <div className="relative">
                <input
                  type="date"
                  value={dateRange.from}
                  onChange={(e) => handleDateChange(e, 'from')}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full focus:ring-blue-500 focus:border-blue-500"
                />
                <Calendar size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
              <div className="relative">
                <input
                  type="date"
                  value={dateRange.to}
                  onChange={(e) => handleDateChange(e, 'to')}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full focus:ring-blue-500 focus:border-blue-500"
                />
                <Calendar size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
              <select
                value={actionType}
                onChange={handleActionTypeChange}
                className="pl-4 pr-10 py-2 border border-gray-300 rounded-md w-full focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Types</option>
                <option value="rule_creation">Rule Creation</option>
                <option value="rule_modification">Rule Modification</option>
                <option value="department_optimization">Department Optimization</option>
                <option value="resource_allocation">Resource Allocation</option>
                <option value="ai_profile_adjustment">AI Profile Adjustment</option>
              </select>
            </div>
          </div>
        </motion.div>
      )}
      
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-800 p-4 rounded-md">
          <p>Error loading intervention timeline. Please try again.</p>
        </div>
      ) : interventions.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-md text-center">
          <p className="text-gray-500">No interventions found for the selected filters.</p>
        </div>
      ) : (
        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>
          
          {interventions.map((intervention, index) => (
            <motion.div 
              key={intervention.id}
              initial={{ x: -10, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.05 }}
              className="relative pl-12 pb-8"
            >
              <div className="absolute left-4 top-1 w-4 h-4 rounded-full bg-blue-500 z-10"></div>
              <div className="flex flex-col md:flex-row md:items-start">
                <div className="mb-2 md:mb-0 md:mr-4 flex items-center text-sm text-gray-500">
                  <Clock size={14} className="mr-1" />
                  <span>{formatDate(intervention.created_at)}</span>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm flex-1">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium text-gray-900">
                      {intervention.intervention_type.replace(/_/g, ' ')}
                    </h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(intervention.status)}`}>
                      {intervention.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">
                    {(intervention.state_before as Record<string, string>).description || 'Artur performed an intervention based on system analysis.'}
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                    <div className="bg-gray-50 p-3 rounded-md">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Before</h4>
                      <p className="text-sm text-gray-600">
                        {JSON.stringify(intervention.state_before).length > 100 
                          ? JSON.stringify(intervention.state_before).substring(0, 100) + '...' 
                          : JSON.stringify(intervention.state_before)}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">After</h4>
                      <p className="text-sm text-gray-600">
                        {JSON.stringify(intervention.state_after).length > 100 
                          ? JSON.stringify(intervention.state_after).substring(0, 100) + '...' 
                          : JSON.stringify(intervention.state_after)}
                      </p>
                    </div>
                  </div>
                  
                  {intervention.user_id && (
                    <div className="mt-3 text-xs text-gray-500">
                      Executed by User ID: {intervention.user_id}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default TimelineView;
