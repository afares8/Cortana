import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useContractAI } from '../hooks/useContractAI';
import DueDiligencePanel from '../components/DueDiligencePanel';
import { LegalQAResponse } from '../types';

const LegalDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [contracts, setContracts] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { askLegalQuestion } = useContractAI();
  const [legalQuestion, setLegalQuestion] = useState('');
  const [legalResponse, setLegalResponse] = useState<LegalQAResponse | null>(null);
  const [askingQuestion, setAskingQuestion] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const apiUrl = process.env.REACT_APP_API_URL || '';
        
        const contractsResponse = await axios.get(`${apiUrl}/api/v1/legal/contracts`);
        setContracts(contractsResponse.data);
        
        const clientsResponse = await axios.get(`${apiUrl}/api/v1/legal/clients`);
        setClients(clientsResponse.data);
      } catch (error) {
        console.error('Dashboard data error:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  const handleAskQuestion = async () => {
    if (!legalQuestion.trim()) return;
    
    setAskingQuestion(true);
    try {
      const response = await askLegalQuestion(legalQuestion);
      setLegalResponse(response);
    } catch (error) {
      console.error('Error asking legal question:', error);
    } finally {
      setAskingQuestion(false);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('Legal Dashboard 2.0')}</h1>
        <div className="flex space-x-2">
          <button 
            className="px-4 py-2 bg-blue-500 text-white rounded"
            onClick={() => navigate('/legal/contracts/new')}
          >
            {t('New Contract')}
          </button>
          <button 
            className="px-4 py-2 bg-blue-500 text-white rounded"
            onClick={() => navigate('/legal/clients/new')}
          >
            {t('New Client')}
          </button>
        </div>
      </div>
      
      <div className="w-full">
        <div className="flex mb-4 border-b">
          <button 
            className={`px-4 py-2 ${activeTab === 'overview' ? 'border-b-2 border-blue-500' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            {t('Overview')}
          </button>
          <button 
            className={`px-4 py-2 ${activeTab === 'ai-tools' ? 'border-b-2 border-blue-500' : ''}`}
            onClick={() => setActiveTab('ai-tools')}
          >
            {t('AI Tools')}
          </button>
          <button 
            className={`px-4 py-2 ${activeTab === 'due-diligence' ? 'border-b-2 border-blue-500' : ''}`}
            onClick={() => setActiveTab('due-diligence')}
          >
            {t('Due Diligence')}
          </button>
        </div>
        
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border rounded shadow p-4">
              <div className="border-b pb-2 mb-4">
                <h2 className="text-lg font-semibold">{t('Recent Contracts')}</h2>
              </div>
              <div>
                {loading ? (
                  <p>{t('Loading...')}</p>
                ) : contracts.length > 0 ? (
                  <ul className="space-y-2">
                    {contracts.slice(0, 5).map((contract: any) => (
                      <li key={contract.id} className="p-2 hover:bg-gray-100 rounded cursor-pointer" 
                          onClick={() => navigate(`/legal/contracts/${contract.id}`)}>
                        {contract.title}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>{t('No contracts found')}</p>
                )}
              </div>
            </div>
            
            <div className="border rounded shadow p-4">
              <div className="border-b pb-2 mb-4">
                <h2 className="text-lg font-semibold">{t('Recent Clients')}</h2>
              </div>
              <div>
                {loading ? (
                  <p>{t('Loading...')}</p>
                ) : clients.length > 0 ? (
                  <ul className="space-y-2">
                    {clients.slice(0, 5).map((client: any) => (
                      <li key={client.id} className="p-2 hover:bg-gray-100 rounded cursor-pointer"
                          onClick={() => navigate(`/legal/clients/${client.id}`)}>
                        {client.name}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>{t('No clients found')}</p>
                )}
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'ai-tools' && (
          <div className="grid grid-cols-1 gap-6">
            <div className="border rounded shadow p-4">
              <div className="border-b pb-2 mb-4">
                <h2 className="text-lg font-semibold">{t('Legal Assistant')}</h2>
              </div>
              <div className="space-y-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="flex-1 p-2 border rounded"
                    placeholder={t('Ask a legal question...')}
                    value={legalQuestion}
                    onChange={(e) => setLegalQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
                  />
                  <button 
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                    onClick={handleAskQuestion} 
                    disabled={askingQuestion}
                  >
                    {askingQuestion ? t('Asking...') : t('Ask')}
                  </button>
                </div>
                
                {legalResponse && (
                  <div className="p-4 border rounded bg-gray-50">
                    <h3 className="font-semibold mb-2">{t('Response:')}</h3>
                    <p>{legalResponse.response || legalResponse.error}</p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="border rounded shadow p-4">
              <div className="border-b pb-2 mb-4">
                <h2 className="text-lg font-semibold">{t('Contract Analysis Tools')}</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button 
                  className="px-4 py-2 bg-blue-500 text-white rounded"
                  onClick={() => navigate('/legal/contracts/analyze')}
                >
                  {t('Extract Clauses')}
                </button>
                <button 
                  className="px-4 py-2 bg-blue-500 text-white rounded"
                  onClick={() => navigate('/legal/contracts/analyze')}
                >
                  {t('legal.calculateRiskScore')}
                </button>
                <button 
                  className="px-4 py-2 bg-blue-500 text-white rounded"
                  onClick={() => navigate('/legal/contracts/analyze')}
                >
                  {t('Detect Anomalies')}
                </button>
                <button 
                  className="px-4 py-2 bg-blue-500 text-white rounded"
                  onClick={() => navigate('/legal/contracts/analyze')}
                >
                  {t('Suggest Rewrites')}
                </button>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'due-diligence' && (
          <DueDiligencePanel />
        )}
      </div>
    </div>
  );
};

export default LegalDashboard;
