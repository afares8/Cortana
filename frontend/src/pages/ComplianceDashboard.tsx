import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid, Box, Chip, CircularProgress, Button, Divider, List, ListItem, ListItemText, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

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
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">No dashboard data available.</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Compliance Dashboard
        </Typography>
        <Box>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleGenerateUAFReport}
            sx={{ mr: 1 }}
          >
            Generate UAF Report
          </Button>
          <Button 
            variant="outlined" 
            color="primary" 
            onClick={handleRunPEPScreening}
            sx={{ mr: 1 }}
          >
            Run PEP Screening
          </Button>
          <Button 
            variant="outlined" 
            color="secondary" 
            onClick={handleRunSanctionsScreening}
          >
            Run Sanctions Screening
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Reports Summary */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Compliance Reports
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h4">{dashboardData.reports.total}</Typography>
                    <Typography variant="body2" color="textSecondary">Total Reports</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h4">{dashboardData.reports.pending}</Typography>
                    <Typography variant="body2" color="textSecondary">Pending</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h4">{dashboardData.reports.submitted}</Typography>
                    <Typography variant="body2" color="textSecondary">Submitted</Typography>
                  </Box>
                </Grid>
              </Grid>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" gutterBottom>
                Reports by Type
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {Object.entries(dashboardData.reports.by_type).map(([type, count]) => (
                  <Chip 
                    key={type} 
                    label={`${type}: ${count}`} 
                    color="primary" 
                    variant="outlined" 
                    size="small" 
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Screenings Summary */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Screening Results
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ p: 1 }}>
                    <Typography variant="subtitle1">PEP Screenings</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <Box sx={{ position: 'relative', display: 'inline-flex', mr: 2 }}>
                        <CircularProgress 
                          variant="determinate" 
                          value={dashboardData.screenings.pep.match_percentage} 
                          color={dashboardData.screenings.pep.match_percentage > 20 ? "warning" : "success"}
                        />
                        <Box
                          sx={{
                            top: 0,
                            left: 0,
                            bottom: 0,
                            right: 0,
                            position: 'absolute',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <Typography variant="caption" component="div" color="text.secondary">
                            {`${Math.round(dashboardData.screenings.pep.match_percentage)}%`}
                          </Typography>
                        </Box>
                      </Box>
                      <Box>
                        <Typography variant="body2">
                          {dashboardData.screenings.pep.matches} matches out of {dashboardData.screenings.pep.total} screenings
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1 }}>
                    <Typography variant="subtitle1">Sanctions Screenings</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <Box sx={{ position: 'relative', display: 'inline-flex', mr: 2 }}>
                        <CircularProgress 
                          variant="determinate" 
                          value={dashboardData.screenings.sanctions.match_percentage} 
                          color={dashboardData.screenings.sanctions.match_percentage > 5 ? "error" : "success"}
                        />
                        <Box
                          sx={{
                            top: 0,
                            left: 0,
                            bottom: 0,
                            right: 0,
                            position: 'absolute',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <Typography variant="caption" component="div" color="text.secondary">
                            {`${Math.round(dashboardData.screenings.sanctions.match_percentage)}%`}
                          </Typography>
                        </Box>
                      </Box>
                      <Box>
                        <Typography variant="body2">
                          {dashboardData.screenings.sanctions.matches} matches out of {dashboardData.screenings.sanctions.total} screenings
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {dashboardData.recent_activity.map((activity, index) => (
                  <React.Fragment key={`${activity.type}-${activity.id}`}>
                    {index > 0 && <Divider component="li" />}
                    <ListItem 
                      alignItems="flex-start"
                      button
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
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography component="span" sx={{ mr: 1 }}>
                              {getActivityIcon(activity.type)}
                            </Typography>
                            <Typography component="span">
                              {activity.type === 'report' 
                                ? `${activity.report_type} Report` 
                                : activity.type === 'pep_screening'
                                  ? 'PEP Screening'
                                  : 'Sanctions Screening'
                              }
                            </Typography>
                            {(activity.status || activity.match_status) && (
                              <Chip 
                                size="small" 
                                label={activity.status || activity.match_status} 
                                color={getStatusColor(activity.status || activity.match_status) as any}
                                sx={{ ml: 1 }}
                              />
                            )}
                          </Box>
                        }
                        secondary={
                          <React.Fragment>
                            <Typography
                              component="span"
                              variant="body2"
                              color="textPrimary"
                            >
                              {activity.type === 'report' 
                                ? `Entity: ${activity.entity_type} #${activity.entity_id}` 
                                : `Client #${activity.client_id}`
                              }
                            </Typography>
                            {" — "}
                            {formatDate(activity.created_at)}
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComplianceDashboard;
