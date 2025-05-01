import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Contract } from '@/types';

interface AIContractAnalysisProps {
  contract: Contract;
}

export function AIContractAnalysis({ contract }: AIContractAnalysisProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [activeTab, setActiveTab] = useState("clauses");
  
  const [extractedClauses, setExtractedClauses] = useState<any[]>([]);
  const [riskScore, setRiskScore] = useState<any>(null);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  
  const handleAnalyze = () => {
    setIsAnalyzing(true);
    
    setTimeout(() => {
      setExtractedClauses([
        {
          id: 1,
          clause_type: "confidentiality",
          clause_text: "All information shared between parties shall be kept confidential for a period of 5 years after termination of this agreement.",
          confidence_score: 0.92
        },
        {
          id: 2,
          clause_type: "termination",
          clause_text: "This agreement may be terminated by either party with 30 days written notice.",
          confidence_score: 0.88
        },
        {
          id: 3,
          clause_type: "penalties",
          clause_text: "Failure to deliver services on time will result in a penalty of 5% of the contract value per week of delay.",
          confidence_score: 0.75
        }
      ]);
      
      setRiskScore({
        overall_score: 0.65,
        missing_clauses: ["jurisdiction"],
        abnormal_durations: false,
        red_flag_terms: [
          { term: "indemnify and hold harmless", category: "indemnification" }
        ]
      });
      
      setAnomalies([
        {
          id: 1,
          anomaly_type: "policy_deviation",
          description: "Missing required clauses: jurisdiction",
          severity: "medium"
        },
        {
          id: 2,
          anomaly_type: "red_flag_term",
          description: "Contains red flag term: indemnify and hold harmless (category: indemnification)",
          severity: "medium"
        }
      ]);
      
      setIsAnalyzing(false);
      setAnalysisComplete(true);
    }, 2000);
  };
  
  const getRiskColor = (score: number) => {
    if (score < 0.3) return "bg-green-500";
    if (score < 0.7) return "bg-yellow-500";
    return "bg-red-500";
  };
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low": return "bg-green-500";
      case "medium": return "bg-yellow-500";
      case "high": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>AI Contract Analysis</CardTitle>
        <CardDescription>
          Extract clauses, assess risk, and detect anomalies in this contract
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!analysisComplete ? (
          <div className="flex flex-col items-center justify-center py-8">
            {isAnalyzing ? (
              <div className="text-center">
                <div className="mb-4">Analyzing contract...</div>
                <Progress value={45} className="w-[60%] mx-auto" />
              </div>
            ) : (
              <Button onClick={handleAnalyze} className="w-[200px]">
                Analyze Contract
              </Button>
            )}
          </div>
        ) : (
          <Tabs defaultValue={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="clauses">Extracted Clauses</TabsTrigger>
              <TabsTrigger value="risk">Risk Assessment</TabsTrigger>
              <TabsTrigger value="anomalies">Anomalies</TabsTrigger>
            </TabsList>
            
            <TabsContent value="clauses" className="py-4">
              <h3 className="text-lg font-medium mb-4">Extracted Clauses</h3>
              <div className="space-y-4">
                {extractedClauses.map((clause) => (
                  <div key={clause.id} className="border rounded-md p-4">
                    <div className="flex justify-between items-start mb-2">
                      <Badge variant="outline" className="capitalize">
                        {clause.clause_type}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        Confidence: {Math.round(clause.confidence_score * 100)}%
                      </span>
                    </div>
                    <p className="text-sm">{clause.clause_text}</p>
                  </div>
                ))}
              </div>
            </TabsContent>
            
            <TabsContent value="risk" className="py-4">
              <h3 className="text-lg font-medium mb-4">Risk Assessment</h3>
              {riskScore && (
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="text-xl font-bold">
                      Risk Score: {Math.round(riskScore.overall_score * 100)}%
                    </div>
                    <div className={`w-3 h-3 rounded-full ${getRiskColor(riskScore.overall_score)}`}></div>
                  </div>
                  
                  {riskScore.missing_clauses.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Missing Clauses:</h4>
                      <ul className="list-disc list-inside">
                        {riskScore.missing_clauses.map((clause: string, index: number) => (
                          <li key={index} className="capitalize">{clause}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {riskScore.red_flag_terms.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Red Flag Terms:</h4>
                      <ul className="list-disc list-inside">
                        {riskScore.red_flag_terms.map((term: any, index: number) => (
                          <li key={index}>
                            {term.term} <span className="text-muted-foreground">({term.category})</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="anomalies" className="py-4">
              <h3 className="text-lg font-medium mb-4">Detected Anomalies</h3>
              <div className="space-y-4">
                {anomalies.map((anomaly) => (
                  <div key={anomaly.id} className="border rounded-md p-4">
                    <div className="flex justify-between items-start mb-2">
                      <Badge variant="outline" className="capitalize">
                        {anomaly.anomaly_type.replace('_', ' ')}
                      </Badge>
                      <div className="flex items-center gap-2">
                        <span className="text-sm capitalize">{anomaly.severity}</span>
                        <div className={`w-2 h-2 rounded-full ${getSeverityColor(anomaly.severity)}`}></div>
                      </div>
                    </div>
                    <p className="text-sm">{anomaly.description}</p>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
      <CardFooter className="flex justify-between">
        <div className="text-sm text-muted-foreground">
          Powered by AI Contract Intelligence Engine
        </div>
      </CardFooter>
    </Card>
  );
}
