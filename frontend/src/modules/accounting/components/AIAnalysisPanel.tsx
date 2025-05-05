import React, { useState } from 'react';
import { AIAnalysisRequest, AIAnalysisResponse, analyzeObligations } from '../api/accountingApi';
import { Company } from '../types';
import { BrainCircuit, Loader2 } from 'lucide-react';

interface AIAnalysisPanelProps {
  companies: Company[];
}

const AIAnalysisPanel: React.FC<AIAnalysisPanelProps> = ({ companies }) => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [companyId, setCompanyId] = useState<number | null>(companies[0]?.id || null);
  const [months, setMonths] = useState<number>(6);
  const [language, setLanguage] = useState<string>('es');
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!companyId) {
      setError('Please select a company');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const request: AIAnalysisRequest = {
        company_id: companyId,
        months,
        language
      };
      
      const response = await analyzeObligations(request);
      setAnalysisResult(response.analysis);
    } catch (err) {
      setError('Error analyzing obligations. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 mt-6">
      <div className="flex items-center mb-4">
        <div className="p-3 rounded-full bg-indigo-100 text-indigo-600 mr-4">
          <BrainCircuit className="h-6 w-6" />
        </div>
        <h2 className="text-xl font-semibold">AI Analysis</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company
          </label>
          <select
            className="w-full p-2 border border-gray-300 rounded-md"
            value={companyId || ''}
            onChange={(e) => setCompanyId(Number(e.target.value) || null)}
          >
            <option value="">Select a company</option>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Months to analyze
          </label>
          <select
            className="w-full p-2 border border-gray-300 rounded-md"
            value={months}
            onChange={(e) => setMonths(Number(e.target.value))}
          >
            <option value={3}>3 months</option>
            <option value={6}>6 months</option>
            <option value={12}>12 months</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Language
          </label>
          <select
            className="w-full p-2 border border-gray-300 rounded-md"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="es">Spanish</option>
            <option value="en">English</option>
          </select>
        </div>
        
        <div className="flex items-end">
          <button
            className="w-full p-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 flex items-center justify-center gap-2"
            onClick={handleAnalyze}
            disabled={isLoading || !companyId}
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <BrainCircuit className="h-5 w-5" />
                <span>Run Analysis</span>
              </>
            )}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded-md mb-4">
          {error}
        </div>
      )}
      
      {analysisResult && (
        <div className="bg-gray-50 p-4 rounded-md prose max-w-none">
          <h3 className="text-lg font-medium mb-2">Analysis Results</h3>
          <div className="whitespace-pre-line">
            {analysisResult}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAnalysisPanel;
