import React, { useState, useEffect } from 'react';
import { Play, Cpu } from 'lucide-react';
import { getSimulations, getSimulationById, runSimulation } from '../api/arturApi';
import { ArturSimulation, SimulationStatus, SimulationResult } from '../types';

const SimulationView: React.FC = () => {
  const [simulations, setSimulations] = useState<ArturSimulation[]>([]);
  const [selectedSimulation, setSelectedSimulation] = useState<ArturSimulation | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runningSimulation, setRunningSimulation] = useState(false);

  useEffect(() => {
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    try {
      setLoading(true);
      const data = await getSimulations();
      setSimulations(data);
      setError(null);
    } catch (err) {
      setError('Failed to load simulations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSimulation = async (id: number) => {
    try {
      setDetailLoading(true);
      const data = await getSimulationById(id);
      setSelectedSimulation(data);
    } catch (err) {
      setError('Failed to load simulation details');
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleRunSimulation = async (id: number) => {
    try {
      setRunningSimulation(true);
      await runSimulation(id);
      const updatedSimulation = await getSimulationById(id);
      setSelectedSimulation(updatedSimulation);
      
      await fetchSimulations();
    } catch (err) {
      setError('Failed to run simulation');
      console.error(err);
    } finally {
      setRunningSimulation(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case SimulationStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case SimulationStatus.RUNNING:
        return 'bg-blue-100 text-blue-800';
      case SimulationStatus.FAILED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getResultColor = (result: string) => {
    switch (result) {
      case SimulationResult.RECOMMENDED:
        return 'bg-green-100 text-green-800';
      case SimulationResult.NEUTRAL:
        return 'bg-gray-100 text-gray-800';
      case SimulationResult.NOT_RECOMMENDED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <Cpu className="h-8 w-8 mr-3 text-purple-600" />
          <h1 className="text-2xl font-bold">Simulation Environment</h1>
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
              <h2 className="text-lg font-medium">Simulation History</h2>
            </div>
            
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500"></div>
              </div>
            ) : simulations.length === 0 ? (
              <div className="p-6 text-center">
                <p className="text-gray-500">No simulations available</p>
              </div>
            ) : (
              <div className="overflow-y-auto max-h-[600px]">
                {simulations.map((simulation) => (
                  <div
                    key={simulation.id}
                    onClick={() => handleSelectSimulation(simulation.id)}
                    className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                      selectedSimulation?.id === simulation.id ? 'bg-purple-50' : ''
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center mb-1">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mr-2 ${getStatusColor(
                              simulation.status
                            )}`}
                          >
                            {simulation.status}
                          </span>
                          {simulation.result && (
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getResultColor(
                                simulation.result
                              )}`}
                            >
                              {simulation.result}
                            </span>
                          )}
                        </div>
                        <p className="text-sm font-medium">
                          Simulation #{simulation.id} for Suggestion #{simulation.suggestion_id}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(simulation.created_at).toLocaleString()}
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
          {!selectedSimulation ? (
            <div className="bg-white shadow-md rounded-lg p-8 text-center h-full flex flex-col justify-center items-center">
              <Cpu className="h-16 w-16 text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Simulation</h3>
              <p className="text-gray-500 max-w-md">
                Choose a simulation from the list to view its details and outcomes.
              </p>
            </div>
          ) : detailLoading ? (
            <div className="bg-white shadow-md rounded-lg p-8 flex justify-center items-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
            </div>
          ) : (
            <div className="bg-white shadow-md rounded-lg overflow-hidden">
              <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                <h2 className="text-lg font-medium">
                  Simulation #{selectedSimulation.id} Details
                </h2>
                {selectedSimulation.status === SimulationStatus.PENDING && (
                  <button
                    onClick={() => handleRunSimulation(selectedSimulation.id)}
                    disabled={runningSimulation}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded-md flex items-center text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {runningSimulation ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                        Running...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        Run Simulation
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
                        selectedSimulation.status
                      )}`}
                    >
                      {selectedSimulation.status}
                    </span>
                    {selectedSimulation.result && (
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ml-2 ${getResultColor(
                          selectedSimulation.result
                        )}`}
                      >
                        {selectedSimulation.result}
                      </span>
                    )}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Timing</h3>
                    <p className="text-sm">
                      Created: {new Date(selectedSimulation.created_at).toLocaleString()}
                    </p>
                    {selectedSimulation.completed_at && (
                      <p className="text-sm">
                        Completed: {new Date(selectedSimulation.completed_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Simulation Parameters</h3>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <pre className="whitespace-pre-wrap text-sm">
                      {JSON.stringify(selectedSimulation.simulation_parameters, null, 2)}
                    </pre>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Expected Outcomes</h3>
                    <div className="bg-gray-50 p-3 rounded-md">
                      <pre className="whitespace-pre-wrap text-sm">
                        {JSON.stringify(selectedSimulation.expected_outcomes, null, 2)}
                      </pre>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Actual Outcomes</h3>
                    <div className="bg-gray-50 p-3 rounded-md">
                      <pre className="whitespace-pre-wrap text-sm">
                        {JSON.stringify(selectedSimulation.actual_outcomes, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Dependencies</h3>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <ul className="space-y-2">
                      {selectedSimulation.dependencies.map((dep, index) => (
                        <li key={index} className="text-sm">
                          <span className="font-medium">{dep.type}:</span> {dep.name} (ID: {dep.id})
                          {dep.impact && (
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ml-2 ${
                                dep.impact === 'high'
                                  ? 'bg-red-100 text-red-800'
                                  : dep.impact === 'medium'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {dep.impact} impact
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SimulationView;
