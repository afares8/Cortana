import axios from 'axios';
import { 
  ArturInsight, 
  ArturSuggestion, 
  ArturIntervention, 
  ArturSimulation,
  DepartmentHealth,
  HeatmapData,
  Prediction,
  SimulationResult
} from '../types';

const API_URL = '/api/v1/artur';

export const getInsights = async (
  params: { 
    category?: string; 
    entity_type?: string; 
    department_id?: number;
    skip?: number;
    limit?: number;
  } = {}
): Promise<ArturInsight[]> => {
  const response = await axios.get(`${API_URL}/observation/insights`, { params });
  return response.data;
};

export const getInsightById = async (id: number): Promise<ArturInsight> => {
  const response = await axios.get(`${API_URL}/observation/insights/${id}`);
  return response.data;
};

export const getSuggestions = async (
  params: {
    status?: string;
    department_id?: number;
    source?: string;
    skip?: number;
    limit?: number;
    min_confidence?: number;
  } = {}
): Promise<ArturSuggestion[]> => {
  const response = await axios.get(`${API_URL}/evaluation/suggestions`, { params });
  return response.data;
};

export const getSuggestionById = async (id: number): Promise<ArturSuggestion> => {
  const response = await axios.get(`${API_URL}/evaluation/suggestions/${id}`);
  return response.data;
};

export const updateSuggestionStatus = async (id: number, status: string): Promise<ArturSuggestion> => {
  const response = await axios.patch(`${API_URL}/evaluation/suggestions/${id}`, { status });
  return response.data;
};

export const runEvaluationCycle = async (): Promise<{ status: string; message: string }> => {
  const response = await axios.post(`${API_URL}/evaluation/run-evaluation-cycle`);
  return response.data;
};

export const getInterventions = async (
  params: {
    status?: string;
    intervention_type?: string;
    department_id?: number;
    skip?: number;
    limit?: number;
  } = {}
): Promise<ArturIntervention[]> => {
  const response = await axios.get(`${API_URL}/intervention/interventions`, { params });
  return response.data;
};

export const getInterventionById = async (id: number): Promise<ArturIntervention> => {
  const response = await axios.get(`${API_URL}/intervention/interventions/${id}`);
  return response.data;
};

export const prepareIntervention = async (
  suggestion_id: number,
  intervention_type: string
): Promise<ArturIntervention> => {
  const response = await axios.post(`${API_URL}/intervention/prepare`, {
    suggestion_id,
    intervention_type
  });
  return response.data;
};

export const executeIntervention = async (
  intervention_id: number,
  user_id?: number
): Promise<{ status: string; message: string }> => {
  const response = await axios.post(`${API_URL}/intervention/execute/${intervention_id}`, { user_id });
  return response.data;
};

export const rollbackIntervention = async (
  intervention_id: number
): Promise<{ status: string; message: string }> => {
  const response = await axios.post(`${API_URL}/intervention/rollback/${intervention_id}`);
  return response.data;
};

export const getSimulations = async (
  params: {
    status?: string;
    result?: string;
    suggestion_id?: number;
    skip?: number;
    limit?: number;
  } = {}
): Promise<ArturSimulation[]> => {
  const response = await axios.get(`${API_URL}/simulation/simulations`, { params });
  return response.data;
};

export const getSimulationById = async (id: number): Promise<ArturSimulation> => {
  const response = await axios.get(`${API_URL}/simulation/simulations/${id}`);
  return response.data;
};

export const prepareSimulation = async (
  suggestion_id: number,
  simulation_type: string
): Promise<ArturSimulation> => {
  const response = await axios.post(`${API_URL}/simulation/prepare`, {
    suggestion_id,
    simulation_type
  });
  return response.data;
};

export const runSimulation = async (
  simulation_id: number
): Promise<{ status: string; message: string }> => {
  const response = await axios.post(`${API_URL}/simulation/run/${simulation_id}`);
  return response.data;
};

export const runObservationCycle = async (): Promise<{ status: string; message: string }> => {
  const response = await axios.post(`${API_URL}/observation/run-observation-cycle`);
  return response.data;
};

export const getDepartmentHealth = async (): Promise<DepartmentHealth[]> => {
  const response = await axios.get(`${API_URL}/department-health`);
  return response.data;
};

export const getInterventionLogs = async (
  params: {
    department_id?: number;
    from_date?: string;
    to_date?: string;
    action_type?: string;
    skip?: number;
    limit?: number;
  } = {}
): Promise<ArturIntervention[]> => {
  const response = await axios.get(`${API_URL}/interventions/logs`, { params });
  return response.data;
};

export const getHeatmapData = async (): Promise<HeatmapData> => {
  const response = await axios.get(`${API_URL}/insights/heatmap`);
  return response.data;
};

export const getPredictions = async (): Promise<Prediction[]> => {
  const response = await axios.get(`${API_URL}/insights/predictions`);
  return response.data.items;
};

export const simulateIntervention = async (
  params: {
    suggestion_id: number;
    simulation_type: string;
    parameters?: Record<string, unknown>;
  }
): Promise<SimulationResult> => {
  const response = await axios.post(`${API_URL}/simulate`, params);
  return response.data;
};
