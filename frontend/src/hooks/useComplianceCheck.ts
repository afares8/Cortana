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
  name: string;
  score: number;
  details: Record<string, any>;
  source_id?: string;
  match_type?: string;
}

interface VerificationResult {
  status: string;
  matches: VerificationMatch[];
  source?: string;
  timestamp?: string;
}

export interface ComplianceCheckResponse {
  customer: {
    name: string;
    enriched_data: Record<string, any>;
    pep_matches: VerificationMatch[];
    sanctions_matches: VerificationMatch[];
    risk_score: number;
  };
  directors: Array<any>;
  ubos: Array<any>;
  country_risk: {
    country_code: string;
    name: string;
    risk_level: string;
    sources: string[];
    notes?: string;
    last_updated: string;
  };
  report: {
    id: number;
    path: string;
    generated_at: string;
  };
  sources_checked: string[];
}

export const useComplianceCheck = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  const checkCompliance = async (data: CustomerVerifyRequest): Promise<ComplianceCheckResponse | null> => {
    try {
      setLoading(true);
      setError(null);
      setResult(null); // Reset result before new request
      
      console.log('Sending compliance check request:', data);
      
      const response = await axios.post<ComplianceCheckResponse>(
        `${API_URL}/api/v1/compliance/verify-customer`, 
        data
      );
      
      console.log('Received compliance check response:', response.data);
      
      const transformedResult = {
        pep: {
          status: response.data.customer.pep_matches.length > 0 ? 'matched' : 'clear',
          matches: response.data.customer.pep_matches,
          source: 'PEP Lists',
          timestamp: new Date().toISOString()
        },
        ofac: {
          status: response.data.customer.sanctions_matches.some(m => m.source.includes('OFAC')) ? 'matched' : 'clear',
          matches: response.data.customer.sanctions_matches.filter(m => m.source.includes('OFAC')),
          source: 'OFAC',
          timestamp: new Date().toISOString()
        },
        un: {
          status: response.data.customer.sanctions_matches.some(m => m.source.includes('UN')) ? 'matched' : 'clear',
          matches: response.data.customer.sanctions_matches.filter(m => m.source.includes('UN')),
          source: 'UN',
          timestamp: new Date().toISOString()
        },
        eu: {
          status: response.data.customer.sanctions_matches.some(m => m.source.includes('EU')) ? 'matched' : 'clear',
          matches: response.data.customer.sanctions_matches.filter(m => m.source.includes('EU')),
          source: 'EU',
          timestamp: new Date().toISOString()
        },
        enriched_data: response.data.customer.enriched_data,
        verification_id: response.data.report.id.toString(),
        created_at: response.data.report.generated_at
      };
      
      console.log('Transformed result:', transformedResult);
      setResult(transformedResult);
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
