import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { AIDashboardStats } from '@/types';
import PageLayout from '@/components/layout/PageLayout';

export default function AIDashboard() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [queryResponse, setQueryResponse] = useState<string | null>(null);
  
  const [stats, setStats] = useState<AIDashboardStats>({
    total_contracts: 16,
    analyzed_contracts: 12,
    risk_distribution: {
      high_risk: 3,
      medium_risk: 7,
      low_risk: 2,
    },
    anomalies: {
      total: 8,
      high_severity: 2,
      medium_severity: 4,
      low_severity: 2,
    },
    clauses: {
      total: 48,
      by_type: {
        confidentiality: 12,
        termination: 10,
        penalties: 8,
        jurisdiction: 6,
        obligations: 12,
      },
    },
  });
  
  const handleQuerySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsQuerying(true);
    setQueryResponse(null);
    
    setTimeout(() => {
      let response = '';
      
      if (query.toLowerCase().includes('expir')) {
        response = "I found 3 contracts that expire next quarter:\n\n" +
          "1. Service Agreement with Acme Corp (expires July 15, 2025)\n" +
          "2. NDA with TechStart Inc (expires August 1, 2025)\n" +
          "3. Lease Agreement for Office Space (expires September 30, 2025)";
      } else if (query.toLowerCase().includes('indemnity') || query.toLowerCase().includes('clause')) {
        response = "I found 2 contracts that lack indemnity clauses:\n\n" +
          "1. NDA with TechStart Inc\n" +
          "2. Lease Agreement for Office Space\n\n" +
          "This represents a potential risk as these contracts don't protect against third-party claims.";
      } else if (query.toLowerCase().includes('create') || query.toLowerCase().includes('draft') || query.toLowerCase().includes('nda')) {
        response = "I've prepared a draft NDA with standard clauses. Would you like me to:\n\n" +
          "1. Show you the template\n" +
          "2. Pre-fill it with a specific company name\n" +
          "3. Customize the confidentiality period";
      } else {
        response = `I've analyzed your query: "${query}"\n\n` +
          "I found 5 potentially relevant contracts in the database. The most relevant are:\n\n" +
          "1. Service Agreement with Acme Corp (90% relevance)\n" +
          "2. License Agreement with Global Tech (75% relevance)\n\n" +
          "Would you like me to show you specific clauses from these contracts?";
      }
      
      setQueryResponse(response);
      setIsQuerying(false);
    }, 1500);
  };
  
  return (
    <PageLayout>
      <div className="container mx-auto py-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">AI Legal Command Center</h1>
          <Button onClick={() => navigate('/contracts')}>
            View All Contracts
          </Button>
        </div>
        
        {/* Natural Language Query */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Legal AI Assistant</CardTitle>
            <CardDescription>
              Ask questions about your contracts in plain English
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleQuerySubmit} className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="e.g., 'Show me all contracts that expire next quarter' or 'Which contracts lack indemnity clauses?'"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="flex-1"
                />
                <Button type="submit" disabled={isQuerying}>
                  {isQuerying ? 'Processing...' : 'Ask'}
                </Button>
              </div>
              
              {isQuerying && (
                <div className="text-center py-8">
                  <div className="mb-2">Analyzing contracts and generating response...</div>
                  <Progress value={65} className="w-[80%] mx-auto" />
                </div>
              )}
              
              {queryResponse && (
                <div className="mt-4 p-4 border rounded-md bg-muted/50 whitespace-pre-line">
                  {queryResponse}
                </div>
              )}
            </form>
          </CardContent>
        </Card>
        
        {/* AI Dashboard Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Contract Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold mb-2">
                {stats.analyzed_contracts}/{stats.total_contracts}
              </div>
              <p className="text-muted-foreground text-sm">
                Contracts analyzed by AI
              </p>
              <Progress 
                value={(stats.analyzed_contracts / stats.total_contracts) * 100} 
                className="mt-4" 
              />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Risk Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center mb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span className="text-sm">High Risk</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span className="text-sm">Medium Risk</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-sm">Low Risk</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm">{stats.risk_distribution.high_risk}</div>
                  <div className="text-sm">{stats.risk_distribution.medium_risk}</div>
                  <div className="text-sm">{stats.risk_distribution.low_risk}</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Anomalies Detected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold mb-2">
                {stats.anomalies.total}
              </div>
              <div className="flex gap-2 mt-2">
                <Badge variant="destructive">{stats.anomalies.high_severity} High</Badge>
                <Badge variant="outline" className="bg-yellow-100">{stats.anomalies.medium_severity} Medium</Badge>
                <Badge variant="outline" className="bg-green-100">{stats.anomalies.low_severity} Low</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Clause Distribution */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Clause Distribution</CardTitle>
            <CardDescription>
              Analysis of {stats.clauses.total} clauses extracted from contracts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(stats.clauses.by_type).map(([type, count]) => (
                <div key={type} className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium capitalize">{type}</span>
                    <span className="text-sm text-muted-foreground">{count}</span>
                  </div>
                  <Progress value={(count / stats.clauses.total) * 100} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        {/* Smart Notifications */}
        <Card>
          <CardHeader>
            <CardTitle>Smart Notifications</CardTitle>
            <CardDescription>
              AI-powered alerts and recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 border rounded-md bg-yellow-50">
                <div className="font-medium mb-1">Contract ABC will expire in 17 days</div>
                <p className="text-sm text-muted-foreground">
                  This contract contains a non-standard arbitration clause that requires 30 days notice for renewal.
                </p>
              </div>
              
              <div className="p-4 border rounded-md bg-red-50">
                <div className="font-medium mb-1">3 contracts from Supplier X are pending signature beyond SLA threshold</div>
                <p className="text-sm text-muted-foreground">
                  These contracts have been in review for more than 14 days, exceeding your company's standard approval timeline.
                </p>
              </div>
              
              <div className="p-4 border rounded-md bg-blue-50">
                <div className="font-medium mb-1">Pattern detected: Increasing termination rate in Q2</div>
                <p className="text-sm text-muted-foreground">
                  Termination rate for service agreements has increased by 15% compared to previous quarter.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageLayout>
  );
}
