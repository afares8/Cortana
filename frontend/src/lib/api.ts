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
  console.log('Using mock contracts data');
  
  const mockContracts: Contract[] = [
    {
      id: 1,
      title: 'Service Agreement with Acme Corp',
      client_name: 'Acme Corporation',
      contract_type: 'Service Agreement',
      start_date: '2025-01-15',
      expiration_date: '2026-01-14',
      responsible_lawyer: 'Jane Smith',
      description: 'Annual service agreement for IT consulting services',
      status: 'active',
      file_path: '/uploads/contract1.pdf',
      created_at: '2025-01-10T10:30:00Z',
      updated_at: '2025-01-10T10:30:00Z'
    },
    {
      id: 2,
      title: 'NDA with TechStart Inc',
      client_name: 'TechStart Inc',
      contract_type: 'Non-Disclosure Agreement',
      start_date: '2025-02-01',
      expiration_date: '2025-05-01',
      responsible_lawyer: 'John Doe',
      description: 'NDA for potential partnership discussions',
      status: 'active',
      file_path: '/uploads/contract2.pdf',
      created_at: '2025-01-25T14:15:00Z',
      updated_at: '2025-01-25T14:15:00Z'
    },
    {
      id: 3,
      title: 'Lease Agreement for Office Space',
      client_name: 'Commercial Properties LLC',
      contract_type: 'Lease Agreement',
      start_date: '2024-12-01',
      expiration_date: '2025-05-15',
      responsible_lawyer: 'Jane Smith',
      description: 'Lease for satellite office in downtown',
      status: 'active',
      file_path: '/uploads/contract3.pdf',
      created_at: '2024-11-15T09:45:00Z',
      updated_at: '2024-11-15T09:45:00Z'
    }
  ];
  
  let filteredContracts = [...mockContracts];
  
  if (filters) {
    if (filters.client_name) {
      filteredContracts = filteredContracts.filter(c => 
        c.client_name.toLowerCase().includes(filters.client_name.toLowerCase())
      );
    }
    
    if (filters.contract_type) {
      filteredContracts = filteredContracts.filter(c => 
        c.contract_type.toLowerCase().includes(filters.contract_type.toLowerCase())
      );
    }
    
    if (filters.responsible_lawyer) {
      filteredContracts = filteredContracts.filter(c => 
        c.responsible_lawyer.toLowerCase().includes(filters.responsible_lawyer.toLowerCase())
      );
    }
    
    if (filters.status) {
      filteredContracts = filteredContracts.filter(c => c.status === filters.status);
    }
  }
  
  return filteredContracts;
};

export const getContract = async (id: number): Promise<Contract> => {
  console.log(`Using mock contract data for ID: ${id}`);
  
  const mockContracts = await getContracts();
  const contract = mockContracts.find(c => c.id === id);
  
  if (!contract) {
    throw new Error('Contract not found');
  }
  
  return contract;
};

export const createContract = async (data: FormData): Promise<Contract> => {
  console.log('Using mock create contract data');
  
  const mockContracts = await getContracts();
  const newId = Math.max(...mockContracts.map(c => c.id)) + 1;
  
  const newContract: Contract = {
    id: newId,
    title: data.get('title') as string || 'New Contract',
    client_name: data.get('client_name') as string || 'New Client',
    contract_type: data.get('contract_type') as string || 'General Agreement',
    start_date: data.get('start_date') as string || new Date().toISOString().split('T')[0],
    expiration_date: data.get('expiration_date') as string || new Date(Date.now() + 31536000000).toISOString().split('T')[0],
    responsible_lawyer: data.get('responsible_lawyer') as string || 'John Doe',
    description: data.get('description') as string || '',
    status: 'active',
    file_path: '/uploads/new-contract.pdf',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
  
  return newContract;
};

export const updateContract = async (id: number, data: Partial<Contract>): Promise<Contract> => {
  console.log(`Using mock update contract data for ID: ${id}`);
  
  const contract = await getContract(id);
  
  const updatedContract: Contract = {
    ...contract,
    ...data,
    updated_at: new Date().toISOString()
  };
  
  return updatedContract;
};

export const deleteContract = async (id: number): Promise<Contract> => {
  console.log(`Using mock delete contract data for ID: ${id}`);
  
  const contract = await getContract(id);
  return contract;
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
