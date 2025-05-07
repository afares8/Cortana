import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface ComplianceMetric {
  label: string;
  value: number;
  status: 'success' | 'warning' | 'danger';
  icon?: string;
}

interface ComplianceDashboardWidgetProps {
  title?: string;
  description?: string;
}

const ComplianceDashboardWidget: React.FC<ComplianceDashboardWidgetProps> = ({ 
  title = "Compliance Dashboard", 
  description = "Overview of compliance metrics and pending actions" 
}) => {
  const [metrics, setMetrics] = useState<ComplianceMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const apiUrl = import.meta.env.VITE_API_URL || '';
        const response = await axios.get(`${apiUrl}/api/v1/compliance/dashboard`);
        
        if (response.data) {
          const transformedMetrics: ComplianceMetric[] = [
            {
              label: 'Active Contracts',
              value: response.data.active_contracts || 0,
              status: 'success',
              icon: '📄'
            },
            {
              label: 'Expiring Soon',
              value: response.data.expiring_contracts || 0,
              status: response.data.expiring_contracts > 5 ? 'warning' : 'success',
              icon: '⏱️'
            },
            {
              label: 'PEP Matches',
              value: response.data.pep_matches || 0,
              status: response.data.pep_matches > 0 ? 'danger' : 'success',
              icon: '👤'
            },
            {
              label: 'Sanctions Matches',
              value: response.data.sanctions_matches || 0,
              status: response.data.sanctions_matches > 0 ? 'danger' : 'success',
              icon: '🚫'
            },
            {
              label: 'Pending Reports',
              value: response.data.pending_reports || 0,
              status: response.data.pending_reports > 3 ? 'warning' : 'success',
              icon: '📊'
            },
            {
              label: 'High Risk Clients',
              value: response.data.high_risk_clients || 0,
              status: response.data.high_risk_clients > 10 ? 'danger' : 'warning',
              icon: '⚠️'
            }
          ];
          
          setMetrics(transformedMetrics);
        }
      } catch (err) {
        console.error('Error fetching compliance dashboard data:', err);
        setError('Failed to load compliance dashboard data');
        
        setMetrics([
          { label: 'Active Contracts', value: 42, status: 'success', icon: '📄' },
          { label: 'Expiring Soon', value: 7, status: 'warning', icon: '⏱️' },
          { label: 'PEP Matches', value: 2, status: 'danger', icon: '👤' },
          { label: 'Sanctions Matches', value: 1, status: 'danger', icon: '🚫' },
          { label: 'Pending Reports', value: 5, status: 'warning', icon: '📊' },
          { label: 'High Risk Clients', value: 12, status: 'danger', icon: '⚠️' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusColor = (status: 'success' | 'warning' | 'danger') => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'danger':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  return (
    <Card className="w-full shadow-md">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center items-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        ) : error ? (
          <div className="text-center text-red-500 p-4">{error}</div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {metrics.map((metric, index) => (
              <div 
                key={index} 
                className={`p-4 rounded-lg ${getStatusColor(metric.status)} flex flex-col items-center justify-center`}
              >
                <div className="text-2xl mb-1">{metric.icon}</div>
                <div className="text-2xl font-bold">{metric.value}</div>
                <div className="text-sm">{metric.label}</div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button 
          variant="outline" 
          onClick={() => handleNavigate('/compliance/uaf-report')}
        >
          Generate UAF Report
        </Button>
        <Button 
          variant="outline" 
          onClick={() => handleNavigate('/compliance/sanctions-screening')}
        >
          Sanctions Screening
        </Button>
        <Button 
          variant="outline"
          onClick={() => handleNavigate('/compliance/verify-customer')}
        >
          Customer Verification
        </Button>
        <Button 
          onClick={() => handleNavigate('/compliance/dashboard')}
        >
          View Full Dashboard
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ComplianceDashboardWidget;
