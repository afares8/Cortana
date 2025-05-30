import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { RefreshCw } from 'lucide-react';
import Heatmap from '../components/maps/Heatmap';

interface CountryRiskData {
  name: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  sources: string[];
  basel_score?: number;
  basel_rank?: number;
  fatf_status?: string;
  eu_high_risk?: boolean;
  country_code?: string;
  client_data?: {
    total_clients: number;
    high_risk_clients: number;
    medium_risk_clients: number;
    low_risk_clients: number;
    clients: Array<{
      id: number;
      name: string;
      risk_score: number;
    }>;
  };
}

interface CountryRisk {
  countries: Record<string, CountryRiskData>;
  metadata: {
    is_simulated: boolean;
    country_count: number;
    data_sources: string[];
    validation_status: string;
  };
  last_updated: string;
}

interface RiskAnalysis {
  analysis: string;
  global_risk_score: number;
  recommended_score: number;
  high_risk_countries_with_clients: string[];
  timestamp: string;
  data_sources: string[];
}

const CountryRiskMap: React.FC = () => {
  const { t } = useTranslation();
  const [countryRiskData, setCountryRiskData] = useState<CountryRisk | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<RiskAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState<boolean>(false);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);
  const lastDataRef = useRef<CountryRisk | null>(null);

  const fetchCountryRiskData = async () => {
    try {
      setLoading(true);
      const apiUrl = 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/api/v1/compliance/country-risk`);
      const newData = response.data;
      
      if (!lastDataRef.current || JSON.stringify(newData) !== JSON.stringify(lastDataRef.current)) {
        console.log('Country risk data changed, updating and triggering analysis');
        setCountryRiskData(newData);
        lastDataRef.current = newData;
        setError(null);
        await generateAnalysis();
      } else {
        console.log('Country risk data unchanged, skipping analysis');
        setLoading(false);
      }
    } catch (err) {
      console.error('Error fetching country risk data:', err);
      setError('Failed to load country risk data. Please try again later.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCountryRiskData();
    
    const refreshInterval = setInterval(() => {
      if (autoRefresh) {
        fetchCountryRiskData();
      }
    }, 30000);
    
    return () => clearInterval(refreshInterval);
  }, [autoRefresh]);
  
  const generateAnalysis = async () => {
    try {
      setAnalysisLoading(true);
      const apiUrl = 'http://localhost:8000';
      const response = await axios.post(`${apiUrl}/api/v1/compliance/country-risk/analysis`);
      setAnalysis(response.data);
    } catch (err) {
      console.error('Error generating risk analysis:', err);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-PA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[80vh]">
        <div className="animate-spin">⏳</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <strong>Error: </strong>
        <span>{error}</span>
      </div>
    );
  }

  if (!countryRiskData) {
    return (
      <div className="p-3 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
        <span>⚠️ {t('compliance.noRiskData')}</span>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          {t('compliance.countryRiskMap')}
        </h1>
        <div className="text-sm text-muted-foreground">
          {t('compliance.lastUpdated')}: {formatDate(countryRiskData.last_updated)}
        </div>
      </div>

      {countryRiskData.metadata?.is_simulated && (
        <div className="mb-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          <span className="font-bold">⚠️ {t('compliance.warning')}: </span>
          <span>{t('compliance.simulatedDataWarning')}</span>
        </div>
      )}

      <div className="mb-4 bg-white shadow rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">{t('compliance.riskMapSummary')}</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-2 border rounded">
            <div className="text-2xl font-bold">{countryRiskData.metadata?.country_count || 0}</div>
            <div className="text-sm text-gray-600">{t('compliance.countriesAnalyzed')}</div>
          </div>
          <div className="text-center p-2 border rounded">
            <div className="text-2xl font-bold text-red-600">
              {Object.values(countryRiskData.countries).filter(c => c.risk_level === 'HIGH').length}
            </div>
            <div className="text-sm text-gray-600">{t('compliance.highRiskCountries')}</div>
          </div>
          <div className="text-center p-2 border rounded">
            <div className="text-2xl font-bold text-yellow-600">
              {Object.values(countryRiskData.countries).filter(c => c.risk_level === 'MEDIUM').length}
            </div>
            <div className="text-sm text-gray-600">{t('compliance.mediumRiskCountries')}</div>
          </div>
          <div className="text-center p-2 border rounded">
            <div className="text-2xl font-bold text-green-600">
              {Object.values(countryRiskData.countries).filter(c => c.risk_level === 'LOW').length}
            </div>
            <div className="text-sm text-gray-600">{t('compliance.lowRiskCountries')}</div>
          </div>
        </div>
      </div>

      <div className="h-[600px] w-full">
        <Heatmap 
          data={countryRiskData ? {
            last_updated: countryRiskData.last_updated,
            countries: Object.entries(countryRiskData.countries).reduce((acc, [code, data]) => {
              acc[code] = {
                ...data,
                country_code: code,
                risk_level: (typeof data.risk_level === 'string' 
                  ? data.risk_level.toUpperCase() 
                  : data.risk_level) as 'LOW' | 'MEDIUM' | 'HIGH'
              };
              return acc;
            }, {} as Record<string, any>)
          } : undefined}
          loading={loading}
          error={error ? error : undefined}
          height={600}
        />
      </div>

      <div className="mt-4 text-sm text-muted-foreground">
        <div><strong>{t('compliance.dataSources')}:</strong> {countryRiskData.metadata?.data_sources.join(', ')}</div>
        <div><strong>{t('compliance.validationStatus')}:</strong> {countryRiskData.metadata?.validation_status}</div>
      </div>
      
      {/* AI Analysis Section */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">{t('compliance.aiAnalysis')}</h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Auto-refresh:</label>
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  autoRefresh ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    autoRefresh ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            <button 
              onClick={generateAnalysis}
              disabled={analysisLoading}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors disabled:opacity-50"
              aria-label={t('compliance.refreshAnalysis')}
            >
              <RefreshCw size={16} className={analysisLoading ? 'animate-spin' : ''} />
              <span>{t('compliance.refreshAnalysis')}</span>
            </button>
          </div>
        </div>
        
        {analysisLoading ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : analysis ? (
          <div>
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <div className="text-sm text-gray-500">
                  {t('compliance.generatedOn')} {formatDate(analysis.timestamp)}
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-medium mr-2">{t('compliance.globalRiskScore')}:</span>
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    analysis.global_risk_score > analysis.recommended_score 
                      ? 'bg-red-100 text-red-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {analysis.global_risk_score.toFixed(1)} / {analysis.recommended_score.toFixed(1)}
                  </span>
                </div>
              </div>
              
              <div className="prose max-w-none">
                <p>{analysis.analysis}</p>
              </div>
              
              {analysis.high_risk_countries_with_clients.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">{t('compliance.highRiskCountriesWithClients')}:</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.high_risk_countries_with_clients.map((country, index) => (
                      <span key={index} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                        {country}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="mt-4 text-xs text-gray-500">
                <div>{t('compliance.dataSources')}: {analysis.data_sources.join(', ')}</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 p-8 rounded-md text-center">
            <p className="text-gray-500">{t('compliance.analysisWillAppear')}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CountryRiskMap;
