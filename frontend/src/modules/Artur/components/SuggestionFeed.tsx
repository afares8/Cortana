import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Lightbulb, 
  Check, 
  X, 
  PlayCircle, 
  Filter, 
  ChevronDown, 
  ChevronUp,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { ArturSuggestion, SuggestionStatus } from '../types';
import { useSuggestions } from '../hooks/useArturData';

interface SuggestionFeedProps {
  departmentId?: number;
  onSimulate: (suggestion: ArturSuggestion) => void;
  onApply: (suggestion: ArturSuggestion) => void;
  onDismiss: (suggestion: ArturSuggestion) => void;
}

const SuggestionFeed: React.FC<SuggestionFeedProps> = ({ 
  departmentId, 
  onSimulate, 
  onApply, 
  onDismiss 
}) => {
  const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
  const [filterType, setFilterType] = useState<string>("");
  const [filterSeverity, setFilterSeverity] = useState<string>("");
  
  const { data: suggestions, loading, error, refetch } = useSuggestions({
    status: SuggestionStatus.PENDING,
    department_id: departmentId,
    source: filterType || undefined,
    min_confidence: filterSeverity ? parseFloat(filterSeverity) / 100 : undefined
  });
  
  const toggleFilter = () => {
    setIsFilterOpen(!isFilterOpen);
  };
  
  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterType(e.target.value);
  };
  
  const handleSeverityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterSeverity(e.target.value);
  };
  
  const getSeverityBadge = (confidence: number) => {
    if (confidence >= 0.8) {
      return (
        <span className="flex items-center text-xs font-medium px-2 py-1 rounded-full bg-red-100 text-red-800">
          <AlertTriangle size={12} className="mr-1" />
          High
        </span>
      );
    } else if (confidence >= 0.5) {
      return (
        <span className="flex items-center text-xs font-medium px-2 py-1 rounded-full bg-yellow-100 text-yellow-800">
          <AlertTriangle size={12} className="mr-1" />
          Medium
        </span>
      );
    } else {
      return (
        <span className="flex items-center text-xs font-medium px-2 py-1 rounded-full bg-blue-100 text-blue-800">
          <AlertTriangle size={12} className="mr-1" />
          Low
        </span>
      );
    }
  };
  
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white rounded-lg shadow-md p-4 mb-6"
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Actionable Suggestions</h2>
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Suggestion Type</label>
              <select
                value={filterType}
                onChange={handleTypeChange}
                className="pl-4 pr-10 py-2 border border-gray-300 rounded-md w-full focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Types</option>
                <option value="function_usage">Function Usage</option>
                <option value="rule_overlap">Rule Overlap</option>
                <option value="resource_optimization">Resource Optimization</option>
                <option value="ai_profile_adjustment">AI Profile Adjustment</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Severity (Confidence)</label>
              <select
                value={filterSeverity}
                onChange={handleSeverityChange}
                className="pl-4 pr-10 py-2 border border-gray-300 rounded-md w-full focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Severities</option>
                <option value="80">High (80%+)</option>
                <option value="50">Medium (50%+)</option>
                <option value="30">Low (30%+)</option>
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
          <p>Error loading suggestions. Please try again.</p>
        </div>
      ) : suggestions.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-md text-center">
          <p className="text-gray-500">No pending suggestions found.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {suggestions.map((suggestion, index) => (
            <motion.div 
              key={suggestion.id}
              initial={{ x: -10, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-start">
                  <Lightbulb className="h-5 w-5 text-yellow-500 mt-0.5 mr-2 flex-shrink-0" />
                  <div>
                    <h3 className="font-medium text-gray-900">{suggestion.issue_summary}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {(suggestion.suggested_action as Record<string, string>).description || 
                       `Artur suggests an action based on ${suggestion.source.replace(/_/g, ' ')} analysis.`}
                    </p>
                  </div>
                </div>
                {getSeverityBadge(suggestion.confidence_score)}
              </div>
              
              <div className="mt-3 pt-3 border-t border-gray-100">
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => onSimulate(suggestion)}
                    className="flex items-center px-3 py-1.5 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 transition-colors text-sm"
                  >
                    <PlayCircle size={16} className="mr-1.5" />
                    Simulate
                  </button>
                  <button
                    onClick={() => onApply(suggestion)}
                    className="flex items-center px-3 py-1.5 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm"
                  >
                    <Check size={16} className="mr-1.5" />
                    Apply Now
                  </button>
                  <button
                    onClick={() => onDismiss(suggestion)}
                    className="flex items-center px-3 py-1.5 bg-gray-50 text-gray-700 rounded-md hover:bg-gray-100 transition-colors text-sm"
                  >
                    <X size={16} className="mr-1.5" />
                    Dismiss
                  </button>
                </div>
                <div className="mt-2 flex items-center">
                  <span className="text-xs text-gray-500">
                    Confidence: {Math.round(suggestion.confidence_score * 100)}%
                  </span>
                  <div className="ml-2 bg-gray-200 h-1.5 w-24 rounded-full overflow-hidden">
                    <div 
                      className="bg-blue-500 h-full rounded-full" 
                      style={{ width: `${suggestion.confidence_score * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default SuggestionFeed;
