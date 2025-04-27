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
