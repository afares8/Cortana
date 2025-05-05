import axios from 'axios';

const API_URL = 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

import { 
  InvoiceRecord,
  TrafficSubmission,
  InvoiceDataUpload,
  ConsolidationRequest,
  ConsolidationResponse,
  SubmissionRequest,
  SubmissionResponse
} from '../types';

export const uploadInvoiceData = async (data: InvoiceDataUpload): Promise<InvoiceRecord[]> => {
  const response = await axios.post(`${API_BASE}/traffic/upload`, data);
  return response.data;
};

export const getRecords = async (params?: {
  skip?: number;
  limit?: number;
  status?: string;
  client_id?: string;
  movement_type?: string;
}): Promise<InvoiceRecord[]> => {
  const response = await axios.get(`${API_BASE}/traffic/records`, { params });
  return response.data;
};

export const getRecord = async (id: number): Promise<InvoiceRecord> => {
  const response = await axios.get(`${API_BASE}/traffic/record/${id}`);
  return response.data;
};

export const consolidateInvoices = async (request: ConsolidationRequest): Promise<ConsolidationResponse> => {
  const response = await axios.post(`${API_BASE}/traffic/consolidate`, request);
  return response.data;
};

export const submitToDMCE = async (request: SubmissionRequest): Promise<SubmissionResponse> => {
  const response = await axios.post(`${API_BASE}/traffic/submit`, request);
  return response.data;
};

export const getSubmissionLogs = async (params?: {
  skip?: number;
  limit?: number;
  status?: string;
  client_id?: string;
  movement_type?: string;
  start_date?: string;
  end_date?: string;
}): Promise<TrafficSubmission[]> => {
  const response = await axios.get(`${API_BASE}/traffic/logs`, { params });
  return response.data;
};

export const getSubmissionLog = async (id: number): Promise<TrafficSubmission> => {
  const response = await axios.get(`${API_BASE}/traffic/logs/${id}`);
  return response.data;
};
