import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Filter, ChevronDown, ChevronUp, Zap, X } from 'lucide-react';
import { useHeatmapData } from '../hooks/useArturData';

interface IntelligentHeatmapProps {
  departmentId?: number;
}

const IntelligentHeatmap: React.FC<IntelligentHeatmapProps> = () => {
  const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
  const [filterMetric, setFilterMetric] = useState<'token_usage' | 'function_executions' | 'rule_triggers'>('token_usage');
  const [selectedDepartment, setSelectedDepartment] = useState<number | null>(null);
  const [tooltipInfo, setTooltipInfo] = useState<{ 
    visible: boolean; 
    x: number; 
    y: number; 
    content: React.ReactNode;
  }>({ visible: false, x: 0, y: 0, content: null });
  
  const heatmapRef = useRef<HTMLDivElement>(null);
  
  const { data: heatmapData, loading, error, refetch } = useHeatmapData();
  
  const toggleFilter = () => {
    setIsFilterOpen(!isFilterOpen);
  };
  
  const handleMetricChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterMetric(e.target.value as 'token_usage' | 'function_executions' | 'rule_triggers');
  };
  
  const handleDepartmentClick = (departmentId: number) => {
    setSelectedDepartment(departmentId === selectedDepartment ? null : departmentId);
  };
  
  const showTooltip = (e: React.MouseEvent, content: React.ReactNode) => {
    const rect = heatmapRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setTooltipInfo({
      visible: true,
      x,
      y,
      content
    });
  };
  
  const hideTooltip = () => {
    setTooltipInfo(prev => ({ ...prev, visible: false }));
  };
  
  const getMetricValue = (item: { ia_token_usage: number; function_executions: number; rule_triggers: number }) => {
    switch (filterMetric) {
      case 'token_usage':
        return item.ia_token_usage;
      case 'function_executions':
        return item.function_executions;
      case 'rule_triggers':
        return item.rule_triggers;
      default:
        return 0;
    }
  };
  
  const getMaxValue = () => {
    switch (filterMetric) {
      case 'token_usage':
        return heatmapData.max_token_usage;
      case 'function_executions':
        return heatmapData.max_executions;
      case 'rule_triggers':
        return heatmapData.max_triggers;
      default:
        return 1;
    }
  };
  
  const getColorIntensity = (value: number) => {
    const maxValue = getMaxValue();
    const intensity = Math.min(0.9, Math.max(0.1, value / maxValue));
    return intensity;
  };
  
  const getMetricLabel = () => {
    switch (filterMetric) {
      case 'token_usage':
        return 'IA Token Usage';
      case 'function_executions':
        return 'Function Executions';
      case 'rule_triggers':
        return 'Rule Triggers';
      default:
        return '';
    }
  };
  
  const getHealthColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white rounded-lg shadow-md p-4 mb-6"
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Intelligent Heatmap</h2>
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Metric</label>
              <select
                value={filterMetric}
                onChange={handleMetricChange}
                className="pl-4 pr-10 py-2 border border-gray-300 rounded-md w-full focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="token_usage">IA Token Usage</option>
                <option value="function_executions">Function Executions</option>
                <option value="rule_triggers">Rule Triggers</option>
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
          <p>Error loading heatmap data. Please try again.</p>
        </div>
      ) : heatmapData.items.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-md text-center">
          <p className="text-gray-500">No heatmap data available.</p>
        </div>
      ) : (
        <div className="relative">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center">
              <Zap size={16} className="text-blue-500 mr-1" />
              <span className="text-sm font-medium">{getMetricLabel()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-blue-100"></div>
              <span className="text-xs text-gray-500">Low</span>
              <div className="w-3 h-3 bg-blue-300"></div>
              <span className="text-xs text-gray-500">Medium</span>
              <div className="w-3 h-3 bg-blue-500"></div>
              <span className="text-xs text-gray-500">High</span>
            </div>
          </div>
          
          <div 
            ref={heatmapRef}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 relative"
          >
            {heatmapData.items.map((item) => {
              const intensity = getColorIntensity(getMetricValue(item));
              const bgColor = `rgba(59, 130, 246, ${intensity})`;
              
              return (
                <motion.div
                  key={item.department_id}
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer"
                  style={{ backgroundColor: bgColor }}
                  onClick={() => handleDepartmentClick(item.department_id)}
                >
                  <div className="flex justify-between items-start">
                    <h3 className="font-medium text-white text-shadow">{item.department_name}</h3>
                    <div className={`w-3 h-3 rounded-full ${getHealthColor(item.health_score)}`}></div>
                  </div>
                  
                  <div className="mt-4 text-white text-shadow">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm">IA Tokens:</span>
                      <span className="font-medium">{item.ia_token_usage.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm">Functions:</span>
                      <span className="font-medium">{item.function_executions}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Rules:</span>
                      <span className="font-medium">{item.rule_triggers}</span>
                    </div>
                  </div>
                  
                  {item.hotspots.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-white border-opacity-30">
                      <div className="text-xs text-white text-shadow mb-2">Hotspots:</div>
                      <div className="flex flex-wrap gap-2">
                        {item.hotspots.map((hotspot, index) => (
                          <div
                            key={index}
                            className="w-6 h-6 rounded-full bg-yellow-400 flex items-center justify-center text-xs font-bold text-yellow-900 cursor-pointer"
                            onMouseEnter={(e) => showTooltip(e, (
                              <div>
                                <div className="font-medium mb-1">{hotspot.type.replace(/_/g, ' ')}</div>
                                <div className="text-sm">Entity ID: {hotspot.entity_id}</div>
                                <div className="text-sm">Value: {hotspot.value}</div>
                              </div>
                            ))}
                            onMouseLeave={hideTooltip}
                          >
                            {index + 1}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              );
            })}
            
            {tooltipInfo.visible && (
              <div 
                className="absolute bg-white shadow-lg rounded-md p-3 z-10 w-48"
                style={{ 
                  left: `${tooltipInfo.x + 10}px`, 
                  top: `${tooltipInfo.y + 10}px`,
                  transform: 'translate(0, -50%)'
                }}
              >
                {tooltipInfo.content}
              </div>
            )}
          </div>
          
          {selectedDepartment && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 bg-gray-50 p-4 rounded-lg border border-gray-200"
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-medium text-gray-900">
                  {heatmapData.items.find(item => item.department_id === selectedDepartment)?.department_name} Details
                </h3>
                <button
                  onClick={() => setSelectedDepartment(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X size={18} />
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-3 rounded-md border border-gray-200">
                  <h4 className="font-medium text-gray-800 mb-2">Metrics</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Health Score:</span>
                      <span className="font-medium">
                        {heatmapData.items.find(item => item.department_id === selectedDepartment)?.health_score}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">IA Token Usage:</span>
                      <span className="font-medium">
                        {heatmapData.items.find(item => item.department_id === selectedDepartment)?.ia_token_usage.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Function Executions:</span>
                      <span className="font-medium">
                        {heatmapData.items.find(item => item.department_id === selectedDepartment)?.function_executions}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Rule Triggers:</span>
                      <span className="font-medium">
                        {heatmapData.items.find(item => item.department_id === selectedDepartment)?.rule_triggers}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white p-3 rounded-md border border-gray-200">
                  <h4 className="font-medium text-gray-800 mb-2">Hotspots</h4>
                  {heatmapData.items.find(item => item.department_id === selectedDepartment)?.hotspots.length === 0 ? (
                    <p className="text-gray-500 italic">No hotspots detected</p>
                  ) : (
                    <div className="space-y-2">
                      {heatmapData.items.find(item => item.department_id === selectedDepartment)?.hotspots.map((hotspot, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <div>
                            <div className="font-medium text-gray-800">
                              {hotspot.type.replace(/_/g, ' ')}
                            </div>
                            <div className="text-xs text-gray-500">
                              Entity ID: {hotspot.entity_id}
                            </div>
                          </div>
                          <div className="text-sm font-medium">
                            {hotspot.value}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      )}
      
      <style>
        {`
          .text-shadow {
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
          }
        `}
      </style>
    </motion.div>
  );
};

export default IntelligentHeatmap;
