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

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getUsers = async (): Promise<User[]> => {
  try {
    const response = await api.get('/admin/users');
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};

export const getUser = async (id: number): Promise<User> => {
  try {
    const response = await api.get(`/admin/users/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching user with ID ${id}:`, error);
    throw error;
  }
};

export const createUser = async (user: UserCreate): Promise<User> => {
  try {
    const response = await api.post('/admin/users', user);
    return response.data;
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
};

export const updateUser = async (id: number, user: UserUpdate): Promise<User> => {
  try {
    const response = await api.put(`/admin/users/${id}`, user);
    return response.data;
  } catch (error) {
    console.error(`Error updating user with ID ${id}:`, error);
    throw error;
  }
};

export const deleteUser = async (id: number): Promise<void> => {
  try {
    await api.delete(`/admin/users/${id}`);
  } catch (error) {
    console.error(`Error deleting user with ID ${id}:`, error);
    throw error;
  }
};

export const getRoles = async (): Promise<Role[]> => {
  try {
    const response = await api.get('/admin/roles');
    return response.data;
  } catch (error) {
    console.error('Error fetching roles:', error);
    throw error;
  }
};

export const getRole = async (id: number): Promise<Role> => {
  try {
    const response = await api.get(`/admin/roles/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching role with ID ${id}:`, error);
    throw error;
  }
};

export const createRole = async (role: RoleCreate): Promise<Role> => {
  try {
    const response = await api.post('/admin/roles', role);
    return response.data;
  } catch (error) {
    console.error('Error creating role:', error);
    throw error;
  }
};

export const updateRole = async (id: number, role: RoleUpdate): Promise<Role> => {
  try {
    const response = await api.put(`/admin/roles/${id}`, role);
    return response.data;
  } catch (error) {
    console.error(`Error updating role with ID ${id}:`, error);
    throw error;
  }
};

export const deleteRole = async (id: number): Promise<void> => {
  try {
    await api.delete(`/admin/roles/${id}`);
  } catch (error) {
    console.error(`Error deleting role with ID ${id}:`, error);
    throw error;
  }
};

export const getPermissions = async (): Promise<Permission[]> => {
  try {
    const response = await api.get('/admin/permissions');
    return response.data;
  } catch (error) {
    console.error('Error fetching permissions:', error);
    throw error;
  }
};

export const getPermission = async (id: number): Promise<Permission> => {
  try {
    const response = await api.get(`/admin/permissions/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching permission with ID ${id}:`, error);
    throw error;
  }
};

export const createPermission = async (permission: PermissionCreate): Promise<Permission> => {
  try {
    const response = await api.post('/admin/permissions', permission);
    return response.data;
  } catch (error) {
    console.error('Error creating permission:', error);
    throw error;
  }
};

export const updatePermission = async (id: number, permission: PermissionUpdate): Promise<Permission> => {
  try {
    const response = await api.put(`/admin/permissions/${id}`, permission);
    return response.data;
  } catch (error) {
    console.error(`Error updating permission with ID ${id}:`, error);
    throw error;
  }
};

export const deletePermission = async (id: number): Promise<void> => {
  try {
    await api.delete(`/admin/permissions/${id}`);
  } catch (error) {
    console.error(`Error deleting permission with ID ${id}:`, error);
    throw error;
  }
};

export const getUserAuditLogs = async (userId?: number): Promise<AuditRecord[]> => {
  try {
    const url = userId 
      ? `/admin/users/${userId}/audit-logs` 
      : `/admin/users/audit-logs`;
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching audit logs:', error);
    throw error;
  }
};
