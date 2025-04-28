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
  const formData = new FormData();
  formData.append('username', data.username);
  formData.append('password', data.password);
  
  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const register = async (data: RegisterRequest): Promise<User> => {
  const response = await api.post('/auth/register', data);
  return response.data;
};

export const getContracts = async (filters?: Record<string, string>): Promise<Contract[]> => {
  const response = await api.get('/contracts', { params: filters });
  return response.data;
};

export const getContract = async (id: number): Promise<Contract> => {
  const response = await api.get(`/contracts/${id}`);
  return response.data;
};

export const createContract = async (data: FormData): Promise<Contract> => {
  const response = await api.post('/contracts', data, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const updateContract = async (id: number, data: Partial<Contract>): Promise<Contract> => {
  const response = await api.put(`/contracts/${id}`, data);
  return response.data;
};

export const deleteContract = async (id: number): Promise<Contract> => {
  const response = await api.delete(`/contracts/${id}`);
  return response.data;
};

export const getDashboardStats = async (): Promise<DashboardStats> => {
  console.log('Using mock dashboard stats data');
  return {
    total_active_contracts: 12,
    contracts_expiring_soon: 3,
    overdue_contracts: 1,
    total_contracts: 16
  };
};
