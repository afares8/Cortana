import React, { useState } from 'react';
import axios from 'axios';
import { DueDiligenceResponse } from '../types';

const DueDiligencePanel: React.FC = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    passport: '',
    country: ''
  });
  const [result, setResult] = useState<DueDiligenceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const apiUrl = process.env.REACT_APP_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/legal/verify-client`, formData);
      setResult(response.data);
    } catch (err) {
      console.error('Verification error:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'clear':
        return <span className="px-2 py-1 rounded bg-green-500 text-white">Clear</span>;
      case 'flagged':
        return <span className="px-2 py-1 rounded bg-red-500 text-white">Flagged</span>;
      case 'error':
        return <span className="px-2 py-1 rounded bg-yellow-500 text-white">Error</span>;
      default:
        return <span className="px-2 py-1 rounded bg-gray-500 text-white">{status}</span>;
    }
  };

  const getRiskBadge = (score: number) => {
    if (score < 0.3) return <span className="px-2 py-1 rounded bg-green-500 text-white">Low Risk</span>;
    if (score < 0.7) return <span className="px-2 py-1 rounded bg-yellow-500 text-white">Medium Risk</span>;
    return <span className="px-2 py-1 rounded bg-red-500 text-white">High Risk</span>;
  };

  return (
    <div className="w-full border rounded shadow p-4">
      <div className="border-b pb-2 mb-4">
        <h2 className="text-lg font-semibold">Due Diligence Verification</h2>
      </div>
      <div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="full_name" className="block text-sm font-medium">Full Name</label>
            <input
              id="full_name"
              type="text"
              className="w-full p-2 border rounded"
              placeholder="John Doe"
              value={formData.full_name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, full_name: e.target.value})}
              required
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="passport" className="block text-sm font-medium">Passport/ID</label>
            <input
              id="passport"
              type="text"
              className="w-full p-2 border rounded"
              placeholder="A123456"
              value={formData.passport}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, passport: e.target.value})}
              required
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="country" className="block text-sm font-medium">Country</label>
            <input
              id="country"
              type="text"
              className="w-full p-2 border rounded"
              placeholder="US"
              value={formData.country}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, country: e.target.value})}
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="w-full px-4 py-2 bg-blue-500 text-white rounded" 
            disabled={loading}
          >
            {loading ? 'Verifying...' : 'Verify Client'}
          </button>
        </form>
        
        {error && (
          <div className="mt-4 p-4 border border-red-500 bg-red-50 rounded">
            <h3 className="text-red-700 font-semibold">Error</h3>
            <p className="text-red-600">{error}</p>
          </div>
        )}
        
        {result && (
          <div className="mt-6 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Verification Results</h3>
              <div className="flex space-x-2">
                {getStatusBadge(result.status)}
                {getRiskBadge(result.risk_score)}
              </div>
            </div>
            
            <div className="border rounded p-4">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-sm text-gray-500">Name</p>
                  <p>{result.full_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Passport/ID</p>
                  <p>{result.passport}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Country</p>
                  <p>{result.country}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Verification Date</p>
                  <p>{new Date(result.verification_date).toLocaleString()}</p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2">Screening Results</h4>
              
              <div className="space-y-4">
                <div>
                  <h5 className="font-medium">OFAC Sanctions</h5>
                  {result.results.OFAC && result.results.OFAC.length > 0 ? (
                    <ul className="list-disc pl-5">
                      {result.results.OFAC.map((match, index) => (
                        <li key={index} className="text-red-500">
                          {match.name} (Score: {match.score})
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-green-500">No matches found</p>
                  )}
                </div>
                
                <div>
                  <h5 className="font-medium">UN Sanctions</h5>
                  {result.results.UN && result.results.UN.length > 0 ? (
                    <ul className="list-disc pl-5">
                      {result.results.UN.map((match, index) => (
                        <li key={index} className="text-red-500">
                          {match.name} (Score: {match.score})
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-green-500">No matches found</p>
                  )}
                </div>
                
                <div>
                  <h5 className="font-medium">EU Sanctions</h5>
                  {result.results.EU && result.results.EU.length > 0 ? (
                    <ul className="list-disc pl-5">
                      {result.results.EU.map((match, index) => (
                        <li key={index} className="text-red-500">
                          {match.name} (Score: {match.score})
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-green-500">No matches found</p>
                  )}
                </div>
                
                <div>
                  <h5 className="font-medium">PEP Status</h5>
                  {result.results.PEP && result.results.PEP.length > 0 ? (
                    <ul className="list-disc pl-5">
                      {result.results.PEP.map((match, index) => (
                        <li key={index} className="text-yellow-500">
                          {match.name} (Score: {match.score})
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-green-500">No matches found</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DueDiligencePanel;
