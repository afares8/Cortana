export interface Company {
  id: number;
  name: string;
  location: string;
  address?: string;
  contact_email?: string;
  contact_phone?: string;
  is_zona_libre: boolean;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface CompanyCreate {
  name: string;
  location: string;
  address?: string;
  contact_email?: string;
  contact_phone?: string;
  is_zona_libre: boolean;
  notes?: string;
}

export interface CompanyUpdate {
  name?: string;
  location?: string;
  address?: string;
  contact_email?: string;
  contact_phone?: string;
  is_zona_libre?: boolean;
  notes?: string;
}

export interface TaxType {
  id: number;
  name: string;
  authority: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface TaxTypeCreate {
  name: string;
  authority: string;
  description?: string;
}

export interface TaxTypeUpdate {
  name?: string;
  authority?: string;
  description?: string;
}

export interface Obligation {
  id: number;
  company_id: number;
  tax_type_id: number;
  name: string;
  description?: string;
  frequency: string; // monthly, quarterly, annual
  due_day: number;
  reminder_days: number;
  amount?: number;
  status: string; // pending, completed, overdue
  last_payment_date?: string;
  next_due_date: string;
  penalties?: Record<string, string | number>;
  created_at: string;
  updated_at?: string;
  company_name?: string;
  tax_type_name?: string;
}

export interface ObligationCreate {
  company_id: number;
  tax_type_id: number;
  name: string;
  description?: string;
  frequency: string;
  due_day: number;
  reminder_days?: number;
  amount?: number;
  status?: string;
  next_due_date: string;
  penalties?: Record<string, string | number>;
}

export interface ObligationUpdate {
  company_id?: number;
  tax_type_id?: number;
  name?: string;
  description?: string;
  frequency?: string;
  due_day?: number;
  reminder_days?: number;
  amount?: number;
  status?: string;
  next_due_date?: string;
  penalties?: Record<string, string | number>;
}

export interface Payment {
  id: number;
  obligation_id: number;
  amount: number;
  payment_date: string;
  receipt_number?: string;
  notes?: string;
  attachment_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface PaymentCreate {
  obligation_id: number;
  amount: number;
  payment_date: string;
  receipt_number?: string;
  notes?: string;
  attachment_id?: number;
}

export interface PaymentUpdate {
  amount?: number;
  payment_date?: string;
  receipt_number?: string;
  notes?: string;
  attachment_id?: number;
}

export interface Attachment {
  id: number;
  file_name: string;
  file_path: string;
  file_type: string;
  uploaded_by?: string;
  upload_date: string;
  created_at: string;
  updated_at?: string;
}

export interface AttachmentCreate {
  file_name: string;
  file_type: string;
  uploaded_by?: string;
  file_content: string; // Base64 encoded file content
}

export interface Notification {
  id: string;
  user_id: number;
  message: string;
  read: boolean;
  related_obligation_id?: string;
  created_at: string;
  updated_at?: string;
}
