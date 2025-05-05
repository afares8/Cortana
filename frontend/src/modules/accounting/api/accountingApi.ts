import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

import { 
  Company, 
  CompanyCreate, 
  CompanyUpdate,
  TaxType,
  TaxTypeCreate,
  TaxTypeUpdate,
  Obligation,
  ObligationCreate,
  ObligationUpdate,
  Payment,
  PaymentCreate,
  PaymentUpdate,
  Attachment,
  AttachmentCreate
} from '../types';

export const getCompanies = async (params?: { 
  skip?: number; 
  limit?: number;
  name?: string;
  location?: string;
  is_zona_libre?: boolean;
}): Promise<Company[]> => {
  const response = await axios.get(`${API_BASE}/accounting/companies`, { params });
  return response.data;
};

export const getCompany = async (id: number): Promise<Company> => {
  const response = await axios.get(`${API_BASE}/accounting/companies/${id}`);
  return response.data;
};

export const createCompany = async (company: CompanyCreate): Promise<Company> => {
  const response = await axios.post(`${API_BASE}/accounting/companies`, company);
  return response.data;
};

export const updateCompany = async (id: number, company: CompanyUpdate): Promise<Company> => {
  const response = await axios.put(`${API_BASE}/accounting/companies/${id}`, company);
  return response.data;
};

export const deleteCompany = async (id: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_BASE}/accounting/companies/${id}`);
  return response.data;
};

export const getTaxTypes = async (params?: { 
  skip?: number; 
  limit?: number;
  name?: string;
  authority?: string;
}): Promise<TaxType[]> => {
  const response = await axios.get(`${API_BASE}/accounting/tax-types`, { params });
  return response.data;
};

export const getTaxType = async (id: number): Promise<TaxType> => {
  const response = await axios.get(`${API_BASE}/accounting/tax-types/${id}`);
  return response.data;
};

export const createTaxType = async (taxType: TaxTypeCreate): Promise<TaxType> => {
  const response = await axios.post(`${API_BASE}/accounting/tax-types`, taxType);
  return response.data;
};

export const updateTaxType = async (id: number, taxType: TaxTypeUpdate): Promise<TaxType> => {
  const response = await axios.put(`${API_BASE}/accounting/tax-types/${id}`, taxType);
  return response.data;
};

export const deleteTaxType = async (id: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_BASE}/accounting/tax-types/${id}`);
  return response.data;
};

export const getObligations = async (params?: { 
  skip?: number; 
  limit?: number;
  company_id?: number;
  tax_type_id?: number;
  status?: string;
  frequency?: string;
  due_before?: string;
}): Promise<Obligation[]> => {
  const response = await axios.get(`${API_BASE}/accounting/obligations`, { params });
  return response.data;
};

export const getObligation = async (id: number): Promise<Obligation> => {
  const response = await axios.get(`${API_BASE}/accounting/obligations/${id}`);
  return response.data;
};

export const createObligation = async (obligation: ObligationCreate): Promise<Obligation> => {
  const response = await axios.post(`${API_BASE}/accounting/obligations`, obligation);
  return response.data;
};

export const updateObligation = async (id: number, obligation: ObligationUpdate): Promise<Obligation> => {
  const response = await axios.put(`${API_BASE}/accounting/obligations/${id}`, obligation);
  return response.data;
};

export const deleteObligation = async (id: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_BASE}/accounting/obligations/${id}`);
  return response.data;
};

export const getPayments = async (params?: { 
  skip?: number; 
  limit?: number;
  obligation_id?: number;
  payment_date_from?: string;
  payment_date_to?: string;
}): Promise<Payment[]> => {
  const response = await axios.get(`${API_BASE}/accounting/payments`, { params });
  return response.data;
};

export const getPayment = async (id: number): Promise<Payment> => {
  const response = await axios.get(`${API_BASE}/accounting/payments/${id}`);
  return response.data;
};

export const createPayment = async (payment: PaymentCreate): Promise<Payment> => {
  const response = await axios.post(`${API_BASE}/accounting/payments`, payment);
  return response.data;
};

export const updatePayment = async (id: number, payment: PaymentUpdate): Promise<Payment> => {
  const response = await axios.put(`${API_BASE}/accounting/payments/${id}`, payment);
  return response.data;
};

export const deletePayment = async (id: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_BASE}/accounting/payments/${id}`);
  return response.data;
};

export const getAttachments = async (params?: { 
  skip?: number; 
  limit?: number;
  file_type?: string;
  uploaded_by?: string;
}): Promise<Attachment[]> => {
  const response = await axios.get(`${API_BASE}/accounting/attachments`, { params });
  return response.data;
};

export const getAttachment = async (id: number): Promise<Attachment> => {
  const response = await axios.get(`${API_BASE}/accounting/attachments/${id}`);
  return response.data;
};

export const createAttachment = async (attachment: AttachmentCreate): Promise<Attachment> => {
  const response = await axios.post(`${API_BASE}/accounting/attachments`, attachment);
  return response.data;
};

export const deleteAttachment = async (id: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_BASE}/accounting/attachments/${id}`);
  return response.data;
};
