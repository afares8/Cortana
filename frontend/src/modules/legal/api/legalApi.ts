import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

import { 
  Client, 
  ClientCreate, 
  ClientUpdate,
  Contract, 
  ContractCreate, 
  ContractUpdate,
  ContractVersion,
  WorkflowTemplate,
  WorkflowInstance,
  Task,
  TaskCreate,
  TaskUpdate,
  AuditLog,
  DueDiligenceResponse,
  ContractAnalysisResult,
  LegalQAResponse
} from '../types';

export const getClients = async (params?: { 
  skip?: number; 
  limit?: number;
  name?: string;
  industry?: string;
  kyc_verified?: boolean;
}): Promise<Client[]> => {
  const response = await axios.get(`${API_BASE}/legal/clients`, { params });
  return response.data;
};

export const getClient = async (id: number): Promise<Client> => {
  const response = await axios.get(`${API_BASE}/legal/clients/${id}`);
  return response.data;
};

export const createClient = async (client: ClientCreate): Promise<Client> => {
  console.log('API: Creating client with data:', client);
  try {
    const response = await axios.post(`${API_BASE}/legal/clients`, client);
    console.log('API: Client created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('API: Error creating client:', error);
    throw error;
  }
};

export const updateClient = async (id: number, client: ClientUpdate): Promise<Client> => {
  const response = await axios.put(`${API_BASE}/legal/clients/${id}`, client);
  return response.data;
};

export const deleteClient = async (id: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_BASE}/legal/clients/${id}`);
  return response.data;
};

export const getContracts = async (params?: {
  skip?: number;
  limit?: number;
  client_id?: number;
  contract_type?: string;
  status?: string;
  responsible_lawyer?: string;
  start_date_after?: string;
  expiration_date_before?: string;
}): Promise<Contract[]> => {
  const response = await axios.get(`${API_BASE}/legal/contracts`, { params });
  return response.data;
};

export const getContract = async (id: number): Promise<Contract> => {
  const response = await axios.get(`${API_BASE}/legal/contracts/${id}`);
  return response.data;
};

export const createContract = async (contract: ContractCreate): Promise<Contract> => {
  const response = await axios.post(`${API_BASE}/legal/contracts`, contract);
  return response.data;
};

export const updateContract = async (id: number, contract: ContractUpdate): Promise<Contract> => {
  const response = await axios.put(`${API_BASE}/legal/contracts/${id}`, contract);
  return response.data;
};

export const deleteContract = async (id: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_BASE}/legal/contracts/${id}`);
  return response.data;
};

export const getContractVersions = async (contractId: number): Promise<ContractVersion[]> => {
  const response = await axios.get(`${API_BASE}/legal/contracts/${contractId}/versions`);
  return response.data;
};

export const getContractVersion = async (contractId: number, version: number): Promise<ContractVersion> => {
  const response = await axios.get(`${API_URL}/legal/contracts/${contractId}/versions/${version}`);
  return response.data;
};

export const getWorkflowTemplates = async (): Promise<WorkflowTemplate[]> => {
  const response = await axios.get(`${API_URL}/legal/workflows/templates`);
  return response.data;
};

export const getWorkflowTemplate = async (id: string): Promise<WorkflowTemplate> => {
  const response = await axios.get(`${API_URL}/legal/workflows/templates/${id}`);
  return response.data;
};

export const createWorkflowTemplate = async (template: any): Promise<WorkflowTemplate> => {
  const response = await axios.post(`${API_URL}/legal/workflows/templates`, template);
  return response.data;
};

export const updateWorkflowTemplate = async (id: string, template: any): Promise<WorkflowTemplate> => {
  const response = await axios.put(`${API_URL}/legal/workflows/templates/${id}`, template);
  return response.data;
};

export const deleteWorkflowTemplate = async (id: string): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_URL}/legal/workflows/templates/${id}`);
  return response.data;
};

export const getWorkflowInstances = async (params?: {
  skip?: number;
  limit?: number;
  template_id?: string;
  contract_id?: number;
  status?: string;
}): Promise<WorkflowInstance[]> => {
  const response = await axios.get(`${API_URL}/legal/workflows/instances`, { params });
  return response.data;
};

export const getWorkflowInstance = async (id: number): Promise<WorkflowInstance> => {
  const response = await axios.get(`${API_URL}/legal/workflows/instances/${id}`);
  return response.data;
};

export const createWorkflowInstance = async (instance: any): Promise<WorkflowInstance> => {
  const response = await axios.post(`${API_URL}/legal/workflows/instances`, instance);
  return response.data;
};

export const updateWorkflowStep = async (
  instanceId: number, 
  stepId: string, 
  stepData: any
): Promise<WorkflowInstance> => {
  const response = await axios.put(
    `${API_URL}/legal/workflows/instances/${instanceId}/steps/${stepId}`, 
    stepData
  );
  return response.data;
};

export const getTasks = async (params?: {
  skip?: number;
  limit?: number;
  assigned_to?: string;
  status?: string;
  priority?: string;
  related_contract_id?: number;
  related_client_id?: number;
  due_date_before?: string;
  ai_generated?: boolean;
}): Promise<Task[]> => {
  const response = await axios.get(`${API_URL}/legal/tasks`, { params });
  return response.data;
};

export const getTask = async (id: number): Promise<Task> => {
  const response = await axios.get(`${API_URL}/legal/tasks/${id}`);
  return response.data;
};

export const createTask = async (task: TaskCreate): Promise<Task> => {
  const response = await axios.post(`${API_URL}/legal/tasks`, task);
  return response.data;
};

export const updateTask = async (id: number, task: TaskUpdate): Promise<Task> => {
  const response = await axios.put(`${API_URL}/legal/tasks/${id}`, task);
  return response.data;
};

export const deleteTask = async (id: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_URL}/legal/tasks/${id}`);
  return response.data;
};

export const getAuditLogs = async (params?: {
  skip?: number;
  limit?: number;
  entity_type?: string;
  entity_id?: number;
  action?: string;
  user_email?: string;
  start_date?: string;
  end_date?: string;
}): Promise<AuditLog[]> => {
  const response = await axios.get(`${API_URL}/legal/audit-logs`, { params });
  return response.data;
};

export const verifyClient = async (
  clientId: number, 
  data?: { name?: string; country?: string; type?: string }
): Promise<DueDiligenceResponse> => {
  const payload = {
    client_id: clientId,
    ...data
  };
  
  const response = await axios.post(`${API_BASE}/legal/verify-client`, payload);
  return response.data;
};

export const analyzeContract = async (contractId: number): Promise<ContractAnalysisResult> => {
  const response = await axios.post(`${API_BASE}/legal/contracts/${contractId}/analyze`);
  return response.data;
};

export const evaluateClientRisk = async (
  clientId: number, 
  clientData: { 
    client_type?: string; 
    country?: string; 
    industry?: string; 
    channel?: string 
  }
): Promise<any> => {
  const payload = {
    client_id: clientId,
    client_data: clientData
  };
  
  const response = await axios.post(`${API_BASE}/compliance/risk-evaluation`, payload);
  return response.data;
};

export const generateUAFReport = async (
  clientId: number,
  startDate: string,
  endDate: string
): Promise<any> => {
  const payload = {
    client_id: clientId,
    start_date: startDate,
    end_date: endDate
  };
  
  const response = await axios.post(`${API_BASE}/compliance/uaf-reports`, payload);
  return response.data;
};

export const downloadUAFReport = async (reportId: number): Promise<Blob> => {
  const response = await axios.get(`${API_BASE}/compliance/reports/${reportId}/download`, {
    responseType: 'blob'
  });
  return response.data;
};
