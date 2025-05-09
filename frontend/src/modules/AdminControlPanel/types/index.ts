export interface Department {
  id: number;
  name: string;
  type: string;
  ai_enabled: boolean;
  ai_profile?: string;
  country: string;
  timezone: string;
  company_id: string;
}

export interface Role {
  id: number;
  name: string;
  description: string;
  department_id: number;
  permissions: string[];
}

export interface Function {
  id: number;
  name: string;
  description: string;
  input_schema: Record<string, any>;
  output_schema: Record<string, any>;
  department_id: number;
}

export interface AutomationRule {
  id: number;
  name: string;
  trigger_event: string;
  conditions: Record<string, any>;
  actions: Record<string, any>[];
  department_id: number;
  active: boolean;
}

export interface AIProfile {
  id: number;
  name: string;
  model: string;
  embedding_id: string;
  temperature: number;
  top_p: number;
  context_type: string;
  department_id: number;
}

export interface DepartmentTemplate {
  id: number;
  name: string;
  description: string;
  predefined_modules: string[];
  roles: Record<string, any>;
  functions: Record<string, any>;
  ai_profile: Record<string, any>;
}

export interface UserDepartmentRole {
  user_id: number;
  department_id: number;
  role_id: number;
  department_name?: string;
  role_name?: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  action_type: string;
  target_type: string;
  target_id?: number;
  payload: Record<string, any>;
  success: boolean;
  error_message?: string;
  created_at: string;
}
