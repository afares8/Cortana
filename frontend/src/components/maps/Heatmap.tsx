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
    if (data && leafletMap.current) {
      leafletMap.current.eachLayer((layer) => {
        if (layer instanceof L.GeoJSON) {
          leafletMap.current?.removeLayer(layer);
        }
      });

      fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson')
        .then(response => response.json())
        .then(geoJson => {
          L.geoJSON(geoJson, {
            style: (feature) => {
              const countryCode = feature?.properties?.ISO_A2;
              const countryData = countryCode ? data.countries[countryCode] : null;
              
              let fillColor = '#cccccc'; // Default color for countries without data
              
              if (countryData) {
                switch (countryData.risk_level) {
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
              
              return {
                fillColor,
                weight: 1,
                opacity: 1,
                color: 'white',
                fillOpacity: 0.7
              };
            },
            onEachFeature: (feature, layer) => {
              const countryCode = feature?.properties?.ISO_A2;
              const countryName = feature?.properties?.ADMIN || 'Unknown';
              const countryData = countryCode ? data.countries[countryCode] : null;
              
              let popupContent = `<b>${countryName}</b>`;
              
              if (countryData) {
                popupContent += `
                  <br>Risk Level: <b>${countryData.risk_level}</b>
                  ${countryData.fatf_status ? `<br>FATF Status: ${countryData.fatf_status}` : ''}
                  ${countryData.eu_high_risk ? '<br>EU High-Risk: Yes' : ''}
                  ${countryData.basel_score ? `<br>Basel AML Index: ${countryData.basel_score}` : ''}
                  ${countryData.basel_rank ? `<br>Basel Rank: ${countryData.basel_rank}` : ''}
                  ${countryData.last_updated ? `<br>Last Updated: ${new Date(countryData.last_updated).toLocaleDateString()}` : ''}
                `;
              } else {
                popupContent += '<br>No risk data available';
              }
              
              layer.bindPopup(popupContent);
            }
          }).addTo(leafletMap.current!);
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
