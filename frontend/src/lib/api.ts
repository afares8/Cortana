import axios from 'axios';
import { Contract, DashboardStats, LoginRequest, LoginResponse, RegisterRequest, User } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  const params = new URLSearchParams();
  params.append('username', data.username);
  params.append('password', data.password);
  
  const response = await api.post('/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const register = async (data: RegisterRequest): Promise<User> => {
  const response = await api.post('/auth/register', data);
  return response.data;
};

export const getContracts = async (filters?: Record<string, string>): Promise<Contract[]> => {
  try {
    const queryParams = new URLSearchParams();
    
    if (filters) {
      if (filters.client_name) {
        queryParams.append('name', filters.client_name);
      }
      
      if (filters.contract_type) {
        queryParams.append('contract_type', filters.contract_type);
      }
      
      if (filters.responsible_lawyer) {
        queryParams.append('responsible_lawyer', filters.responsible_lawyer);
      }
      
      if (filters.status) {
        queryParams.append('status', filters.status);
      }
    }
    
    const queryString = queryParams.toString();
    const url = `/legal/contracts${queryString ? `?${queryString}` : ''}`;
    
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching contracts:', error);
    throw error;
  }
};

export const getContract = async (id: number): Promise<Contract> => {
  try {
    const response = await api.get(`/legal/contracts/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching contract with ID ${id}:`, error);
    throw error;
  }
};

export const createContract = async (data: FormData): Promise<Contract> => {
  try {
    const contractData = {
      title: data.get('title'),
      client_id: parseInt(data.get('client_id') as string),
      contract_type: data.get('contract_type'),
      start_date: data.get('start_date'),
      expiration_date: data.get('expiration_date'),
      responsible_lawyer: data.get('responsible_lawyer'),
      description: data.get('description'),
      status: 'active'
    };
    
    const response = await api.post('/legal/contracts', contractData);
    return response.data;
  } catch (error) {
    console.error('Error creating contract:', error);
    throw error;
  }
};

export const updateContract = async (id: number, data: Partial<Contract>): Promise<Contract> => {
  try {
    const response = await api.put(`/legal/contracts/${id}`, data);
    return response.data;
  } catch (error) {
    console.error(`Error updating contract with ID ${id}:`, error);
    throw error;
  }
};

export const deleteContract = async (id: number): Promise<{ success: boolean }> => {
  try {
    const response = await api.delete(`/legal/contracts/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting contract with ID ${id}:`, error);
    throw error;
  }
};

export const getDashboardStats = async (): Promise<DashboardStats> => {
  try {
    const response = await api.get('/compliance/dashboard');
    
    return {
      total_active_contracts: response.data.active_contracts || 0,
      contracts_expiring_soon: response.data.expiring_contracts || 0,
      overdue_contracts: response.data.flagged_clients || 0,
      total_contracts: response.data.total_screenings || 0
    };
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
};
