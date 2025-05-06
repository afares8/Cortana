export interface InvoiceItem {
  id: number;
  invoice_id: number;
  tariff_code: string;
  description: string;
  quantity: number;
  unit: string;
  weight: number;
  value: number;
  volume?: number;
  created_at: string;
  updated_at: string;
}

export interface InvoiceRecord {
  id: number;
  user_id: number;
  submission_id?: number;
  upload_date: string;
  invoice_number: string;
  invoice_date: string;
  client_name: string;
  client_id: string;
  movement_type: string;
  total_value: number;
  total_weight: number;
  status: string;
  validation_errors?: Record<string, any>;
  ai_suggestions?: string[];
  is_consolidated: boolean;
  consolidated_into_id?: number;
  original_invoice_ids?: number[];
  items: InvoiceItem[];
  created_at: string;
  updated_at: string;
}

export interface TrafficSubmission {
  id: number;
  user_id: number;
  submission_date: string;
  movement_type: string;
  client_name: string;
  client_id: string;
  total_value: number;
  total_weight: number;
  total_items: number;
  dmce_number?: string;
  status: string;
  error_message?: string;
  is_consolidated: boolean;
  original_invoice_ids?: number[];
  invoice_records: InvoiceRecord[];
  created_at: string;
  updated_at: string;
}

export interface InvoiceDataUpload {
  data: {
    invoice_number: string;
    invoice_date: string;
    client_name: string;
    client_id: string;
    movement_type: string;
    total_value: number;
    total_weight: number;
    items: {
      tariff_code: string;
      description: string;
      quantity: number;
      unit: string;
      weight: number;
      value: number;
      volume?: number;
    }[];
  };
}

export interface ConsolidationRequest {
  invoice_record_ids: number[];
}

export interface ConsolidationResponse {
  success: boolean;
  consolidated_record: InvoiceRecord;
  message: string;
}

export interface SubmissionRequest {
  record_id: number;
}

export interface SubmissionResponse {
  success: boolean;
  submission_id: number;
  dmce_number?: string;
  message: string;
}

export interface DMCELoginResponse {
  success: boolean;
  message: string;
  error?: string;
  loginUrl?: string;
  sessionId?: string;
}
