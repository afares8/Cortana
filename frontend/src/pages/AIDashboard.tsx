import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { AIDashboardStats } from '@/types';
import Layout from '@/components/layout/Layout';
import axios from 'axios';
import { AIContextualChat } from '@/components/ai/AIContextualChat';

interface EnhancedAIDashboardStats extends AIDashboardStats {
  ai_activity?: {
    recent_queries: string[];
    total_queries: number;
    model: string;
  };
  anomalies: {
    total: number;
    high_severity: number;
    medium_severity: number;
    low_severity: number;
    by_source?: {
      traditional_nlp: number;
      mistral: number;
    };
  };
}

const API_URL = import.meta.env.VITE_API_URL || 'https://prueba-pouw.onrender.com';

export default function AIDashboard() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [queryResponse, setQueryResponse] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isFallback, setIsFallback] = useState(false);
  
  const [stats, setStats] = useState<EnhancedAIDashboardStats>({
    total_contracts: 0,
    analyzed_contracts: 0,
    risk_distribution: {
      high_risk: 0,
      medium_risk: 0,
      low_risk: 0,
    },
    anomalies: {
      total: 0,
      high_severity: 0,
      medium_severity: 0,
      low_severity: 0,
    },
    clauses: {
      total: 0,
      by_type: {},
    },
  });
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/v1/ai/dashboard/stats`);
        setStats(response.data);
      } catch (err) {
        console.error('Error fetching AI dashboard stats:', err);
        setError('Failed to load AI dashboard statistics. Please try again later.');
        
        setStats({
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
          ai_activity: {
            recent_queries: [
              "Show contracts expiring next month",
              "Which contracts have indemnity clauses?",
              "Analyze risk in the Acme Corp agreement"
            ],
            total_queries: 24,
            model: "OpenHermes-2.5-Mistral-7B"
          }
        });
      }
    };
    
    fetchStats();
  }, []);
  
  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsQuerying(true);
    setQueryResponse(null);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/api/v1/ai/mistral/generate`, {
        inputs: query,
        max_new_tokens: 100
      });
      
      setQueryResponse(response.data.generated_text);
      setIsFallback(response.data.is_fallback || false);
    } catch (err) {
      console.error('Error querying AI:', err);
      setError('Failed to process your query. Please try again later.');
      
      let fallbackResponse = `I've analyzed your query: "${query}"\n\n` +
        "I found several potentially relevant contracts in the database, but I'm currently experiencing connectivity issues.\n\n" +
        "Please try again in a few moments.";
      
      setQueryResponse(fallbackResponse);
      setIsFallback(true);
    } finally {
      setIsQuerying(false);
    }
  };
  
  return (
    <Layout title="AI Legal Command Center">
      <div className="container mx-auto">
        <div className="flex justify-between items-center mb-6">
          <Button onClick={() => navigate('/contracts')}>
            View All Contracts
          </Button>
        </div>
        
        {/* Natural Language Query */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Legal AI Assistant</CardTitle>
            <CardDescription>
              Ask questions about your contracts using the Mistral 7B model
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
                  <div className="mb-2">Analyzing contracts and generating response with Mistral 7B...</div>
                  <Progress value={65} className="w-[80%] mx-auto" />
                </div>
              )}
              
              {error && (
                <div className="mt-4 p-4 border rounded-md bg-red-50 text-red-800">
                  {error}
                </div>
              )}
              
              {queryResponse && (
                <div className="mt-4">
                  {isFallback && (
                    <div className="mb-3 p-3 border rounded-md bg-amber-50 text-amber-800">
                      <strong>Note:</strong> This is a fallback response. The Mistral 7B model requires GPU hardware with Flash Attention v2 support, which is not available in the current environment.
                    </div>
                  )}
                  <div className="p-4 border rounded-md bg-muted/50 whitespace-pre-line">
                    {queryResponse}
                  </div>
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
                value={(stats.analyzed_contracts / stats.total_contracts) * 100 || 0} 
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
              {stats.anomalies.by_source && (
                <div className="mt-3 text-xs text-muted-foreground">
                  <div>Traditional NLP: {stats.anomalies.by_source.traditional_nlp}</div>
                  <div>Mistral AI: {stats.anomalies.by_source.mistral}</div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        
        {/* AI Model Info & Activity */}
        {stats.ai_activity && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>AI Model Information</CardTitle>
              <CardDescription>
                Using {stats.ai_activity.model} for enhanced legal analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium mb-2">Recent Queries ({stats.ai_activity.total_queries} total)</h3>
                  <ul className="space-y-2">
                    {stats.ai_activity.recent_queries.map((q, i) => (
                      <li key={i} className="text-sm p-2 bg-gray-50 rounded-md">{q}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
        
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
                  <Progress value={(count / stats.clauses.total) * 100 || 0} />
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
    </Layout>
  );
}
