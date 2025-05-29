import React, { useEffect, useRef } from 'react';
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
              
              if (countryData && countryData.client_data && countryData.client_data.total_clients > 0) {
                console.log(`Country ${countryCode} has ${countryData.client_data.total_clients} clients with risk level ${countryData.risk_level}`);
                
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
              }
              
              return {
                fillColor,
                weight: 1,
                opacity: 1,
                color: 'white',
                fillOpacity: 0.7
              };
            },
            onEachFeature: (feature, layer) => {
              const tooltipIsoMapping: Record<string, string> = {
                'VEN': 'VE',  // Venezuela
                'RUS': 'RU',  // Russia
                'IRN': 'IR',  // Iran
                'PRK': 'KP',  // North Korea
                'SYR': 'SY',  // Syria
                'BLR': 'BY',  // Belarus
                'IDN': 'ID',  // Indonesia
                'USA': 'US',  // United States
                'GBR': 'GB',  // United Kingdom
                'DEU': 'DE',  // Germany
                'FRA': 'FR',  // France
                'ESP': 'ES',  // Spain
                'ITA': 'IT',  // Italy
                'CHN': 'CN',  // China
                'JPN': 'JP',  // Japan
                'CAN': 'CA',  // Canada
                'AUS': 'AU',  // Australia
                'BRA': 'BR',  // Brazil
                'IND': 'IN',  // India
                'MEX': 'MX',  // Mexico
              };
              
              const geoJsonCode = feature?.properties?.['ISO3166-1-Alpha-3'] || feature?.properties?.['ISO3166-1-Alpha-2'];
              const countryName = feature?.properties?.name || 'Unknown';
              const countryCode = tooltipIsoMapping[geoJsonCode] || geoJsonCode;
              const countryData = countryCode ? data.countries[countryCode] : null;
              
              let popupContent = `<b>${countryName}</b>`;
              
              if (countryData) {
                popupContent += `<br>Risk Level: <b>${countryData.risk_level}</b>`;
                
                if (countryData.client_data) {
                  const clientData = countryData.client_data;
                  popupContent += `<br><br><b>Client Information:</b>`;
                  popupContent += `<br>Total Clients: <b>${clientData.total_clients}</b>`;
                  
                  if (clientData.total_clients > 0) {
                    popupContent += `<br>High Risk Clients: ${clientData.high_risk_clients}`;
                    popupContent += `<br>Medium Risk Clients: ${clientData.medium_risk_clients}`;
                    popupContent += `<br>Low Risk Clients: ${clientData.low_risk_clients}`;
                    
                    if (countryData.basel_score) {
                      popupContent += `<br>Risk Score: ${countryData.basel_score}`;
                    }
                  }
                }
                
                if (countryData.fatf_status) {
                  popupContent += `<br>FATF Status: ${countryData.fatf_status}`;
                }
                if (countryData.eu_high_risk) {
                  popupContent += '<br>EU High-Risk: Yes';
                }
                if (countryData.basel_rank) {
                  popupContent += `<br>Basel Rank: ${countryData.basel_rank}`;
                }
                if (countryData.last_updated) {
                  popupContent += `<br>Last Updated: ${new Date(countryData.last_updated).toLocaleDateString()}`;
                }
              } else {
                popupContent += '<br>No risk data available';
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
