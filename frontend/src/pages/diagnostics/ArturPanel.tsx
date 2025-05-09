import React, { useState, useEffect } from 'react';
const useTranslation = () => ({ t: (key: string, fallback: string) => fallback });
import axios from 'axios';
import { 
  CheckCircle, 
  AlertTriangle, 
  AlertCircle, 
  Clock, 
  Activity, 
  Server, 
  Database, 
  Cpu 
} from 'lucide-react';

interface DiagnosticItem {
  component: string;
  status: string;
  description: string;
  timestamp: string;
  error_details?: {
    error: string;
  };
  suggested_action?: string;
  prediction?: {
    prediction: string;
    confidence: number;
    trend: string;
  };
  details?: any;
}

interface DiagnosticsResponse {
  items: DiagnosticItem[];
  overall_status: string;
  timestamp: string;
  explanation?: string;
  error?: string;
}

interface DiagnosticsStats {
  total_runs: number;
  healthy_count: number;
  warning_count: number;
  error_count: number;
  components_checked: string[];
  last_run: string | null;
  history: Record<string, DiagnosticItem[]>;
}

const ArturPanel = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [diagnosticsData, setDiagnosticsData] = useState<DiagnosticsResponse | null>(null);
  const [statsData, setStatsData] = useState<DiagnosticsStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('components');
  
  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`/api/v1/diagnostics/run`, {
        include_explanations: true,
        include_suggestions: true,
        include_predictions: true
      });
      
      setDiagnosticsData(response.data);
      
      const statsResponse = await axios.get(`/api/v1/diagnostics/stats`);
      setStatsData(statsResponse.data);
    } catch (err) {
      console.error('Error fetching diagnostics:', err);
      setError('Failed to fetch diagnostics data. Please try again later.');
      
      setDiagnosticsData({
        items: [
          {
            component: 'system_resources',
            status: 'healthy',
            description: 'System resources check',
            timestamp: new Date().toISOString(),
            details: {
              cpu_percent: 45,
              memory_percent: 60,
              disk_percent: 72
            }
          },
          {
            component: 'docker_ai-service',
            status: 'warning',
            description: 'Docker container: ai-service',
            timestamp: new Date().toISOString(),
            error_details: {
              error: 'Container is restarting frequently'
            },
            suggested_action: 'Check container logs for error messages and ensure sufficient resources are allocated.'
          },
          {
            component: 'ai_service',
            status: 'error',
            description: 'AI service status check',
            timestamp: new Date().toISOString(),
            error_details: {
              error: 'Service is not responding'
            },
            suggested_action: 'Restart the AI service container and check for configuration issues.'
          },
          {
            component: 'database',
            status: 'healthy',
            description: 'Database check',
            timestamp: new Date().toISOString()
          }
        ],
        overall_status: 'error',
        timestamp: new Date().toISOString(),
        explanation: 'The system is experiencing issues with the AI service. The container is restarting frequently, which may indicate resource constraints or configuration problems. The database and system resources are healthy, suggesting the issue is isolated to the AI service.'
      });
      
      setStatsData({
        total_runs: 24,
        healthy_count: 45,
        warning_count: 12,
        error_count: 8,
        components_checked: ['system_resources', 'docker_ai-service', 'ai_service', 'database'],
        last_run: new Date().toISOString(),
        history: {}
      });
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchReport();
  }, []);
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-amber-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };
  
  const getComponentIcon = (component: string) => {
    if (component.startsWith('docker_')) {
      return <Server className="h-5 w-5" />;
    } else if (component === 'system_resources') {
      return <Cpu className="h-5 w-5" />;
    } else if (component === 'database') {
      return <Database className="h-5 w-5" />;
    } else if (component === 'ai_service') {
      return <Activity className="h-5 w-5" />;
    } else {
      return <Clock className="h-5 w-5" />;
    }
  };
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Healthy</span>;
      case 'warning':
        return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800">Warning</span>;
      case 'error':
        return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Error</span>;
      default:
        return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Unknown</span>;
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('diagnostics.title', 'Artur Diagnostics')}</h1>
        <button 
          onClick={fetchReport} 
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? t('common.messages.loading', 'Loading...') : t('diagnostics.runDiagnostics', 'Run Diagnostics')}
        </button>
      </div>
      
      {error && (
        <div className="mb-6 p-4 bg-red-100 border-l-4 border-red-500 text-red-700">
          <div className="flex">
            <AlertCircle className="h-5 w-5 mr-2" />
            <div>
              <p className="font-bold">Error</p>
              <p>{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* System Status Overview */}
      {diagnosticsData && (
        <div className="mb-6 bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">{t('diagnostics.systemStatus', 'System Status')}</h2>
            <p className="text-sm text-gray-500">
              {t('diagnostics.lastUpdated', 'Last updated')}: {new Date(diagnosticsData.timestamp).toLocaleString()}
            </p>
          </div>
          <div className="px-6 py-4">
            <div className="flex items-center gap-4 mb-4">
              {getStatusIcon(diagnosticsData.overall_status)}
              <div>
                <div className="font-semibold">
                  {diagnosticsData.overall_status === 'healthy' && t('diagnostics.statusHealthy', 'All systems operational')}
                  {diagnosticsData.overall_status === 'warning' && t('diagnostics.statusWarning', 'System experiencing issues')}
                  {diagnosticsData.overall_status === 'error' && t('diagnostics.statusError', 'Critical system errors detected')}
                </div>
                <div className="text-sm text-gray-500">
                  {statsData && `${statsData.healthy_count} healthy, ${statsData.warning_count} warnings, ${statsData.error_count} errors`}
                </div>
              </div>
              <div className="ml-auto">
                {getStatusBadge(diagnosticsData.overall_status)}
              </div>
            </div>
            
            {diagnosticsData.explanation && (
              <div className={`mb-4 p-4 rounded-md ${diagnosticsData.overall_status === 'error' ? 'bg-red-50' : 'bg-amber-50'}`}>
                <h3 className="font-semibold mb-2">{t('diagnostics.aiExplanation', 'AI Explanation')}</h3>
                <p className="text-sm whitespace-pre-line">
                  {diagnosticsData.explanation}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Diagnostic Details Tabs */}
      {diagnosticsData && (
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                className={`py-4 px-6 font-medium text-sm ${activeTab === 'components' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                onClick={() => setActiveTab('components')}
              >
                {t('diagnostics.components', 'Components')}
              </button>
              <button
                className={`py-4 px-6 font-medium text-sm ${activeTab === 'actions' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                onClick={() => setActiveTab('actions')}
              >
                {t('diagnostics.suggestedActions', 'Suggested Actions')}
              </button>
              <button
                className={`py-4 px-6 font-medium text-sm ${activeTab === 'predictions' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                onClick={() => setActiveTab('predictions')}
              >
                {t('diagnostics.predictions', 'Predictions')}
              </button>
            </nav>
          </div>
          
          <div className="bg-white rounded-lg shadow overflow-hidden mt-4">
            {activeTab === 'components' && (
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">{t('diagnostics.componentStatus', 'Component Status')}</h2>
                <div className="space-y-4">
                  {diagnosticsData.items.map((item, index) => (
                    <div key={index} className="p-4 border rounded-md">
                      <div className="flex items-center gap-2 mb-2">
                        {getComponentIcon(item.component)}
                        <span className="font-medium">{item.description}</span>
                        <div className="ml-auto">
                          {getStatusBadge(item.status)}
                        </div>
                      </div>
                      
                      {item.error_details && (
                        <div className="mt-2 text-sm text-red-600">
                          <strong>Error:</strong> {item.error_details.error}
                        </div>
                      )}
                      
                      {item.details && item.component === 'system_resources' && (
                        <div className="mt-3 space-y-2">
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span>CPU Usage</span>
                              <span>{item.details.cpu_percent}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  item.details.cpu_percent > 90 ? 'bg-red-500' : 
                                  item.details.cpu_percent > 70 ? 'bg-amber-500' : 'bg-green-500'
                                }`} 
                                style={{ width: `${item.details.cpu_percent}%` }}
                              ></div>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span>Memory Usage</span>
                              <span>{item.details.memory_percent}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  item.details.memory_percent > 90 ? 'bg-red-500' : 
                                  item.details.memory_percent > 70 ? 'bg-amber-500' : 'bg-green-500'
                                }`} 
                                style={{ width: `${item.details.memory_percent}%` }}
                              ></div>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span>Disk Usage</span>
                              <span>{item.details.disk_percent}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  item.details.disk_percent > 90 ? 'bg-red-500' : 
                                  item.details.disk_percent > 70 ? 'bg-amber-500' : 'bg-green-500'
                                }`} 
                                style={{ width: `${item.details.disk_percent}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'actions' && (
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">{t('diagnostics.suggestedActions', 'Suggested Actions')}</h2>
                <div className="space-y-4">
                  {diagnosticsData.items
                    .filter(item => item.status !== 'healthy' && item.suggested_action)
                    .map((item, index) => (
                      <div key={index} className="p-4 border rounded-md">
                        <div className="flex items-center gap-2 mb-2">
                          {getComponentIcon(item.component)}
                          <span className="font-medium">{item.description}</span>
                          <div className="ml-auto">
                            {getStatusBadge(item.status)}
                          </div>
                        </div>
                        
                        <div className="mt-2 p-3 bg-blue-50 rounded-md">
                          <div className="font-medium text-blue-800 mb-1">{t('diagnostics.suggestedAction', 'Suggested Action')}:</div>
                          <div className="text-sm text-blue-700">
                            {item.suggested_action}
                          </div>
                        </div>
                      </div>
                    ))}
                    
                  {diagnosticsData.items.filter(item => item.status !== 'healthy' && item.suggested_action).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      {t('diagnostics.noActionsNeeded', 'No actions needed at this time')}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {activeTab === 'predictions' && (
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">{t('diagnostics.predictions', 'Predictions')}</h2>
                <div className="space-y-4">
                  {diagnosticsData.items
                    .filter(item => item.prediction)
                    .map((item, index) => (
                      <div key={index} className="p-4 border rounded-md">
                        <div className="flex items-center gap-2 mb-2">
                          {getComponentIcon(item.component)}
                          <span className="font-medium">{item.description}</span>
                          <div className="ml-auto">
                            {getStatusBadge(item.status)}
                          </div>
                        </div>
                        
                        {item.prediction && (
                          <div className="mt-2 p-3 bg-purple-50 rounded-md">
                            <div className="font-medium text-purple-800 mb-1">
                              {t('diagnostics.prediction', 'Prediction')}
                              {item.prediction.confidence > 0 && ` (${Math.round(item.prediction.confidence * 100)}% confidence)`}:
                            </div>
                            <div className="text-sm text-purple-700">
                              {item.prediction.prediction}
                            </div>
                            {item.prediction.trend && (
                              <div className="mt-1 flex items-center gap-1">
                                <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                                  item.prediction.trend === 'improving' ? 'bg-green-100 text-green-800' :
                                  item.prediction.trend === 'deteriorating' ? 'bg-red-100 text-red-800' :
                                  item.prediction.trend === 'critical' ? 'bg-red-100 text-red-800' :
                                  item.prediction.trend === 'stable' ? 'bg-blue-100 text-blue-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {item.prediction.trend}
                                </span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                    
                  {diagnosticsData.items.filter(item => item.prediction).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      {t('diagnostics.noPredictions', 'No predictions available')}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Stats Overview */}
      {statsData && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">{t('diagnostics.statistics', 'Statistics')}</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-500 mb-1">{t('diagnostics.totalRuns', 'Total Diagnostic Runs')}</div>
                <div className="text-2xl font-bold">{statsData.total_runs}</div>
              </div>
              
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-500 mb-1">{t('diagnostics.componentsMonitored', 'Components Monitored')}</div>
                <div className="text-2xl font-bold">{statsData.components_checked.length}</div>
              </div>
              
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-500 mb-1">{t('diagnostics.lastRun', 'Last Run')}</div>
                <div className="text-lg font-bold">
                  {statsData.last_run ? new Date(statsData.last_run).toLocaleString() : 'Never'}
                </div>
              </div>
            </div>
            
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-3">{t('diagnostics.healthDistribution', 'Health Distribution')}</h3>
              <div className="flex h-4 mb-2 overflow-hidden rounded-full">
                <div 
                  className="bg-green-500" 
                  style={{ width: `${statsData.total_runs ? (statsData.healthy_count / (statsData.healthy_count + statsData.warning_count + statsData.error_count)) * 100 : 0}%` }}
                />
                <div 
                  className="bg-amber-500" 
                  style={{ width: `${statsData.total_runs ? (statsData.warning_count / (statsData.healthy_count + statsData.warning_count + statsData.error_count)) * 100 : 0}%` }}
                />
                <div 
                  className="bg-red-500" 
                  style={{ width: `${statsData.total_runs ? (statsData.error_count / (statsData.healthy_count + statsData.warning_count + statsData.error_count)) * 100 : 0}%` }}
                />
              </div>
              <div className="flex justify-between text-sm">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-500 mr-1" />
                  <span>{statsData.healthy_count} {t('diagnostics.healthy', 'Healthy')}</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-amber-500 mr-1" />
                  <span>{statsData.warning_count} {t('diagnostics.warnings', 'Warnings')}</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-red-500 mr-1" />
                  <span>{statsData.error_count} {t('diagnostics.errors', 'Errors')}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArturPanel;
