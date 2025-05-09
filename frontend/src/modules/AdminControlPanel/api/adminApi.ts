import axios from 'axios';
import { 
  Department, 
  Role, 
  Function, 
  AutomationRule, 
  AIProfile, 
  DepartmentTemplate,
  UserDepartmentRole,
  AuditLog
} from '../types';

const API_URL = '/api/v1';

export const getDepartments = async (): Promise<Department[]> => {
  const response = await axios.get(`${API_URL}/admin/departments`);
  return response.data;
};

export const getDepartment = async (id: number): Promise<Department> => {
  const response = await axios.get(`${API_URL}/admin/departments/${id}`);
  return response.data;
};

export const createDepartment = async (department: Omit<Department, 'id'>): Promise<Department> => {
  const response = await axios.post(`${API_URL}/admin/departments`, department);
  return response.data;
};

export const updateDepartment = async (id: number, department: Partial<Department>): Promise<Department> => {
  const response = await axios.put(`${API_URL}/admin/departments/${id}`, department);
  return response.data;
};

export const deleteDepartment = async (id: number): Promise<void> => {
  await axios.delete(`${API_URL}/admin/departments/${id}`);
};

export const getRoles = async (): Promise<Role[]> => {
  const response = await axios.get(`${API_URL}/admin/roles`);
  return response.data;
};

export const getRolesByDepartment = async (departmentId: number): Promise<Role[]> => {
  const response = await axios.get(`${API_URL}/admin/roles/by-department/${departmentId}`);
  return response.data;
};

export const createRole = async (role: Omit<Role, 'id'>): Promise<Role> => {
  const response = await axios.post(`${API_URL}/admin/roles`, role);
  return response.data;
};

export const assignRole = async (assignment: UserDepartmentRole): Promise<UserDepartmentRole> => {
  const response = await axios.post(`${API_URL}/admin/roles/assign`, assignment);
  return response.data;
};

export const getFunctions = async (): Promise<Function[]> => {
  const response = await axios.get(`${API_URL}/admin/functions`);
  return response.data;
};

export const getFunctionsByDepartment = async (departmentId: number): Promise<Function[]> => {
  const response = await axios.get(`${API_URL}/admin/functions/by-department/${departmentId}`);
  return response.data;
};

export const createFunction = async (func: Omit<Function, 'id'>): Promise<Function> => {
  const response = await axios.post(`${API_URL}/admin/functions`, func);
  return response.data;
};

export const getAutomationRules = async (): Promise<AutomationRule[]> => {
  const response = await axios.get(`${API_URL}/automation/rules`);
  return response.data;
};

export const getAutomationRulesByDepartment = async (departmentId: number): Promise<AutomationRule[]> => {
  const response = await axios.get(`${API_URL}/automation/rules/by-department/${departmentId}`);
  return response.data;
};

export const createAutomationRule = async (rule: Omit<AutomationRule, 'id'>): Promise<AutomationRule> => {
  const response = await axios.post(`${API_URL}/automation/rules`, rule);
  return response.data;
};

export const getAIProfiles = async (): Promise<AIProfile[]> => {
  const response = await axios.get(`${API_URL}/ai/profiles`);
  return response.data;
};

export const getAIProfileByDepartment = async (departmentId: number): Promise<AIProfile> => {
  const response = await axios.get(`${API_URL}/ai/profiles/by-department/${departmentId}`);
  return response.data;
};

export const createAIProfile = async (profile: Omit<AIProfile, 'id'>): Promise<AIProfile> => {
  const response = await axios.post(`${API_URL}/ai/profiles`, profile);
  return response.data;
};

export const getTemplates = async (): Promise<DepartmentTemplate[]> => {
  const response = await axios.get(`${API_URL}/admin/templates`);
  return response.data;
};

export const createTemplate = async (template: Omit<DepartmentTemplate, 'id'>): Promise<DepartmentTemplate> => {
  const response = await axios.post(`${API_URL}/admin/templates`, template);
  return response.data;
};

export const createDepartmentFromTemplate = async (
  templateId: number, 
  departmentName: string,
  companyId: string,
  country: string,
  timezone: string,
  customize?: Record<string, any>
): Promise<{ success: boolean, department_id: number }> => {
  const response = await axios.post(`${API_URL}/admin/templates/from-template`, {
    template_id: templateId,
    department_name: departmentName,
    company_id: companyId,
    country,
    timezone,
    customize
  });
  return response.data;
};

export const getUserDepartments = async (userId: number): Promise<UserDepartmentRole[]> => {
  const response = await axios.get(`${API_URL}/users/${userId}/departments`);
  return response.data;
};

export const assignUserToDepartment = async (
  userId: number,
  departmentId: number,
  roleId: number
): Promise<UserDepartmentRole> => {
  const response = await axios.post(`${API_URL}/users/${userId}/assign-to-department`, {
    user_id: userId,
    department_id: departmentId,
    role_id: roleId
  });
  return response.data;
};

export const getAuditLogs = async (
  filters?: {
    user_id?: number;
    action_type?: string;
    target_type?: string;
    target_id?: number;
    success?: boolean;
    start_date?: string;
    end_date?: string;
  }
): Promise<AuditLog[]> => {
  const response = await axios.get(`${API_URL}/admin/audit`, { params: filters });
  return response.data;
};

export const getAuditSummary = async (days: number = 7): Promise<{
  total_logs: number;
  success_count: number;
  error_count: number;
  action_type_counts: Record<string, number>;
  target_type_counts: Record<string, number>;
  recent_errors: AuditLog[];
}> => {
  const response = await axios.get(`${API_URL}/admin/audit/summary`, { params: { days } });
  return response.data;
};
