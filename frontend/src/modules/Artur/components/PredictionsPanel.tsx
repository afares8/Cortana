import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Calendar, 
  ChevronDown, 
  ChevronUp,
  RefreshCw,
  Clock,
  ArrowRight
} from 'lucide-react';
import { usePredictions } from '../hooks/useArturData';

interface PredictionsPanelProps {
  departmentId?: number;
}

const PredictionsPanel: React.FC<PredictionsPanelProps> = ({ departmentId }) => {
  const [expandedPrediction, setExpandedPrediction] = useState<number | null>(null);
  
  const { data: predictions, loading, error, refetch } = usePredictions(true); // Auto-refresh enabled
  
  const togglePrediction = (id: number) => {
    setExpandedPrediction(expandedPrediction === id ? null : id);
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };
  
  const getImpactColor = (score: number) => {
    if (score >= 80) return 'bg-red-100 text-red-800';
    if (score >= 50) return 'bg-yellow-100 text-yellow-800';
    return 'bg-blue-100 text-blue-800';
  };
  
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.5) return 'bg-yellow-500';
    return 'bg-blue-500';
  };
  
  const filteredPredictions = departmentId 
    ? predictions.filter(p => p.department_id === departmentId)
    : predictions;
  
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white rounded-lg shadow-md p-4 mb-6"
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Predictive Insights</h2>
        <div className="flex items-center space-x-2">
          <button 
            onClick={refetch}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Refresh"
          >
            <RefreshCw size={18} className="text-gray-600" />
          </button>
          <div className="text-xs text-gray-500 flex items-center">
            <Clock size={12} className="mr-1" />
            Auto-refreshes every 5 minutes
          </div>
        </div>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-800 p-4 rounded-md">
          <p>Error loading predictions. Please try again.</p>
        </div>
      ) : filteredPredictions.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-md text-center">
          <p className="text-gray-500">No predictions available at this time.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredPredictions.map((prediction, index) => (
            <motion.div 
              key={prediction.id}
              initial={{ x: -10, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden"
            >
              <div 
                className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => togglePrediction(prediction.id)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex items-start">
                    <TrendingUp className="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                    <div>
                      <h3 className="font-medium text-gray-900">{prediction.summary}</h3>
                      <div className="flex items-center mt-1 text-sm text-gray-500">
                        <Calendar size={14} className="mr-1" />
                        <span>Predicted for {formatDate(prediction.predicted_timestamp)}</span>
                      </div>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${getImpactColor(prediction.impact_score)}`}>
                    Impact: {prediction.impact_score}/100
                  </span>
                </div>
                
                <div className="flex justify-between items-center mt-3">
                  <div className="flex items-center">
                    <span className="text-xs text-gray-500 mr-2">
                      Confidence: {Math.round(prediction.confidence * 100)}%
                    </span>
                    <div className="bg-gray-200 h-1.5 w-24 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${getConfidenceColor(prediction.confidence)}`}
                        style={{ width: `${prediction.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div>
                    {expandedPrediction === prediction.id ? (
                      <ChevronUp size={18} className="text-gray-500" />
                    ) : (
                      <ChevronDown size={18} className="text-gray-500" />
                    )}
                  </div>
                </div>
              </div>
              
              {expandedPrediction === prediction.id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="bg-gray-50 p-4 border-t border-gray-200"
                >
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-800 mb-2">Details</h4>
                    <div className="bg-white p-3 rounded border border-gray-200">
                      {Object.entries(prediction.details).map(([key, value]) => (
                        <div key={key} className="flex justify-between py-1 border-b border-gray-100 last:border-0">
                          <span className="text-sm text-gray-600">{key.replace(/_/g, ' ')}:</span>
                          <span className="text-sm font-medium">{value as string}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-800 mb-2">Department</h4>
                    <div className="bg-white p-3 rounded border border-gray-200">
                      <span className="font-medium">{prediction.department_name}</span>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-800 mb-2">Prediction Type</h4>
                    <div className="bg-white p-3 rounded border border-gray-200">
                      <span className="font-medium">{prediction.prediction_type.replace(/_/g, ' ')}</span>
                    </div>
                  </div>
                  
                  <div className="flex justify-end mt-4">
                    <button className="flex items-center px-3 py-1.5 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 transition-colors text-sm">
                      View Related Insights
                      <ArrowRight size={14} className="ml-1.5" />
                    </button>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default PredictionsPanel;
