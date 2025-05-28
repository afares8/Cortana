
export interface Client {
  id: number;
  name: string;
  contact_email: string;
  contact_phone?: string;
  address?: string;
  industry?: string;
  kyc_verified: boolean;
  notes?: string;
  created_at: string;
  updated_at?: string;
  client_type?: string;
  country?: string;
  risk_score?: number;
  risk_level?: string;
  risk_details?: Record<string, any>;
  pep_screening_id?: number;
  sanctions_screening_id?: number;
  verification_status?: string;
  verification_date?: string;
  verification_result?: Record<string, any>;
}

export interface ClientCreate {
  name: string;
  contact_email: string;
  contact_phone?: string;
  address?: string;
  industry?: string;
  kyc_verified?: boolean;
  notes?: string;
  client_type?: string;
  country?: string;
}

export interface ClientUpdate {
  name?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  industry?: string;
  kyc_verified?: boolean;
  notes?: string;
}

export interface Contract {
  id: number;
  title: string;
  client_id: number;
  client_name?: string;
  contract_type: string;
  start_date: string;
  expiration_date?: string;
  responsible_lawyer: string;
  description?: string;
  status: string;
  file_path: string;
  versions?: ContractVersion[];
  created_at: string;
  updated_at?: string;
  metadata?: Record<string, any>;
}

export interface ContractCreate {
  title: string;
  client_id: number;
  contract_type: string;
  start_date: string;
  expiration_date?: string;
  responsible_lawyer: string;
  description?: string;
  status?: string;
  file_content?: string;
  metadata?: Record<string, any>;
}

export interface ContractUpdate {
  title?: string;
  client_id?: number;
  contract_type?: string;
  start_date?: string;
  expiration_date?: string;
  responsible_lawyer?: string;
  description?: string;
  status?: string;
  file_content?: string;
  changes_description?: string;
  metadata?: Record<string, any>;
}

export interface ContractVersion {
  id: number;
  contract_id: number;
  version: number;
  file_path: string;
  changes_description?: string;
  created_by: string;
  created_at: string;
}

export interface ApprovalStep {
  step_id: string;
  role: string;
  approver_email?: string;
  approver_id?: number;
  is_approved: boolean;
  approved_at?: string;
  comments?: string;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description?: string;
  steps: ApprovalStep[];
  created_at: string;
  updated_at?: string;
}

export interface WorkflowInstance {
  id: number;
  template_id: string;
  contract_id: number;
  current_step_id: string;
  status: string;
  steps: ApprovalStep[];
  created_at: string;
  updated_at?: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  assigned_to?: string;
  related_contract_id?: number;
  related_client_id?: number;
  status: string;
  priority: string;
  ai_generated: boolean;
  contract_title?: string;
  client_name?: string;
  created_at: string;
  updated_at?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  due_date?: string;
  assigned_to?: string;
  related_contract_id?: number;
  related_client_id?: number;
  status?: string;
  priority?: string;
  ai_generated?: boolean;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  due_date?: string;
  assigned_to?: string;
  status?: string;
  priority?: string;
}

export interface AuditLogEntry {
  id: number;
  entity_type: string;
  entity_id: number;
  action: string;
  user_id?: number;
  user_email?: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface LegalDashboardStats {
  clients: {
    total: number;
    active: number;
    inactive: number;
  };
  contracts: {
    total: number;
    active: number;
    expiring_soon: number;
    expired: number;
  };
  tasks: {
    total: number;
    pending: number;
    completed: number;
    overdue: number;
  };
  workflows: {
    total: number;
    pending_approval: number;
    approved: number;
    rejected: number;
  };
}

export interface AuditLog {
  id: number;
  action: string;
  entity_type: string;
  entity_id: number;
  user_id: number;
  user_name: string;
  details: string;
  timestamp: string;
}

export interface DueDiligenceResponse {
  full_name: string;
  passport: string;
  country: string;
  results: {
    OFAC: MatchResult[];
    UN: MatchResult[];
    EU: MatchResult[];
    PEP: MatchResult[];
  };
  status: string;
  risk_score: number;
  verification_id?: number;
  verification_date: string;
}

export interface MatchResult {
  name: string;
  score: number;
  source?: string;
  details?: string;
}

export interface ContractAnalysisResult {
  clauses?: string[];
  risk_score?: number;
  anomalies?: string[];
  rewrites?: Record<string, string>;
  impact?: string;
  error?: string;
}

export interface LegalQAResponse {
  response: string;
  error?: string;
}
