import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  PlayCircle, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  X,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { ArturSuggestion } from '../types';
import { useSimulateIntervention, useExecuteIntervention } from '../hooks/useArturData';

interface InterventionSimulatorProps {
  suggestion: ArturSuggestion | null;
  onClose: () => void;
  onComplete: () => void;
}

const InterventionSimulator: React.FC<InterventionSimulatorProps> = ({ 
  suggestion, 
  onClose, 
  onComplete 
}) => {
  const [step, setStep] = useState<'initial' | 'simulating' | 'results' | 'executing'>('initial');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    parameters: true,
    before: false,
    after: false,
    dependencies: false
  });
  
  const { result, loading: simulationLoading, error: simulationError, runSimulation } = useSimulateIntervention();
  const { success, loading: executionLoading, error: executionError, execute } = useExecuteIntervention();
  
  useEffect(() => {
    if (success) {
      onComplete();
    }
  }, [success, onComplete]);
  
  const handleRunSimulation = async () => {
    if (!suggestion) return;
    
    setStep('simulating');
    
    const simulationType = suggestion.source === 'function_usage' 
      ? 'optimize_function' 
      : suggestion.source === 'rule_overlap' 
        ? 'merge_rules' 
        : 'default';
    
    await runSimulation({
      suggestion_id: suggestion.id,
      simulation_type: simulationType,
      parameters: {
        run_full_analysis: true,
        include_dependencies: true
      }
    });
    
    setStep('results');
  };
  
  const handleExecute = async () => {
    if (!result) return;
    
    setStep('executing');
    const success = await execute(result.id);
    
    if (success) {
      onComplete();
    }
  };
  
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  const getResultBadge = () => {
    if (!result) return null;
    
    switch (result.result_type) {
      case 'recommended':
        return (
          <span className="flex items-center text-sm font-medium px-3 py-1 rounded-full bg-green-100 text-green-800">
            <CheckCircle size={16} className="mr-1.5" />
            Recommended
          </span>
        );
      case 'neutral':
        return (
          <span className="flex items-center text-sm font-medium px-3 py-1 rounded-full bg-blue-100 text-blue-800">
            <AlertTriangle size={16} className="mr-1.5" />
            Neutral
          </span>
        );
      case 'not_recommended':
        return (
          <span className="flex items-center text-sm font-medium px-3 py-1 rounded-full bg-red-100 text-red-800">
            <XCircle size={16} className="mr-1.5" />
            Not Recommended
          </span>
        );
      default:
        return null;
    }
  };
  
  const getImpactBadge = (level: string) => {
    switch (level) {
      case 'high':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-800">High</span>;
      case 'medium':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-yellow-100 text-yellow-800">Medium</span>;
      case 'low':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-800">Low</span>;
      default:
        return <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-800">Unknown</span>;
    }
  };
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
        >
          <div className="flex justify-between items-center border-b border-gray-200 px-6 py-4">
            <h2 className="text-xl font-semibold text-gray-800">
              {step === 'initial' && 'Intervention Simulator'}
              {step === 'simulating' && 'Running Simulation...'}
              {step === 'results' && 'Simulation Results'}
              {step === 'executing' && 'Executing Intervention...'}
            </h2>
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              disabled={simulationLoading || executionLoading}
            >
              <X size={20} className="text-gray-500" />
            </button>
          </div>
          
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            {step === 'initial' && suggestion && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium text-blue-800 mb-2">Suggestion Details</h3>
                  <p className="text-blue-700 mb-3">{suggestion.issue_summary}</p>
                  <div className="flex items-center text-sm text-blue-600">
                    <span className="mr-2">Confidence:</span>
                    <div className="bg-blue-200 h-2 w-24 rounded-full overflow-hidden">
                      <div 
                        className="bg-blue-600 h-full rounded-full" 
                        style={{ width: `${suggestion.confidence_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="ml-2">{Math.round(suggestion.confidence_score * 100)}%</span>
                  </div>
                </div>
                
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium text-gray-800 mb-2">Simulation Parameters</h3>
                  <p className="text-gray-600 mb-4">
                    The simulation will run in a sandbox environment to predict the outcome of this intervention.
                    No actual changes will be made to the system until you confirm.
                  </p>
                  
                  <div className="flex justify-center mt-6">
                    <button
                      onClick={handleRunSimulation}
                      className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      <PlayCircle size={18} className="mr-2" />
                      Run Simulation
                    </button>
                  </div>
                </div>
              </div>
            )}
            
            {step === 'simulating' && (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
                <p className="text-gray-600">Running simulation in sandbox environment...</p>
                <p className="text-gray-500 text-sm mt-2">This may take a few moments</p>
              </div>
            )}
            
            {step === 'results' && simulationError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <XCircle size={48} className="mx-auto text-red-500 mb-4" />
                <h3 className="text-lg font-medium text-red-800 mb-2">Simulation Failed</h3>
                <p className="text-red-700 mb-6">
                  {simulationError || 'An error occurred while running the simulation. Please try again.'}
                </p>
                <button
                  onClick={() => setStep('initial')}
                  className="px-4 py-2 bg-red-100 text-red-800 rounded-md hover:bg-red-200 transition-colors"
                >
                  Back to Simulator
                </button>
              </div>
            )}
            
            {step === 'results' && result && !simulationError && (
              <div className="space-y-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-1">Simulation Complete</h3>
                    <p className="text-gray-600">
                      The simulation has completed. Review the results before proceeding.
                    </p>
                  </div>
                  {getResultBadge()}
                </div>
                
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection('parameters')}
                    className="w-full flex justify-between items-center px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <span className="font-medium">Simulation Parameters</span>
                    {expandedSections.parameters ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </button>
                  
                  {expandedSections.parameters && (
                    <div className="p-4 border-t border-gray-200">
                      <pre className="bg-gray-50 p-3 rounded text-sm overflow-x-auto">
                        {JSON.stringify(result.parameters, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
                
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection('before')}
                    className="w-full flex justify-between items-center px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <span className="font-medium">Before State</span>
                    {expandedSections.before ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </button>
                  
                  {expandedSections.before && (
                    <div className="p-4 border-t border-gray-200">
                      <pre className="bg-gray-50 p-3 rounded text-sm overflow-x-auto">
                        {JSON.stringify(result.before_state, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
                
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection('after')}
                    className="w-full flex justify-between items-center px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <span className="font-medium">After State</span>
                    {expandedSections.after ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </button>
                  
                  {expandedSections.after && (
                    <div className="p-4 border-t border-gray-200">
                      <pre className="bg-gray-50 p-3 rounded text-sm overflow-x-auto">
                        {JSON.stringify(result.after_state, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
                
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection('dependencies')}
                    className="w-full flex justify-between items-center px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <span className="font-medium">Affected Dependencies</span>
                    {expandedSections.dependencies ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </button>
                  
                  {expandedSections.dependencies && (
                    <div className="p-4 border-t border-gray-200">
                      {result.dependencies.length === 0 ? (
                        <p className="text-gray-500 italic">No dependencies affected</p>
                      ) : (
                        <div className="space-y-3">
                          {result.dependencies.map((dep, index) => (
                            <div key={index} className="bg-gray-50 p-3 rounded border border-gray-200">
                              <div className="flex justify-between items-start mb-2">
                                <span className="font-medium">
                                  {dep.entity_type.replace(/_/g, ' ')} #{dep.entity_id}
                                </span>
                                {getImpactBadge(dep.impact_level)}
                              </div>
                              <pre className="text-xs overflow-x-auto mt-2">
                                {JSON.stringify(dep.details, null, 2)}
                              </pre>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="flex justify-between pt-4 border-t border-gray-200">
                  <button
                    onClick={() => setStep('initial')}
                    className="px-4 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200 transition-colors"
                  >
                    Back
                  </button>
                  
                  <button
                    onClick={handleExecute}
                    disabled={result.result_type === 'not_recommended'}
                    className={`flex items-center px-4 py-2 rounded-md transition-colors ${
                      result.result_type === 'not_recommended'
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    <CheckCircle size={18} className="mr-2" />
                    Execute Intervention
                  </button>
                </div>
                
                {result.result_type === 'not_recommended' && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-3 text-red-700 text-sm">
                    This intervention is not recommended based on simulation results. 
                    Please review the details or try a different approach.
                  </div>
                )}
              </div>
            )}
            
            {step === 'executing' && (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500 mb-4"></div>
                <p className="text-gray-600">Executing intervention...</p>
                <p className="text-gray-500 text-sm mt-2">Applying changes to the system</p>
                
                {executionError && (
                  <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 max-w-md">
                    {executionError}
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default InterventionSimulator;
