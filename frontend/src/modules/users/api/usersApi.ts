import axios from 'axios';
import {
  User,
  UserCreate,
  UserUpdate,
  Role,
  RoleCreate,
  RoleUpdate,
  Permission,
  PermissionCreate,
  PermissionUpdate,
  AuditRecord
} from '../types';

const API_BASE = process.env.VITE_API_URL || '';

const mockUsers: User[] = [
  {
    id: 1,
    name: 'Admin User',
    email: 'admin@example.com',
    active: true,
    roles: [{
      id: 1,
      name: 'Admin',
      permissions: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 2,
    name: 'Legal User',
    email: 'legal@example.com',
    active: true,
    roles: [{
      id: 2,
      name: 'Legal',
      permissions: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 3,
    name: 'Compliance User',
    email: 'compliance@example.com',
    active: true,
    roles: [{
      id: 3,
      name: 'Compliance',
      permissions: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const mockRoles: Role[] = [
  {
    id: 1,
    name: 'Admin',
    permissions: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 2,
    name: 'Legal',
    permissions: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 3,
    name: 'Compliance',
    permissions: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const mockPermissions: Permission[] = [
  { id: 1, name: 'clients.create', description: 'Create Clients', module: 'clients', action: 'create', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 2, name: 'clients.view', description: 'View Clients', module: 'clients', action: 'view', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 3, name: 'clients.edit', description: 'Edit Clients', module: 'clients', action: 'edit', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 4, name: 'clients.delete', description: 'Delete Clients', module: 'clients', action: 'delete', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  
  { id: 5, name: 'contracts.create', description: 'Create Contracts', module: 'contracts', action: 'create', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 6, name: 'contracts.view', description: 'View Contracts', module: 'contracts', action: 'view', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 7, name: 'contracts.edit', description: 'Edit Contracts', module: 'contracts', action: 'edit', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 8, name: 'contracts.delete', description: 'Delete Contracts', module: 'contracts', action: 'delete', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  
  { id: 9, name: 'workflows.create', description: 'Create Workflows', module: 'workflows', action: 'create', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 10, name: 'workflows.view', description: 'View Workflows', module: 'workflows', action: 'view', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 11, name: 'workflows.edit', description: 'Edit Workflows', module: 'workflows', action: 'edit', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 12, name: 'workflows.delete', description: 'Delete Workflows', module: 'workflows', action: 'delete', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  
  { id: 13, name: 'tasks.create', description: 'Create Tasks', module: 'tasks', action: 'create', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 14, name: 'tasks.assign', description: 'Assign Tasks', module: 'tasks', action: 'assign', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 15, name: 'tasks.complete', description: 'Complete Tasks', module: 'tasks', action: 'complete', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 16, name: 'tasks.delete', description: 'Delete Tasks', module: 'tasks', action: 'delete', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  
  { id: 17, name: 'reports.uaf', description: 'Generate UAF Reports', module: 'reports', action: 'uaf', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 18, name: 'reports.audit', description: 'Export Audit Logs', module: 'reports', action: 'audit', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 19, name: 'reports.documents', description: 'Download Documents', module: 'reports', action: 'documents', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  
  { id: 20, name: 'screening.pep', description: 'Run PEP Screening', module: 'screening', action: 'pep', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 21, name: 'screening.sanctions', description: 'Run Sanctions Screening', module: 'screening', action: 'sanctions', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 22, name: 'screening.results', description: 'View Screening Results', module: 'screening', action: 'results', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  
  { id: 23, name: 'users.manage', description: 'Manage Users', module: 'users', action: 'manage', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 24, name: 'users.roles', description: 'Assign Roles', module: 'users', action: 'roles', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 25, name: 'users.permissions', description: 'Edit Permissions', module: 'users', action: 'permissions', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 26, name: 'users.reset', description: 'Reset Passwords', module: 'users', action: 'reset', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  
  { id: 27, name: 'system.audit', description: 'Access Audit Logs', module: 'system', action: 'audit', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 28, name: 'system.settings', description: 'Configure Settings', module: 'system', action: 'settings', created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
];

const mockAuditRecords: AuditRecord[] = [
  {
    id: 1,
    user_id: 1,
    user_name: 'Admin User',
    action: 'create',
    entity_type: 'user',
    entity_id: 2,
    details: 'Created user "Legal User"',
    timestamp: new Date().toISOString()
  },
  {
    id: 2,
    user_id: 1,
    user_name: 'Admin User',
    action: 'update',
    entity_type: 'role',
    entity_id: 2,
    details: 'Updated permissions for role "Legal"',
    timestamp: new Date().toISOString()
  }
];

export const getUsers = async (): Promise<User[]> => {
  try {
    const response = await axios.get(`${API_BASE}/api/v1/users`);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for users');
    return mockUsers;
  }
};

export const getUser = async (id: number): Promise<User> => {
  try {
    const response = await axios.get(`${API_BASE}/api/v1/users/${id}`);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for user');
    const user = mockUsers.find(u => u.id === id);
    if (!user) throw new Error('User not found');
    return user;
  }
};

export const createUser = async (user: UserCreate): Promise<User> => {
  try {
    const response = await axios.post(`${API_BASE}/api/v1/users`, user);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for create user');
    const newUser: User = {
      id: mockUsers.length + 1,
      name: user.name,
      email: user.email,
      active: user.active,
      roles: user.role_ids.map(id => {
        const role = mockRoles.find(r => r.id === id);
        if (!role) throw new Error('Role not found');
        return role;
      }),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    mockUsers.push(newUser);
    return newUser;
  }
};

export const updateUser = async (id: number, user: UserUpdate): Promise<User> => {
  try {
    const response = await axios.put(`${API_BASE}/api/v1/users/${id}`, user);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for update user');
    const userIndex = mockUsers.findIndex(u => u.id === id);
    if (userIndex === -1) throw new Error('User not found');
    
    const updatedUser = {
      ...mockUsers[userIndex],
      ...user,
      roles: user.role_ids ? user.role_ids.map(id => {
        const role = mockRoles.find(r => r.id === id);
        if (!role) throw new Error('Role not found');
        return role;
      }) : mockUsers[userIndex].roles,
      updated_at: new Date().toISOString()
    };
    
    mockUsers[userIndex] = updatedUser;
    return updatedUser;
  }
};

export const deleteUser = async (id: number): Promise<void> => {
  try {
    await axios.delete(`${API_BASE}/api/v1/users/${id}`);
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for delete user');
    const userIndex = mockUsers.findIndex(u => u.id === id);
    if (userIndex === -1) throw new Error('User not found');
    mockUsers.splice(userIndex, 1);
  }
};

export const getRoles = async (): Promise<Role[]> => {
  try {
    const response = await axios.get(`${API_BASE}/api/v1/roles`);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for roles');
    return mockRoles;
  }
};

export const getRole = async (id: number): Promise<Role> => {
  try {
    const response = await axios.get(`${API_BASE}/api/v1/roles/${id}`);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for role');
    const role = mockRoles.find(r => r.id === id);
    if (!role) throw new Error('Role not found');
    return role;
  }
};

export const createRole = async (role: RoleCreate): Promise<Role> => {
  try {
    const response = await axios.post(`${API_BASE}/api/v1/roles`, role);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for create role');
    const newRole: Role = {
      id: mockRoles.length + 1,
      name: role.name,
      permissions: role.permission_ids.map(id => {
        const permission = mockPermissions.find(p => p.id === id);
        if (!permission) throw new Error('Permission not found');
        return permission;
      }),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    mockRoles.push(newRole);
    return newRole;
  }
};

export const updateRole = async (id: number, role: RoleUpdate): Promise<Role> => {
  try {
    const response = await axios.put(`${API_BASE}/api/v1/roles/${id}`, role);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for update role');
    const roleIndex = mockRoles.findIndex(r => r.id === id);
    if (roleIndex === -1) throw new Error('Role not found');
    
    const updatedRole = {
      ...mockRoles[roleIndex],
      ...role,
      permissions: role.permission_ids ? role.permission_ids.map(id => {
        const permission = mockPermissions.find(p => p.id === id);
        if (!permission) throw new Error('Permission not found');
        return permission;
      }) : mockRoles[roleIndex].permissions,
      updated_at: new Date().toISOString()
    };
    
    mockRoles[roleIndex] = updatedRole;
    return updatedRole;
  }
};

export const deleteRole = async (id: number): Promise<void> => {
  try {
    await axios.delete(`${API_BASE}/api/v1/roles/${id}`);
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for delete role');
    const roleIndex = mockRoles.findIndex(r => r.id === id);
    if (roleIndex === -1) throw new Error('Role not found');
    mockRoles.splice(roleIndex, 1);
  }
};

export const getPermissions = async (): Promise<Permission[]> => {
  try {
    const response = await axios.get(`${API_BASE}/api/v1/permissions`);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for permissions');
    return mockPermissions;
  }
};

export const getPermission = async (id: number): Promise<Permission> => {
  try {
    const response = await axios.get(`${API_BASE}/api/v1/permissions/${id}`);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for permission');
    const permission = mockPermissions.find(p => p.id === id);
    if (!permission) throw new Error('Permission not found');
    return permission;
  }
};

export const createPermission = async (permission: PermissionCreate): Promise<Permission> => {
  try {
    const response = await axios.post(`${API_BASE}/api/v1/permissions`, permission);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for create permission');
    const newPermission: Permission = {
      id: mockPermissions.length + 1,
      name: permission.name,
      description: permission.description,
      module: permission.module,
      action: permission.action,
      start_date: permission.start_date,
      end_date: permission.end_date,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    mockPermissions.push(newPermission);
    return newPermission;
  }
};

export const updatePermission = async (id: number, permission: PermissionUpdate): Promise<Permission> => {
  try {
    const response = await axios.put(`${API_BASE}/api/v1/permissions/${id}`, permission);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for update permission');
    const permissionIndex = mockPermissions.findIndex(p => p.id === id);
    if (permissionIndex === -1) throw new Error('Permission not found');
    
    const updatedPermission = {
      ...mockPermissions[permissionIndex],
      ...permission,
      updated_at: new Date().toISOString()
    };
    
    mockPermissions[permissionIndex] = updatedPermission;
    return updatedPermission;
  }
};

export const deletePermission = async (id: number): Promise<void> => {
  try {
    await axios.delete(`${API_BASE}/api/v1/permissions/${id}`);
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for delete permission');
    const permissionIndex = mockPermissions.findIndex(p => p.id === id);
    if (permissionIndex === -1) throw new Error('Permission not found');
    mockPermissions.splice(permissionIndex, 1);
  }
};

export const getUserAuditLogs = async (userId?: number): Promise<AuditRecord[]> => {
  try {
    const url = userId 
      ? `${API_BASE}/api/v1/users/${userId}/audit-logs` 
      : `${API_BASE}/api/v1/users/audit-logs`;
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('API error:', error);
    console.log('Using mock data for audit logs');
    return userId 
      ? mockAuditRecords.filter(record => record.user_id === userId)
      : mockAuditRecords;
  }
};
