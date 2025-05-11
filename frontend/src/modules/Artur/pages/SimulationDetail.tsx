import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  ArrowRight,
  Loader
} from 'lucide-react';
import { getSimulationById, executeIntervention } from '../api/arturApi';

interface Dependency {
  entity_type: string;
  entity_id: number;
  impact_level: string;
  details: Record<string, unknown>;
  before?: Record<string, unknown>;
  after?: Record<string, unknown>;
}

interface Simulation {
  id: number;
  suggestion_id: number;
  simulation_type: string;
  parameters: Record<string, unknown>;
  before_state: Record<string, unknown>;
  after_state: Record<string, unknown>;
  dependencies: Dependency[];
  result_type: string;
  confidence_score: number;
  created_at: string;
  completed_at?: string;
  status: string;
}

const SimulationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [executing, setExecuting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchSimulation = async () => {
      try {
        setLoading(true);
        if (id) {
          const data = await getSimulationById(parseInt(id));
          setSimulation(data as unknown as Simulation);
        }
      } catch (err) {
        setError('Failed to load simulation details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSimulation();
  }, [id]);
  
  const handleExecute = async () => {
    if (!simulation) return;
    
    try {
      setExecuting(true);
      await executeIntervention(simulation.suggestion_id);
      navigate('/admin/artur');
    } catch (err) {
      setError('Failed to execute intervention');
      console.error(err);
    } finally {
      setExecuting(false);
    }
  };
  
  const handleBack = () => {
    navigate('/admin/artur');
  };
  
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  
  const getResultIcon = (result?: string) => {
    if (!result) return <AlertTriangle className="h-5 w-5 text-gray-500" />;
    
    switch (result) {
      case 'recommended':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'neutral':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'not_recommended':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-500" />;
    }
  };
  
  const getImpactColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'border-red-300 bg-red-50';
      case 'medium':
        return 'border-yellow-300 bg-yellow-50';
      case 'low':
        return 'border-green-300 bg-green-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center mb-6">
        <button 
          onClick={handleBack}
          className="mr-4 p-2 rounded hover:bg-gray-100"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <h1 className="text-2xl font-bold">Simulation Detail</h1>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      ) : !simulation ? (
        <div className="text-center py-8 text-gray-500">
          Simulation not found.
        </div>
      ) : (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          <div className="lg:col-span-1">
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Simulation Info</h2>
              
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-500 mb-1">Status</div>
                  <div className={`inline-block px-2 py-1 rounded text-xs ${getStatusColor(simulation.status)}`}>
                    {simulation.status.replace(/_/g, ' ')}
                  </div>
                </div>
                
                {simulation.result_type && (
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Result</div>
                    <div className="flex items-center">
                      {getResultIcon(simulation.result_type)}
                      <span className="ml-2">
                        {simulation.result_type === 'recommended' ? 'Recommended' : 
                         simulation.result_type === 'neutral' ? 'Neutral Impact' : 
                         'Not Recommended'}
                      </span>
                    </div>
                  </div>
                )}
                
                <div>
                  <div className="text-sm text-gray-500 mb-1">Confidence</div>
                  <div className="flex items-center">
                    <div className="bg-gray-200 h-2 w-24 rounded-full overflow-hidden mr-2">
                      <div 
                        className="bg-blue-500 h-full rounded-full" 
                        style={{ width: `${simulation.confidence_score * 100}%` }}
                      ></div>
                    </div>
                    <span>{Math.round(simulation.confidence_score * 100)}%</span>
                  </div>
                </div>
                
                <div>
                  <div className="text-sm text-gray-500 mb-1">Created</div>
                  <div>{new Date(simulation.created_at).toLocaleString()}</div>
                </div>
                
                {simulation.completed_at && (
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Completed</div>
                    <div>{new Date(simulation.completed_at).toLocaleString()}</div>
                  </div>
                )}
                
                {simulation.status === 'completed' && 
                 simulation.result_type === 'recommended' && (
                  <div className="mt-6">
                    <button
                      onClick={handleExecute}
                      disabled={executing}
                      className="w-full flex justify-center items-center px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                    >
                      {executing ? (
                        <>
                          <Loader className="h-5 w-5 mr-2 animate-spin" />
                          Executing...
                        </>
                      ) : (
                        <>
                          <ArrowRight className="h-5 w-5 mr-2" />
                          Execute Changes
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
            
            <div className="bg-white shadow-md rounded-lg p-6 mt-6">
              <h2 className="text-lg font-semibold mb-4">Simulation Parameters</h2>
              <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-80">
                <pre className="text-xs">{JSON.stringify(simulation.parameters, null, 2)}</pre>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-2">
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">State Changes</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Before</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-80">
                    <pre className="text-xs">{JSON.stringify(simulation.before_state, null, 2)}</pre>
                  </div>
                </div>
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">After</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-80">
                    <pre className="text-xs">{JSON.stringify(simulation.after_state, null, 2)}</pre>
                  </div>
                </div>
              </div>
              
              <h2 className="text-lg font-semibold mb-4">Dependency Impact</h2>
              
              {simulation.dependencies.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No dependencies affected by this simulation.
                </div>
              ) : (
                <div className="space-y-4">
                  {simulation.dependencies.map((dep, index) => (
                    <motion.div 
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`border rounded-lg p-4 ${getImpactColor(dep.impact_level)}`}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="font-medium">
                          {dep.entity_type.replace(/_/g, ' ')} #{dep.entity_id}
                        </h3>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          dep.impact_level === 'high' ? 'bg-red-100 text-red-800' :
                          dep.impact_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {dep.impact_level.charAt(0).toUpperCase() + dep.impact_level.slice(1)} Impact
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 mb-3">
                        {JSON.stringify(dep.details).includes('description') 
                          ? (dep.details as Record<string, string>).description 
                          : `This ${dep.entity_type.replace(/_/g, ' ')} will be affected by the proposed changes.`}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <div className="text-xs font-medium text-gray-500 mb-1">Before</div>
                          <div className="bg-white p-2 rounded border border-gray-200 text-xs overflow-auto max-h-40">
                            <pre>{JSON.stringify(dep.before || dep.details, null, 2)}</pre>
                          </div>
                        </div>
                        <div>
                          <div className="text-xs font-medium text-gray-500 mb-1">After</div>
                          <div className="bg-white p-2 rounded border border-gray-200 text-xs overflow-auto max-h-40">
                            <pre>{JSON.stringify(dep.after || {}, null, 2)}</pre>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default SimulationDetail;
