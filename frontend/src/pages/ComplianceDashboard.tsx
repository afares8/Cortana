import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert } from "@/components/ui/alert";
import { AlertCircle, AlertTriangle, Loader2, FileDown } from "lucide-react";
import { API_BASE_URL } from "../constants";

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

interface DashboardData {
  active_contracts: number;
  expiring_contracts: number;
  pep_matches: number;
  sanctions_matches: number;
  pending_reports: number;
  high_risk_clients: number;
  recent_verifications: RecentVerification[];
  recent_list_updates: ListUpdate[];
}

const ComplianceDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const apiUrl = import.meta.env.VITE_API_URL || '';
        const response = await axios.get(`${apiUrl}/api/v1/compliance/dashboard`);
        setDashboardData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching compliance dashboard data:', err);
        setError(t('compliance.loadError'));
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    const intervalId = setInterval(fetchDashboardData, 300000);
    
    return () => clearInterval(intervalId);
  }, []);

  const [generatingReport, setGeneratingReport] = useState<boolean>(false);
  const [verifyingCustomer, setVerifyingCustomer] = useState<boolean>(false);
  const [runningPEPScreening, setRunningPEPScreening] = useState<boolean>(false);
  const [runningSanctionsScreening, setRunningSanctionsScreening] = useState<boolean>(false);
  
  const handleGenerateUAFReport = async () => {
    try {
      setGeneratingReport(true);
      
      const response = await fetch(`${API_BASE_URL}/compliance/uaf-reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: 1, // Default to first client for dashboard action
          start_date: new Date(Date.now() - 30*24*60*60*1000).toISOString(), // Last 30 days
          end_date: new Date().toISOString()
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate UAF report');
      }
      
      const report = await response.json();
      
      if (report.id) {
        window.open(`${API_BASE_URL}/compliance/reports/${report.id}/download`, '_blank');
      } else {
        navigate('/compliance/uaf-report/new');
      }
    } catch (error) {
      console.error('Error generating UAF report:', error);
      navigate('/compliance/uaf-report/new');
    } finally {
      setGeneratingReport(false);
    }
  };

  const handleRunPEPScreening = async () => {
    try {
      setRunningPEPScreening(true);
      
      const response = await fetch(`${API_BASE_URL}/compliance/pep-screening`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: "Test Customer",
          country: "PA"
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to run PEP screening');
      }
      
      const result = await response.json();
      console.log('PEP screening result:', result);
      
      const fetchDashboardData = async () => {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || '';
          const response = await axios.get(`${apiUrl}/api/v1/compliance/dashboard`);
          setDashboardData(response.data);
        } catch (err) {
          console.error('Error refreshing dashboard data:', err);
        }
      };
      fetchDashboardData();
      
    } catch (error) {
      console.error('Error running PEP screening:', error);
      navigate('/compliance/pep-screening/new');
    } finally {
      setRunningPEPScreening(false);
    }
  };

  const handleRunSanctionsScreening = async () => {
    try {
      setRunningSanctionsScreening(true);
      
      const response = await fetch(`${API_BASE_URL}/compliance/sanctions-screening`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: "Test Customer",
          country: "PA"
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to run sanctions screening');
      }
      
      const result = await response.json();
      console.log('Sanctions screening result:', result);
      
      const fetchDashboardData = async () => {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || '';
          const response = await axios.get(`${apiUrl}/api/v1/compliance/dashboard`);
          setDashboardData(response.data);
        } catch (err) {
          console.error('Error refreshing dashboard data:', err);
        }
      };
      fetchDashboardData();
      
    } catch (error) {
      console.error('Error running sanctions screening:', error);
      navigate('/compliance/sanctions-screening/new');
    } finally {
      setRunningSanctionsScreening(false);
    }
  };

  const handleCustomerVerification = async () => {
    try {
      setVerifyingCustomer(true);
      
      const response = await fetch(`${API_BASE_URL}/compliance/verify-customer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer: {
            name: "Test Customer",
            country: "PA",
            type: "natural"
          }
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to verify customer');
      }
      
      const result = await response.json();
      console.log('Verification result:', result);
      
      const fetchDashboardData = async () => {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || '';
          const response = await axios.get(`${apiUrl}/api/v1/compliance/dashboard`);
          setDashboardData(response.data);
        } catch (err) {
          console.error('Error refreshing dashboard data:', err);
        }
      };
      fetchDashboardData();
      
    } catch (error) {
      console.error('Error verifying customer:', error);
      navigate('/compliance/verify-customer');
    } finally {
      setVerifyingCustomer(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-PA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'draft': return 'secondary';
      case 'submitted': return 'warning';
      case 'approved': return 'default';
      case 'rejected': return 'destructive';
      case 'potential_match': return 'secondary';
      case 'confirmed_match': return 'destructive';
      case 'no_match': return 'default';
      default: return 'secondary';
    }
  };
  
  const renderStatusBadge = (status: string) => (
    <Badge variant={getStatusBadgeVariant(status) as "default" | "secondary" | "destructive" | "outline"}>
      {status.replace('_', ' ')}
    </Badge>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[80vh]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3">
        <Alert>
          <AlertCircle className="h-4 w-4 mr-2" />
          {error}
        </Alert>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="p-3">
        <Alert>
          <AlertTriangle className="h-4 w-4 mr-2" />
          {t('compliance.noDashboardData')}
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          {t('compliance.dashboard')}
        </h1>
        <div className="flex space-x-2">
          <Button 
            variant="default"
            onClick={handleGenerateUAFReport}
            disabled={generatingReport}
          >
            {generatingReport ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t('compliance.generating')}
              </>
            ) : (
              <>
                <FileDown className="h-4 w-4 mr-2" />
                {t('compliance.generateUAFReport')}
              </>
            )}
          </Button>
          <Button 
            variant="outline"
            onClick={handleRunPEPScreening}
            disabled={runningPEPScreening}
          >
            {runningPEPScreening ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t('compliance.running')}
              </>
            ) : (
              t('compliance.runPEPScreening')
            )}
          </Button>
          <Button 
            variant="outline"
            onClick={handleRunSanctionsScreening}
            disabled={runningSanctionsScreening}
          >
            {runningSanctionsScreening ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t('compliance.running')}
              </>
            ) : (
              t('compliance.runSanctionsScreening')
            )}
          </Button>
          <Button 
            variant="outline"
            onClick={handleCustomerVerification}
            disabled={verifyingCustomer}
          >
            {verifyingCustomer ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t('compliance.verifying')}
              </>
            ) : (
              t('compliance.verifyCustomer')
            )}
          </Button>
          <Button 
            variant="outline"
            onClick={() => navigate('/compliance/country-risk-map')}
          >
            {t('compliance.viewRiskMap')}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Metrics Summary */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>{t('compliance.reports')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.active_contracts}</div>
                  <div className="text-sm text-muted-foreground">{t('compliance.activeContracts')}</div>
                </div>
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.pending_reports}</div>
                  <div className="text-sm text-muted-foreground">{t('compliance.pending')}</div>
                </div>
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.expiring_contracts}</div>
                  <div className="text-sm text-muted-foreground">{t('compliance.expiring')}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Screenings Summary */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>{t('compliance.screeningResults')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.pep_matches}</div>
                  <div className="text-sm text-muted-foreground">{t('compliance.pepMatches')}</div>
                </div>
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.sanctions_matches}</div>
                  <div className="text-sm text-muted-foreground">{t('compliance.sanctionsMatches')}</div>
                </div>
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.high_risk_clients}</div>
                  <div className="text-sm text-muted-foreground">{t('compliance.highRiskClients')}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Verifications */}
        <div className="col-span-1 md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>{t('compliance.recentVerifications')}</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {dashboardData.recent_verifications.map((verification, index) => (
                    <div key={`verification-${verification.id}`}>
                      {index > 0 && <Separator className="my-2" />}
                      <div 
                        className="p-2 hover:bg-accent rounded-md cursor-pointer"
                        onClick={() => {
                          navigate(`/compliance/verify-customer`);
                        }}
                      >
                        <div className="flex items-center">
                          <span className="mr-2">
                            {verification.result.includes('Match') ? '⚠️' : '✅'}
                          </span>
                          <span className="font-medium">
                            {verification.client_name}
                          </span>
                          <Badge 
                            variant={verification.risk_level.toLowerCase() === 'high' ? 'destructive' : 
                                   verification.risk_level.toLowerCase() === 'medium' ? 'secondary' : 'default'}
                            className="ml-2"
                          >
                            {verification.risk_level}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">
                          <span className="font-medium">
                            {renderStatusBadge(verification.result)}
                          </span>
                          {" — "}
                          {formatDate(verification.verification_date)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
        
        {/* List Updates */}
        <div className="col-span-1 md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>{t('compliance.sanctionsListUpdates')}</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {dashboardData.recent_list_updates.map((update, index) => (
                    <div key={`update-${index}`}>
                      {index > 0 && <Separator className="my-2" />}
                      <div className="p-2 rounded-md">
                        <div className="flex items-center">
                          <span className="mr-2">
                            {update.status === 'Success' ? '✅' : '❌'}
                          </span>
                          <span className="font-medium">
                            {update.list_name}
                          </span>
                          <Badge 
                            variant={update.status === 'Success' ? 'default' : 'destructive'}
                            className="ml-2"
                          >
                            {update.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">
                          {formatDate(update.update_date)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ComplianceDashboard;
