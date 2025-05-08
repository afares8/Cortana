import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from 'react-router-dom';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { DownloadIcon, AlertTriangleIcon, ExternalLinkIcon } from "lucide-react";
import { getComplianceDashboard, downloadUafReport } from "@/lib/api/compliance";
import { useTranslation } from 'react-i18next';

interface ComplianceMetric {
  label: string;
  value: number;
  status: 'success' | 'warning' | 'danger';
  icon?: string;
}

interface RecentVerification {
  id: string;
  client_name: string;
  verification_date: string;
  result: string;
  risk_level: string;
  report_path?: string;
}

interface ListUpdate {
  list_name: string;
  update_date: string;
  status: string;
}

interface ComplianceDashboardWidgetProps {
  title?: string;
  description?: string;
}

const ComplianceDashboardWidget: React.FC<ComplianceDashboardWidgetProps> = ({ 
  title = "Compliance Dashboard", 
  description = "Overview of compliance metrics and pending actions" 
}) => {
  const { t } = useTranslation();
  const [metrics, setMetrics] = useState<ComplianceMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const [recentVerifications, setRecentVerifications] = useState<RecentVerification[]>([]);
  const [listUpdates, setListUpdates] = useState<ListUpdate[]>([]);
  const [highRiskAlerts, setHighRiskAlerts] = useState<RecentVerification[]>([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await getComplianceDashboard();
        
        if (response) {
          const transformedMetrics: ComplianceMetric[] = [
            {
              label: 'Active Contracts',
              value: response.active_contracts || 0,
              status: 'success',
              icon: '📄'
            },
            {
              label: 'Expiring Soon',
              value: response.expiring_contracts || 0,
              status: response.expiring_contracts > 5 ? 'warning' : 'success',
              icon: '⏱️'
            },
            {
              label: 'PEP Matches',
              value: response.pep_matches || 0,
              status: response.pep_matches > 0 ? 'danger' : 'success',
              icon: '👤'
            },
            {
              label: 'Sanctions Matches',
              value: response.sanctions_matches || 0,
              status: response.sanctions_matches > 0 ? 'danger' : 'success',
              icon: '🚫'
            },
            {
              label: 'Pending Reports',
              value: response.pending_reports || 0,
              status: response.pending_reports > 3 ? 'warning' : 'success',
              icon: '📊'
            },
            {
              label: 'High Risk Clients',
              value: response.high_risk_clients || 0,
              status: response.high_risk_clients > 10 ? 'danger' : 'warning',
              icon: '⚠️'
            }
          ];
          
          setMetrics(transformedMetrics);
          
          const verifications = response.recent_verifications || [];
          setRecentVerifications(verifications);
          
          const highRiskItems = verifications.filter(v => 
            v.risk_level.toLowerCase() === 'high' || 
            v.result.toLowerCase().includes('match')
          );
          setHighRiskAlerts(highRiskItems);
          
          setListUpdates(response.recent_list_updates || []);
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
        
        const mockVerifications = [
          { id: '1', client_name: 'Acme Corp', verification_date: '2025-05-01T10:30:00Z', result: 'No Match', risk_level: 'LOW', report_path: '/reports/1.pdf' },
          { id: '2', client_name: 'TechStart Inc', verification_date: '2025-05-02T14:15:00Z', result: 'Match Found', risk_level: 'HIGH', report_path: '/reports/2.pdf' },
          { id: '3', client_name: 'Global Trading LLC', verification_date: '2025-05-03T09:45:00Z', result: 'No Match', risk_level: 'MEDIUM', report_path: '/reports/3.pdf' },
          { id: '4', client_name: 'Nicolás Maduro Moros', verification_date: '2025-05-08T08:30:00Z', result: 'Match Found', risk_level: 'HIGH', report_path: '/reports/4.pdf' }
        ];
        
        setRecentVerifications(mockVerifications);
        
        const highRiskItems = mockVerifications.filter(v => 
          v.risk_level.toLowerCase() === 'high' || 
          v.result.toLowerCase().includes('match')
        );
        setHighRiskAlerts(highRiskItems);
        
        setListUpdates([
          { list_name: 'OFAC', update_date: '2025-05-01T00:00:00Z', status: 'Success' },
          { list_name: 'EU Sanctions', update_date: '2025-05-01T00:00:00Z', status: 'Success' },
          { list_name: 'UN Sanctions', update_date: '2025-05-01T00:00:00Z', status: 'Success' },
          { list_name: 'OpenSanctions', update_date: '2025-05-01T00:00:00Z', status: 'Success' }
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

  const handleDownloadReport = async (reportId: string) => {
    try {
      const blob = await downloadUafReport(reportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `uaf-report-${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading report:', err);
      setError('Failed to download report');
    }
  };

  const getRiskLevelBadge = (level: string) => {
    const lowerLevel = level.toLowerCase();
    if (lowerLevel === 'high') return <Badge className="bg-red-100 text-red-800">HIGH</Badge>;
    if (lowerLevel === 'medium') return <Badge className="bg-yellow-100 text-yellow-800">MEDIUM</Badge>;
    return <Badge className="bg-green-100 text-green-800">LOW</Badge>;
  };

  const renderHighRiskAlerts = () => {
    if (highRiskAlerts.length === 0) return null;
    
    return (
      <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
        <div className="flex items-center mb-3">
          <AlertTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
          <h3 className="text-lg font-medium text-red-800">
            {t('compliance.highRiskAlerts', 'High Risk Alerts')}
          </h3>
        </div>
        
        <div className="space-y-3">
          {highRiskAlerts.map((alert, index) => (
            <div key={index} className="flex items-center justify-between p-3 border border-red-200 rounded bg-white">
              <div className="flex-1">
                <div className="font-medium">{alert.client_name}</div>
                <div className="text-sm text-gray-500">
                  {new Date(alert.verification_date).toLocaleDateString()}
                </div>
                <div className="mt-1 flex items-center">
                  {getRiskLevelBadge(alert.risk_level)}
                  <span className="ml-2 text-sm">{alert.result}</span>
                </div>
              </div>
              <div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => handleDownloadReport(alert.id)}
                  className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                >
                  <ExternalLinkIcon className="h-4 w-4" />
                  <span>{t('compliance.viewDetails', 'View Details')}</span>
                </Button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-3 text-sm text-red-700 font-medium">
          {t('compliance.warning', 'Warning')}: {t('compliance.highRiskWarning', 'These entities require immediate review and enhanced due diligence.')}
        </div>
      </div>
    );
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
          <div className="space-y-6">
            {/* High Risk Alerts Section */}
            {renderHighRiskAlerts()}
            
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
            
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-2">Recent Verifications</h3>
              <div className="border rounded-md overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Client</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Result</TableHead>
                      <TableHead>Risk Level</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {recentVerifications.map((verification) => (
                      <TableRow key={verification.id}>
                        <TableCell>{verification.client_name}</TableCell>
                        <TableCell>{new Date(verification.verification_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Badge className={verification.result.includes('Match') ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}>
                            {verification.result}
                          </Badge>
                        </TableCell>
                        <TableCell>{getRiskLevelBadge(verification.risk_level)}</TableCell>
                        <TableCell>
                          {verification.report_path && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => handleDownloadReport(verification.id)}
                              className="flex items-center gap-1"
                            >
                              <DownloadIcon className="h-4 w-4" />
                              <span>UAF</span>
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
            
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-2">Sanctions List Updates</h3>
              <div className="border rounded-md overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>List</TableHead>
                      <TableHead>Last Updated</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {listUpdates.map((update, index) => (
                      <TableRow key={index}>
                        <TableCell>{update.list_name}</TableCell>
                        <TableCell>{new Date(update.update_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Badge className={update.status === 'Success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                            {update.status}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button 
          variant="outline" 
          onClick={() => handleNavigate('/compliance/uaf-report')}
        >
          {t('compliance.generateUAFReport', 'Generate UAF Report')}
        </Button>
        <Button 
          variant="outline" 
          onClick={() => handleNavigate('/compliance/sanctions-screening')}
        >
          {t('compliance.runSanctionsScreening', 'Sanctions Screening')}
        </Button>
        <Button 
          variant="outline"
          onClick={() => handleNavigate('/compliance/verify-customer')}
        >
          {t('compliance.verifyCustomer', 'Customer Verification')}
        </Button>
        <div className="flex gap-2">
          <Button 
            variant="outline"
            onClick={() => handleNavigate('/compliance/country-risk-map')}
          >
            {t('compliance.viewRiskMap', 'View Risk Map')}
          </Button>
          <Button 
            onClick={() => handleNavigate('/compliance/dashboard')}
          >
            {t('compliance.viewFullDashboard', 'View Full Dashboard')}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};

export default ComplianceDashboardWidget;
