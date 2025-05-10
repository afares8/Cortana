import React, { useState, useEffect } from 'react';
import { History, RotateCcw } from 'lucide-react';
import { getInterventions, getInterventionById, rollbackIntervention } from '../api/arturApi';
import { ArturIntervention, InterventionStatus } from '../types';

const InterventionLog: React.FC = () => {
  const [interventions, setInterventions] = useState<ArturIntervention[]>([]);
  const [selectedIntervention, setSelectedIntervention] = useState<ArturIntervention | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rollingBack, setRollingBack] = useState(false);

  useEffect(() => {
    fetchInterventions();
  }, []);

  const fetchInterventions = async () => {
    try {
      setLoading(true);
      const data = await getInterventions();
      setInterventions(data);
      setError(null);
    } catch (err) {
      setError('Failed to load interventions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectIntervention = async (id: number) => {
    try {
      setDetailLoading(true);
      const data = await getInterventionById(id);
      setSelectedIntervention(data);
    } catch (err) {
      setError('Failed to load intervention details');
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleRollback = async (id: number) => {
    try {
      setRollingBack(true);
      await rollbackIntervention(id);
      const updatedIntervention = await getInterventionById(id);
      setSelectedIntervention(updatedIntervention);
      
      await fetchInterventions();
    } catch (err) {
      setError('Failed to rollback intervention');
      console.error(err);
    } finally {
      setRollingBack(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case InterventionStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case InterventionStatus.IN_PROGRESS:
        return 'bg-blue-100 text-blue-800';
      case InterventionStatus.FAILED:
        return 'bg-red-100 text-red-800';
      case InterventionStatus.ROLLED_BACK:
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <History className="h-8 w-8 mr-3 text-indigo-600" />
          <h1 className="text-2xl font-bold">Intervention Log</h1>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="p-4 bg-gray-50 border-b">
              <h2 className="text-lg font-medium">Intervention History</h2>
            </div>
            
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500"></div>
              </div>
            ) : interventions.length === 0 ? (
              <div className="p-6 text-center">
                <p className="text-gray-500">No interventions available</p>
              </div>
            ) : (
              <div className="overflow-y-auto max-h-[600px]">
                {interventions.map((intervention) => (
                  <div
                    key={intervention.id}
                    onClick={() => handleSelectIntervention(intervention.id)}
                    className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                      selectedIntervention?.id === intervention.id ? 'bg-indigo-50' : ''
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center mb-1">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mr-2 ${getStatusColor(
                              intervention.status
                            )}`}
                          >
                            {intervention.status}
                          </span>
                        </div>
                        <p className="text-sm font-medium">
                          {intervention.intervention_type}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(intervention.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          {!selectedIntervention ? (
            <div className="bg-white shadow-md rounded-lg p-8 text-center h-full flex flex-col justify-center items-center">
              <History className="h-16 w-16 text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Select an Intervention</h3>
              <p className="text-gray-500 max-w-md">
                Choose an intervention from the list to view its details and rollback options.
              </p>
            </div>
          ) : detailLoading ? (
            <div className="bg-white shadow-md rounded-lg p-8 flex justify-center items-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
            </div>
          ) : (
            <div className="bg-white shadow-md rounded-lg overflow-hidden">
              <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                <h2 className="text-lg font-medium">
                  Intervention #{selectedIntervention.id} Details
                </h2>
                {selectedIntervention.status === InterventionStatus.COMPLETED && (
                  <button
                    onClick={() => handleRollback(selectedIntervention.id)}
                    disabled={rollingBack}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded-md flex items-center text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {rollingBack ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                        Rolling Back...
                      </>
                    ) : (
                      <>
                        <RotateCcw className="h-4 w-4 mr-1" />
                        Rollback
                      </>
                    )}
                  </button>
                )}
              </div>

              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Status</h3>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                        selectedIntervention.status
                      )}`}
                    >
                      {selectedIntervention.status}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Timing</h3>
                    <p className="text-sm">
                      Created: {new Date(selectedIntervention.created_at).toLocaleString()}
                    </p>
                    {selectedIntervention.executed_at && (
                      <p className="text-sm">
                        Executed: {new Date(selectedIntervention.executed_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Intervention Type</h3>
                  <p className="text-sm bg-gray-50 p-3 rounded-md">
                    {selectedIntervention.intervention_type}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">State Before</h3>
                    <div className="bg-gray-50 p-3 rounded-md">
                      <pre className="whitespace-pre-wrap text-sm">
                        {JSON.stringify(selectedIntervention.state_before, null, 2)}
                      </pre>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">State After</h3>
                    <div className="bg-gray-50 p-3 rounded-md">
                      <pre className="whitespace-pre-wrap text-sm">
                        {JSON.stringify(selectedIntervention.state_after, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>

                {selectedIntervention.user_id && (
                  <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Executed By</h3>
                    <p className="text-sm bg-gray-50 p-3 rounded-md">
                      User ID: {selectedIntervention.user_id}
                    </p>
                  </div>
                )}

                {selectedIntervention.status === InterventionStatus.ROLLED_BACK && (
                  <div className="p-4 bg-purple-50 border border-purple-200 rounded-md flex items-start">
                    <RotateCcw className="h-5 w-5 text-purple-600 mr-2 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-purple-800">Intervention Rolled Back</p>
                      <p className="text-sm text-purple-700">
                        This intervention has been rolled back to its previous state.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterventionLog;
