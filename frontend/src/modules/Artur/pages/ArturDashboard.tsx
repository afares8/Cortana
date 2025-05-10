import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, AlertTriangle, CheckCircle } from 'lucide-react';
import TimelineView from '../components/TimelineView';
import SuggestionFeed from '../components/SuggestionFeed';
import InterventionSimulator from '../components/InterventionSimulator';
import IntelligentHeatmap from '../components/IntelligentHeatmap';
import PredictionsPanel from '../components/PredictionsPanel';
import { ArturSuggestion, SuggestionStatus } from '../types';
import { updateSuggestionStatus, executeIntervention } from '../api/arturApi';
import { useDepartmentHealth } from '../hooks/useArturData';

const ArturDashboard: React.FC = () => {
  const [selectedSuggestion, setSelectedSuggestion] = useState<ArturSuggestion | null>(null);
  const [showSimulator, setShowSimulator] = useState<boolean>(false);
  
  const { data: departmentHealth, loading, error } = useDepartmentHealth();
  
  const handleSimulate = (suggestion: ArturSuggestion) => {
    setSelectedSuggestion(suggestion);
    setShowSimulator(true);
  };
  
  const handleApply = async (suggestion: ArturSuggestion) => {
    try {
      await executeIntervention(suggestion.id);
    } catch (err) {
      console.error('Failed to execute intervention:', err);
    }
  };
  
  const handleDismiss = async (suggestion: ArturSuggestion) => {
    try {
      await updateSuggestionStatus(suggestion.id, SuggestionStatus.IGNORED);
    } catch (err) {
      console.error('Failed to dismiss suggestion:', err);
    }
  };
  
  const handleCloseSimulator = () => {
    setShowSimulator(false);
  };
  
  const handleSimulationComplete = () => {
    setShowSimulator(false);
    setSelectedSuggestion(null);
  };



  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <Brain className="h-8 w-8 mr-3 text-blue-600" />
          <h1 className="text-2xl font-bold">Artur Dashboard</h1>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
          >
            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Brain className="h-6 w-6 mr-2 text-blue-600" />
                <h2 className="text-lg font-semibold">System Health</h2>
              </div>
              <div className="text-3xl font-bold text-blue-600">
                {departmentHealth.length > 0
                  ? Math.round(
                      departmentHealth.reduce((acc, dept) => acc + dept.health_score, 0) /
                        departmentHealth.length
                    )
                  : 'N/A'}
                %
              </div>
              <p className="text-gray-600 mt-2">Overall system health score</p>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="flex items-center mb-4">
                <AlertTriangle className="h-6 w-6 mr-2 text-yellow-600" />
                <h2 className="text-lg font-semibold">Active Suggestions</h2>
              </div>
              <div className="text-3xl font-bold text-yellow-600">
                {departmentHealth.reduce((acc, dept) => acc + dept.active_suggestions, 0)}
              </div>
              <p className="text-gray-600 mt-2">Pending improvement suggestions</p>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="flex items-center mb-4">
                <CheckCircle className="h-6 w-6 mr-2 text-green-600" />
                <h2 className="text-lg font-semibold">Recent Interventions</h2>
              </div>
              <div className="text-3xl font-bold text-green-600">
                {departmentHealth.reduce((acc, dept) => acc + dept.recent_interventions, 0)}
              </div>
              <p className="text-gray-600 mt-2">Successful system improvements</p>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
            >
              <TimelineView />
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <SuggestionFeed 
                onSimulate={handleSimulate}
                onApply={handleApply}
                onDismiss={handleDismiss}
              />
            </motion.div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <IntelligentHeatmap />
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <PredictionsPanel />
            </motion.div>
          </div>
          
          {showSimulator && (
            <InterventionSimulator 
              suggestion={selectedSuggestion}
              onClose={handleCloseSimulator}
              onComplete={handleSimulationComplete}
            />
          )}
        </>
      )}
    </div>
  );
};

export default ArturDashboard;
