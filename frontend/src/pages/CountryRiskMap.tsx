import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import Heatmap from '../components/maps/Heatmap';

interface CountryRisk {
  countries: Record<string, {
    name: string;
    risk_level: string;
    sources: string[];
    basel_score?: number;
    basel_rank?: number;
    fatf_status?: string;
    eu_high_risk?: boolean;
  }>;
  metadata: {
    is_simulated: boolean;
    country_count: number;
    data_sources: string[];
    validation_status: string;
  };
  last_updated: string;
}

const CountryRiskMap: React.FC = () => {
  const { t } = useTranslation();
  const [countryRiskData, setCountryRiskData] = useState<CountryRisk | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCountryRiskData = async () => {
      try {
        setLoading(true);
        const apiUrl = 'http://localhost:8000';
        const response = await axios.get(`${apiUrl}/api/v1/compliance/country-risk`);
        setCountryRiskData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching country risk data:', err);
        setError('Failed to load country risk data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCountryRiskData();
  }, []);

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
              {Object.values(countryRiskData.countries).filter(c => c.risk_level === 'high').length}
            </div>
            <div className="text-sm text-gray-600">{t('compliance.highRiskCountries')}</div>
          </div>
          <div className="text-center p-2 border rounded">
            <div className="text-2xl font-bold text-yellow-600">
              {Object.values(countryRiskData.countries).filter(c => c.risk_level === 'medium').length}
            </div>
            <div className="text-sm text-gray-600">{t('compliance.mediumRiskCountries')}</div>
          </div>
          <div className="text-center p-2 border rounded">
            <div className="text-2xl font-bold text-green-600">
              {Object.values(countryRiskData.countries).filter(c => c.risk_level === 'low').length}
            </div>
            <div className="text-sm text-gray-600">{t('compliance.lowRiskCountries')}</div>
          </div>
        </div>
      </div>

      <div className="h-[600px] w-full">
        <Heatmap 
          data={countryRiskData ? {
            last_updated: countryRiskData.last_updated,
            countries: countryRiskData.countries
          } : undefined}
          loading={loading}
          error={error}
          height={600}
        />
      </div>

      <div className="mt-4 text-sm text-muted-foreground">
        <div><strong>{t('compliance.dataSources')}:</strong> {countryRiskData.metadata?.data_sources.join(', ')}</div>
        <div><strong>{t('compliance.validationStatus')}:</strong> {countryRiskData.metadata?.validation_status}</div>
      </div>
    </div>
  );
};

export default CountryRiskMap;
