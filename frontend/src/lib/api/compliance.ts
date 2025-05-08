import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

export interface CustomerData {
  name: string;
  dob?: string;
  country: string;
  type: 'natural' | 'legal';
  id_number?: string;
  nationality?: string;
  activity?: string;
  incorporation_date?: string;
}

export interface EntityData {
  name: string;
  dob?: string;
  country: string;
  type: 'natural' | 'legal';
  role?: string;
}

export interface VerifyCustomerRequest {
  customer: CustomerData;
  directors?: EntityData[];
  ubos?: EntityData[];
}

export interface CountryRisk {
  country_code: string;
  name: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  fatf_status?: string;
  eu_high_risk: boolean;
  basel_score?: number;
  basel_rank?: number;
  last_updated?: string;
}

export interface VerificationMatch {
  source: string;
  name: string;
  score: number;
  details: Record<string, unknown>;
}

export interface EntityVerificationResult {
  name: string;
  enriched_data: Record<string, unknown>;
  pep_matches: VerificationMatch[];
  sanctions_matches: VerificationMatch[];
  risk_score: number;
}

export interface VerificationReport {
  id: string;
  path: string;
  generated_at: string;
}

export interface VerificationResponse {
  customer: EntityVerificationResult;
  directors?: EntityVerificationResult[];
  ubos?: EntityVerificationResult[];
  country_risk: CountryRisk;
  report: VerificationReport;
  sources_checked: string[];
}

export interface RiskMapData {
  last_updated: string;
  countries: Record<string, CountryRisk>;
}

export interface ListUpdate {
  list_name: string;
  update_date: string;
  status: string;
}

export interface RecentVerification {
  id: string;
  client_name: string;
  verification_date: string;
  result: string;
  risk_level: string;
  report_path?: string;
}

export interface ComplianceDashboardData {
  active_contracts: number;
  expiring_contracts: number;
  pep_matches: number;
  sanctions_matches: number;
  pending_reports: number;
  high_risk_clients: number;
  recent_verifications: RecentVerification[];
  recent_list_updates: ListUpdate[];
}

export const verifyCustomer = async (data: VerifyCustomerRequest): Promise<VerificationResponse> => {
  const response = await axios.post(`${API_BASE}/compliance/verify-customer`, data);
  return response.data;
};

export const getCountryRiskMap = async (): Promise<RiskMapData> => {
  const response = await axios.get(`${API_BASE}/compliance/country-risk`);
  return response.data;
};

export const getComplianceDashboard = async (): Promise<ComplianceDashboardData> => {
  const response = await axios.get(`${API_BASE}/compliance/dashboard`);
  return response.data;
};

export const downloadUafReport = async (reportId: string): Promise<Blob> => {
  const response = await axios.get(`${API_BASE}/compliance/reports/${reportId}/download`, {
    responseType: 'blob'
  });
  return response.data;
};
