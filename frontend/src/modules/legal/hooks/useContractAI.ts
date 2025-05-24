import { useState } from 'react';
import axios from 'axios';
import { ContractAnalysisResult, LegalQAResponse } from '../types';

export function useContractAI() {
  const [result, setResult] = useState<ContractAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (text: string, analysisType: string = 'extract_clauses', specificQuery?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const apiUrl = import.meta.env?.VITE_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/legal/contracts/analyze`, {
        contract_text: text,
        analysis_type: analysisType,
        specific_query: specificQuery
      });
      
      setResult(response.data);
      return response.data;
    } catch (error) {
      console.error('Contract analysis error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed';
      setError(errorMessage);
      setResult({ error: errorMessage });
      return { error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const askLegalQuestion = async (prompt: string): Promise<LegalQAResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const apiUrl = import.meta.env?.VITE_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/legal/ask`, { prompt });
      return response.data;
    } catch (error) {
      console.error('Legal QA error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Question failed';
      setError(errorMessage);
      return { response: '', error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  return { 
    result, 
    loading, 
    error, 
    analyze, 
    askLegalQuestion 
  };
}
