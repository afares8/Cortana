import axios from 'axios';
import { API_BASE_URL } from '../../../constants';

export interface SearchResult {
  id: string;
  title: string;
  type: string;
  path: string;
  excerpt: string;
}

interface ContractResult {
  id: number;
  title: string;
  client_name: string;
  description: string;
}

interface ClientResult {
  id: number;
  name: string;
  description: string;
}

interface ComplianceReportResult {
  id: number;
  title: string;
  client_name: string;
  report_type: string;
  summary: string;
}

/**
 * Search across multiple entity types in the application
 * @param query Search query string
 * @returns Promise with aggregated search results
 */
export const searchAll = async (query: string): Promise<SearchResult[]> => {
  if (!query.trim()) {
    return [];
  }

  try {
    const results: SearchResult[] = [];
    const apiUrl = API_BASE_URL || '';
    
    try {
      const contractsResponse = await axios.get(`${apiUrl}/legal/contracts?search=${encodeURIComponent(query)}`);
      const contracts: ContractResult[] = contractsResponse.data || [];
      
      contracts.forEach(contract => {
        results.push({
          id: `contract-${contract.id}`,
          title: contract.title,
          type: 'contract',
          path: `/legal/contracts/${contract.id}`,
          excerpt: contract.description || `Contract with ${contract.client_name}`
        });
      });
    } catch (error) {
      console.error('Error searching contracts:', error);
    }
    
    try {
      const clientsResponse = await axios.get(`${apiUrl}/legal/clients?search=${encodeURIComponent(query)}`);
      const clients: ClientResult[] = clientsResponse.data || [];
      
      clients.forEach(client => {
        results.push({
          id: `client-${client.id}`,
          title: `Client: ${client.name}`,
          type: 'client',
          path: `/legal/clients/${client.id}`,
          excerpt: client.description || 'Client profile'
        });
      });
    } catch (error) {
      console.error('Error searching clients:', error);
    }
    
    try {
      const reportsResponse = await axios.get(`${apiUrl}/compliance/reports?search=${encodeURIComponent(query)}`);
      const reports: ComplianceReportResult[] = reportsResponse.data || [];
      
      reports.forEach(report => {
        results.push({
          id: `report-${report.id}`,
          title: report.title,
          type: 'compliance',
          path: `/compliance/reports/${report.id}`,
          excerpt: report.summary || `${report.report_type} report for ${report.client_name}`
        });
      });
    } catch (error) {
      console.error('Error searching compliance reports:', error);
    }
    
    return results;
  } catch (error) {
    console.error('Error performing search:', error);
    return [];
  }
};
