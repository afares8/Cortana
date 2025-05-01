export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface Contract {
  id: number;
  title: string;
  client_name: string;
  contract_type: string;
  start_date: string;
  expiration_date: string;
  responsible_lawyer: string;
  description?: string;
  status: 'active' | 'expired' | 'terminated';
  file_path: string;
  created_at: string;
  updated_at?: string;
}

export interface DashboardStats {
  total_active_contracts: number;
  contracts_expiring_soon: number;
  overdue_contracts: number;
  total_contracts: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface ExtractedClause {
  id: number;
  contract_id: number;
  clause_type: string;
  clause_text: string;
  start_position: number;
  end_position: number;
  confidence_score: number;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface RiskScore {
  id: number;
  contract_id: number;
  overall_score: number;
  missing_clauses: string[];
  abnormal_durations: boolean;
  red_flag_terms: Array<{term: string; category: string}>;
  risk_factors: Record<string, number>;
  last_updated: string;
  created_at: string;
  updated_at?: string;
}

export interface ContractAnomaly {
  id: number;
  contract_id: number;
  anomaly_type: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  detected_at: string;
  created_at: string;
  updated_at?: string;
}

export interface ComplianceCheck {
  id: number;
  contract_id: number;
  check_type: string;
  is_compliant: boolean;
  issues: string[];
  recommendations: string[];
  last_checked: string;
  created_at: string;
  updated_at?: string;
}

export interface AIQuery {
  id: number;
  query_text: string;
  response_text: string;
  related_contract_ids: number[];
  timestamp: string;
  created_at: string;
  updated_at?: string;
}

export interface AIDashboardStats {
  total_contracts: number;
  analyzed_contracts: number;
  risk_distribution: {
    high_risk: number;
    medium_risk: number;
    low_risk: number;
  };
  anomalies: {
    total: number;
    high_severity: number;
    medium_severity: number;
    low_severity: number;
  };
  clauses: {
    total: number;
    by_type: Record<string, number>;
  };
}
