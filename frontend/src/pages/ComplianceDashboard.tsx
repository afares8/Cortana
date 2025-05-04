import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert } from "@/components/ui/alert";
import { AlertCircle, AlertTriangle, Loader2 } from "lucide-react";

interface DashboardData {
  reports: {
    total: number;
    pending: number;
    submitted: number;
    approved: number;
    rejected: number;
    by_type: Record<string, number>;
  };
  screenings: {
    pep: {
      total: number;
      matches: number;
      match_percentage: number;
    };
    sanctions: {
      total: number;
      matches: number;
      match_percentage: number;
    };
  };
  recent_activity: Array<{
    type: string;
    id: number;
    created_at: string;
    [key: string]: any;
  }>;
}

const ComplianceDashboard: React.FC = () => {
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
        setError('Failed to load compliance dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    const intervalId = setInterval(fetchDashboardData, 300000);
    
    return () => clearInterval(intervalId);
  }, []);

  const handleGenerateUAFReport = () => {
    navigate('/compliance/uaf-report/new');
  };

  const handleRunPEPScreening = () => {
    navigate('/compliance/pep-screening/new');
  };

  const handleRunSanctionsScreening = () => {
    navigate('/compliance/sanctions-screening/new');
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'info';
      case 'submitted': return 'warning';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'potential_match': return 'warning';
      case 'confirmed_match': return 'error';
      case 'no_match': return 'success';
      default: return 'default';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'report': return '📄';
      case 'pep_screening': return '🔍';
      case 'sanctions_screening': return '⚠️';
      default: return '📋';
    }
  };

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
          No dashboard data available.
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          Compliance Dashboard
        </h1>
        <div className="flex space-x-2">
          <Button 
            variant="default"
            onClick={handleGenerateUAFReport}
          >
            Generate UAF Report
          </Button>
          <Button 
            variant="outline"
            onClick={handleRunPEPScreening}
          >
            Run PEP Screening
          </Button>
          <Button 
            variant="outline"
            onClick={handleRunSanctionsScreening}
          >
            Run Sanctions Screening
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Reports Summary */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Compliance Reports</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.reports.total}</div>
                  <div className="text-sm text-muted-foreground">Total Reports</div>
                </div>
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.reports.pending}</div>
                  <div className="text-sm text-muted-foreground">Pending</div>
                </div>
                <div className="text-center p-2">
                  <div className="text-2xl font-bold">{dashboardData.reports.submitted}</div>
                  <div className="text-sm text-muted-foreground">Submitted</div>
                </div>
              </div>
              <Separator className="my-4" />
              <div className="text-sm font-medium mb-2">
                Reports by Type
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {Object.entries(dashboardData.reports.by_type).map(([type, count]) => (
                  <Badge 
                    key={type} 
                    variant="outline"
                    className="px-2 py-1"
                  >
                    {`${type}: ${count}`}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Screenings Summary */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Screening Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-2">
                  <div className="text-sm font-medium">PEP Screenings</div>
                  <div className="flex items-center mt-2">
                    <div className="relative inline-flex mr-2">
                      <div className="h-12 w-12 rounded-full flex items-center justify-center border-4 border-primary">
                        <span className="text-sm font-medium">
                          {`${Math.round(dashboardData.screenings.pep.match_percentage)}%`}
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm">
                        {dashboardData.screenings.pep.matches} matches out of {dashboardData.screenings.pep.total} screenings
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-2">
                  <div className="text-sm font-medium">Sanctions Screenings</div>
                  <div className="flex items-center mt-2">
                    <div className="relative inline-flex mr-2">
                      <div className="h-12 w-12 rounded-full flex items-center justify-center border-4 border-destructive">
                        <span className="text-sm font-medium">
                          {`${Math.round(dashboardData.screenings.sanctions.match_percentage)}%`}
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm">
                        {dashboardData.screenings.sanctions.matches} matches out of {dashboardData.screenings.sanctions.total} screenings
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <div className="col-span-1 md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-2">
                  {dashboardData.recent_activity.map((activity, index) => (
                    <div key={`${activity.type}-${activity.id}`}>
                      {index > 0 && <Separator className="my-2" />}
                      <div 
                        className="p-2 hover:bg-accent rounded-md cursor-pointer"
                        onClick={() => {
                          if (activity.type === 'report') {
                            navigate(`/compliance/reports/${activity.id}`);
                          } else if (activity.type === 'pep_screening') {
                            navigate(`/compliance/pep-screenings/${activity.id}`);
                          } else if (activity.type === 'sanctions_screening') {
                            navigate(`/compliance/sanctions-screenings/${activity.id}`);
                          }
                        }}
                      >
                        <div className="flex items-center">
                          <span className="mr-2">
                            {getActivityIcon(activity.type)}
                          </span>
                          <span className="font-medium">
                            {activity.type === 'report' 
                              ? `${activity.report_type} Report` 
                              : activity.type === 'pep_screening'
                                ? 'PEP Screening'
                                : 'Sanctions Screening'
                            }
                          </span>
                          {(activity.status || activity.match_status) && (
                            <Badge 
                              variant={getStatusColor(activity.status || activity.match_status) === 'success' ? 'default' : 
                                     getStatusColor(activity.status || activity.match_status) === 'error' ? 'destructive' : 
                                     getStatusColor(activity.status || activity.match_status) === 'warning' ? 'secondary' : 'outline'}
                              className="ml-2"
                            >
                              {activity.status || activity.match_status}
                            </Badge>
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">
                          <span className="font-medium">
                            {activity.type === 'report' 
                              ? `Entity: ${activity.entity_type} #${activity.entity_id}` 
                              : `Client #${activity.client_id}`
                            }
                          </span>
                          {" — "}
                          {formatDate(activity.created_at)}
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
