import { useState } from 'react';
import axios from 'axios';

const API_URL = typeof import.meta === 'object' && 'env' in import.meta 
  ? import.meta.env.VITE_API_URL || 'http://localhost:8000'
  : 'http://localhost:8000';

interface EntityBase {
  name: string;
  dob?: string;
  country: string;
  type: 'natural' | 'legal';
}

interface CustomerVerifyRequest {
  customer: EntityBase;
  directors?: EntityBase[];
  ubos?: EntityBase[];
}

interface VerificationMatch {
  source: string;
  source_id: string;
  name: string;
  match_type: string;
  score: number;
  details: Record<string, any>;
}

interface VerificationResult {
  status: string;
  matches: VerificationMatch[];
  source: string;
  timestamp: string;
}

export interface ComplianceCheckResponse {
  pep: VerificationResult;
  ofac: VerificationResult;
  un: VerificationResult;
  eu: VerificationResult;
  uk?: VerificationResult;
  local?: VerificationResult;
  wikidata?: VerificationResult;
  enriched_data: Record<string, any>;
  verification_id: string;
  created_at: string;
}

export const useComplianceCheck = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ComplianceCheckResponse | null>(null);

  const checkCompliance = async (data: CustomerVerifyRequest): Promise<ComplianceCheckResponse | null> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post<ComplianceCheckResponse>(
        `${API_URL}/api/v1/compliance/verify-customer`, 
        data
      );
      
      setResult(response.data);
      return response.data;
    } catch (err) {
      console.error('Error performing compliance check:', err);
      setError('Failed to perform compliance check. Please try again later.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    result,
    checkCompliance
  };
};
