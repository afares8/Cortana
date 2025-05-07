import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";
import { AlertCircle, ChevronDown, ChevronRight, Loader2 } from "lucide-react";
import { Alert } from "../ui/alert";
import { Collapsible, CollapsibleContent } from "../ui/collapsible";
import { useComplianceCheck } from '../../hooks/useComplianceCheck';

export interface ComplianceCheckProps {
  customer: { 
    name: string; 
    dob?: string; 
    country: string; 
    type: 'natural' | 'legal' 
  };
  directors?: Array<{ 
    name: string; 
    dob: string; 
    country: string 
  }>;
  ubos?: Array<{ 
    name: string; 
    dob: string; 
    country: string 
  }>;
}

export const ComplianceCheck: React.FC<ComplianceCheckProps> = ({ 
  customer, 
  directors = [], 
  ubos = [] 
}) => {
  const { t } = useTranslation();
  const { loading, error, result, checkCompliance } = useComplianceCheck();
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

  const handleCheck = async () => {
    const requestData = {
      customer: {
        ...customer,
        type: customer.type
      },
      directors: directors.map(director => ({
        ...director,
        type: 'natural' as const
      })),
      ubos: ubos.map(ubo => ({
        ...ubo,
        type: 'natural' as const
      }))
    };
    
    await checkCompliance(requestData);
  };

  const toggleRow = (module: string) => {
    setExpandedRows(prev => ({
      ...prev,
      [module]: !prev[module]
    }));
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'clear':
        return <Badge className="bg-green-500 text-white">Clear</Badge>;
      case 'matched':
        return <Badge variant="destructive">Matched</Badge>;
      case 'watchlist':
        return <Badge className="bg-yellow-500 text-white">Watchlist</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{t('compliance.customerVerification')}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">{customer.name}</p>
              <p className="text-sm text-muted-foreground">
                {customer.type === 'natural' ? t('compliance.naturalPerson') : t('compliance.legalEntity')}
                {customer.country && ` • ${customer.country}`}
                {customer.dob && ` • ${customer.dob}`}
              </p>
              {directors.length > 0 && (
                <p className="text-sm text-muted-foreground">
                  {t('compliance.directors')}: {directors.length}
                </p>
              )}
              {ubos.length > 0 && (
                <p className="text-sm text-muted-foreground">
                  {t('compliance.ubos')}: {ubos.length}
                </p>
              )}
            </div>
            <Button 
              onClick={handleCheck}
              disabled={loading}
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {t('compliance.runComplianceCheck')}
            </Button>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4 mr-2" />
              {error}
            </Alert>
          )}

          {result && (
            <div className="mt-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('compliance.module')}</TableHead>
                    <TableHead>{t('compliance.status')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(result)
                    .filter(([key, value]) => 
                      value && typeof value === 'object' && 'status' in value && key !== 'enriched_data'
                    )
                    .map(([module, data]) => (
                      <React.Fragment key={module}>
                        <TableRow className="cursor-pointer" onClick={() => toggleRow(module)}>
                          <TableCell className="font-medium">
                            <div className="flex items-center">
                              {expandedRows[module] ? (
                                <ChevronDown className="h-4 w-4 mr-2" />
                              ) : (
                                <ChevronRight className="h-4 w-4 mr-2" />
                              )}
                              {module.toUpperCase()}
                            </div>
                          </TableCell>
                          <TableCell>
                            {getStatusBadge(data?.status || 'unknown')}
                          </TableCell>
                        </TableRow>
                        <Collapsible open={expandedRows[module]}>
                          <CollapsibleContent>
                            <TableRow className="bg-accent/50">
                              <TableCell colSpan={2} className="p-4">
                                {data?.matches && data.matches.length > 0 ? (
                                  <div className="space-y-3">
                                    {data.matches.map((match: any, idx: number) => (
                                      <div key={idx} className="p-3 bg-background rounded border">
                                        <div className="font-medium">{match.name}</div>
                                        <div className="text-sm mt-1">
                                          <span className="text-muted-foreground">{t('compliance.source')}:</span> {match.source}
                                        </div>
                                        <div className="text-sm">
                                          <span className="text-muted-foreground">{t('compliance.matchType')}:</span> {match.match_type}
                                        </div>
                                        <div className="text-sm">
                                          <span className="text-muted-foreground">{t('compliance.score')}:</span> {Math.round(match.score * 100)}%
                                        </div>
                                        {match.details && Object.keys(match.details).length > 0 && (
                                          <div className="mt-2 text-sm">
                                            <div className="font-medium">{t('compliance.details')}</div>
                                            <pre className="text-xs mt-1 p-2 bg-muted rounded overflow-x-auto">
                                              {JSON.stringify(match.details, null, 2)}
                                            </pre>
                                          </div>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                ) : (
                                  <div className="text-center py-2">
                                    {t('compliance.noMatches')}
                                  </div>
                                )}
                              </TableCell>
                            </TableRow>
                          </CollapsibleContent>
                        </Collapsible>
                      </React.Fragment>
                    ))}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
