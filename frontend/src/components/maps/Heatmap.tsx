import React, { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface CountryRisk {
  name: string;
  country_code: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  fatf_status?: string;
  eu_high_risk: boolean;
  basel_score?: number;
  basel_rank?: number;
  last_updated?: string;
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

interface RiskMapData {
  last_updated: string;
  countries: Record<string, CountryRisk>;
}

interface HeatmapProps {
  data?: RiskMapData;
  loading?: boolean;
  error?: string;
  height?: string | number;
}

const Heatmap: React.FC<HeatmapProps> = ({ 
  data, 
  loading = false, 
  error = '', 
  height = 400 
}) => {
  const { t } = useTranslation();
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletMap = useRef<L.Map | null>(null);

  useEffect(() => {
    if (mapRef.current && !leafletMap.current) {
      leafletMap.current = L.map(mapRef.current).setView([20, 0], 2);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(leafletMap.current);
    }

    return () => {
      if (leafletMap.current) {
        leafletMap.current.remove();
        leafletMap.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (data && mapRef.current) {
      if (!leafletMap.current) {
        leafletMap.current = L.map(mapRef.current).setView([20, 0], 2);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(leafletMap.current);
      }
      
      leafletMap.current.eachLayer((layer) => {
        if (layer instanceof L.GeoJSON) {
          leafletMap.current?.removeLayer(layer);
        }
      });

      fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson')
        .then(response => response.json())
        .then(geoJson => {
          if (!leafletMap.current) return;
          
          const geoJsonLayer = L.geoJSON(geoJson, {
            style: (feature) => {
              const isoMapping: Record<string, string> = {
                'VEN': 'VE',  // Venezuela
                'COL': 'CO',  // Colombia
                'PAN': 'PA',  // Panama
                'BOL': 'BO',  // Bolivia
                'ARG': 'AR',  // Argentina
                'CHL': 'CL',  // Chile
                'PER': 'PE',  // Peru
                'ECU': 'EC',  // Ecuador
                'URY': 'UY',  // Uruguay
                'PRY': 'PY',  // Paraguay
                'CRI': 'CR',  // Costa Rica
                'GTM': 'GT',  // Guatemala
                'HND': 'HN',  // Honduras
                'SLV': 'SV',  // El Salvador
                'NIC': 'NI',  // Nicaragua
                'DOM': 'DO',  // Dominican Republic
                'HTI': 'HT',  // Haiti
                'JAM': 'JM',  // Jamaica
                'CUB': 'CU',  // Cuba
                'BRA': 'BR',  // Brazil
                'MEX': 'MX',  // Mexico
                'USA': 'US',  // United States
                'CAN': 'CA',  // Canada
                'RUS': 'RU',  // Russia
                'IRN': 'IR',  // Iran
                'PRK': 'KP',  // North Korea
                'SYR': 'SY',  // Syria
                'BLR': 'BY',  // Belarus
              };
              
              const geoJsonCode = feature?.properties?.['ISO3166-1-Alpha-3'] || feature?.properties?.['ISO3166-1-Alpha-2'];
              const countryCode = isoMapping[geoJsonCode] || geoJsonCode;
              
              const countryData = countryCode ? data.countries[countryCode] : null;
              
              // Default color for countries without data or clients
              let fillColor = '#cccccc'; 
              
              if (geoJsonCode === 'VEN' || countryCode === 'VE') {
                console.log('Venezuela found:', {
                  geoJsonCode,
                  mappedCode: countryCode,
                  hasData: !!countryData,
                  name: feature?.properties?.ADMIN,
                  clientData: countryData?.client_data
                });
              }
              
              if (countryData) {
                let hasClients = countryData.client_data && countryData.client_data.total_clients > 0;
                
                if (hasClients) {
                  console.log(`Country ${countryCode} has ${countryData.client_data?.total_clients} clients with risk level ${countryData.risk_level}`);
                }
                
                if (countryData.basel_score) {
                  if (countryData.basel_score >= 8.0) {
                    fillColor = '#ef4444'; // Red - High risk
                  } else if (countryData.basel_score >= 5.0) {
                    fillColor = '#f97316'; // Orange - Medium risk
                  } else {
                    fillColor = '#22c55e'; // Green - Low risk
                  }
                } 
                else {
                  const riskLevel = typeof countryData.risk_level === 'string' 
                    ? countryData.risk_level.toUpperCase() 
                    : String(countryData.risk_level).toUpperCase();
                  
                  switch (riskLevel) {
                    case 'HIGH':
                      fillColor = '#ef4444'; // Red
                      break;
                    case 'MEDIUM':
                      fillColor = '#f97316'; // Orange
                      break;
                    case 'LOW':
                      fillColor = '#22c55e'; // Green
                      break;
                  }
                }
                
                if (hasClients) {
                  return {
                    fillColor,
                    weight: 2,
                    opacity: 1,
                    color: 'black',
                    fillOpacity: 0.8,
                    dashArray: '3'
                  };
                }
              }
              
              // Default return for all countries
              return {
                fillColor,
                weight: 1,
                opacity: 1,
                color: 'white',
                fillOpacity: countryData ? 0.7 : 0.3
              };
            },
            onEachFeature: (feature, layer) => {
              const tooltipIsoMapping: Record<string, string> = {
                'VEN': 'VE',  // Venezuela
                'COL': 'CO',  // Colombia
                'PAN': 'PA',  // Panama
                'BOL': 'BO',  // Bolivia
                'ARG': 'AR',  // Argentina
                'CHL': 'CL',  // Chile
                'PER': 'PE',  // Peru
                'ECU': 'EC',  // Ecuador
                'URY': 'UY',  // Uruguay
                'PRY': 'PY',  // Paraguay
                'CRI': 'CR',  // Costa Rica
                'GTM': 'GT',  // Guatemala
                'HND': 'HN',  // Honduras
                'SLV': 'SV',  // El Salvador
                'NIC': 'NI',  // Nicaragua
                'DOM': 'DO',  // Dominican Republic
                'HTI': 'HT',  // Haiti
                'JAM': 'JM',  // Jamaica
                'CUB': 'CU',  // Cuba
                'BRA': 'BR',  // Brazil
                'MEX': 'MX',  // Mexico
                'USA': 'US',  // United States
                'CAN': 'CA',  // Canada
                'GUY': 'GY',  // Guyana
                'SUR': 'SR',  // Suriname
                'BLZ': 'BZ',  // Belize
                'RUS': 'RU',  // Russia
                'IRN': 'IR',  // Iran
                'PRK': 'KP',  // North Korea
                'SYR': 'SY',  // Syria
                'BLR': 'BY',  // Belarus
                'IDN': 'ID',  // Indonesia
                'GBR': 'GB',  // United Kingdom
                'DEU': 'DE',  // Germany
                'FRA': 'FR',  // France
                'ESP': 'ES',  // Spain
                'ITA': 'IT',  // Italy
                'CHN': 'CN',  // China
                'JPN': 'JP',  // Japan
                'AUS': 'AU',  // Australia
                'IND': 'IN',  // India
              };
              
              const geoJsonCode = feature?.properties?.['ISO3166-1-Alpha-3'] || feature?.properties?.['ISO3166-1-Alpha-2'];
              const countryName = feature?.properties?.name || 'Unknown';
              const countryCode = tooltipIsoMapping[geoJsonCode] || geoJsonCode;
              const countryData = countryCode ? data.countries[countryCode] : null;
              
              let popupContent = `<b>${countryName}</b>`;
              
              if (countryData) {
                popupContent += `<br>${t('heatmap.riskLevel')}: <b>${countryData.risk_level}</b>`;
                
                if (countryData.client_data) {
                  const clientData = countryData.client_data;
                  popupContent += `<br><br><b>${t('heatmap.clientInfo')}</b>`;
                  popupContent += `<br>${t('heatmap.totalClients')}: <b>${clientData.total_clients}</b>`;
                  
                  if (clientData.total_clients > 0) {
                    popupContent += `<br>${t('heatmap.highRiskClients')}: ${clientData.high_risk_clients}`;
                    popupContent += `<br>${t('heatmap.mediumRiskClients')}: ${clientData.medium_risk_clients}`;
                    popupContent += `<br>${t('heatmap.lowRiskClients')}: ${clientData.low_risk_clients}`;
                    
                    if (countryData.basel_score) {
                      popupContent += `<br>${t('heatmap.riskScore')}: ${countryData.basel_score}`;
                    }
                  }
                }
                
                if (countryData.fatf_status) {
                  popupContent += `<br>${t('heatmap.fatfStatus')}: ${countryData.fatf_status}`;
                }
                if (countryData.eu_high_risk) {
                  popupContent += `<br>${t('heatmap.euHighRisk')}: Yes`;
                }
                if (countryData.basel_rank) {
                  popupContent += `<br>${t('heatmap.baselRank')}: ${countryData.basel_rank}`;
                }
                if (countryData.last_updated) {
                  popupContent += `<br>${t('heatmap.lastUpdated')}: ${new Date(countryData.last_updated).toLocaleDateString()}`;
                }
              } else {
                popupContent += `<br>${t('heatmap.noData')}`;
              }
              
              layer.bindPopup(popupContent);
            }
          });
          
          if (leafletMap.current) {
            geoJsonLayer.addTo(leafletMap.current);
          }
        })
        .catch(err => {
          console.error('Error loading GeoJSON:', err);
        });
    }
  }, [data]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full border border-gray-200 rounded-md" style={{ height }}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-full border border-gray-200 rounded-md" style={{ height }}>
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div 
      ref={mapRef} 
      className="border border-gray-200 rounded-md" 
      style={{ height, width: '100%' }}
    />
  );
};

export default Heatmap;
