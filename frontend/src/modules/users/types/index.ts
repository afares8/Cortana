export interface User {
  id: number;
  name: string;
  email: string;
  active: boolean;
  roles: Role[];
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  name: string;
  email: string;
  password: string;
  active: boolean;
  role_ids: number[];
}

export interface UserUpdate {
  name?: string;
  email?: string;
  password?: string;
  active?: boolean;
  role_ids?: number[];
}

export interface Role {
  id: number;
  name: string;
  permissions: Permission[];
  created_at: string;
  updated_at: string;
}

export interface RoleCreate {
  name: string;
  permission_ids: number[];
}

export interface RoleUpdate {
  name?: string;
  permission_ids?: number[];
}

export interface Permission {
  id: number;
  name: string;
  description: string;
  module: string;
  action: string;
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export interface PermissionCreate {
  name: string;
  description: string;
  module: string;
  action: string;
  start_date?: string;
  end_date?: string;
}

export interface PermissionUpdate {
  name?: string;
  description?: string;
  module?: string;
  action?: string;
  start_date?: string;
  end_date?: string;
}

export interface AuditRecord {
  id: number;
  user_id: number;
  user_name: string;
  action: string;
  entity_type: string;
  entity_id: number;
  details: string;
  timestamp: string;
}
