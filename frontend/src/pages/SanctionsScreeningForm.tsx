import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { AlertCircle, Loader2 } from "lucide-react";
import { Toast, ToastProvider, ToastViewport, ToastTitle, ToastDescription } from "@/components/ui/toast";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useTranslation } from "react-i18next";
import { SanctionsScreeningMatch } from "@/modules/compliance/types";

const SanctionsScreeningForm: React.FC = () => {
  const { t } = useTranslation();
  const [clientId, setClientId] = useState<string>('');
  const [entityName, setEntityName] = useState<string>('');
  const [entityType, setEntityType] = useState<string>('individual');
  const [country, setCountry] = useState<string>('');
  const [includeGlobalLists, setIncludeGlobalLists] = useState<boolean>(true);
  const [includeLocalLists, setIncludeLocalLists] = useState<boolean>(true);
  const [fuzzyMatching, setFuzzyMatching] = useState<boolean>(true);
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(70);
  const [useOpenSanctions, setUseOpenSanctions] = useState<boolean>(true);
  const [results, setResults] = useState<SanctionsScreeningMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!clientId) {
      setError(t('Please select a client'));
      return;
    }
    
    if (!entityName) {
      setError(t('Please enter an entity name'));
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/compliance/sanctions-screening`, {
        client_id: parseInt(clientId),
        entity_name: entityName,
        entity_type: entityType,
        country: country,
        include_global_lists: includeGlobalLists,
        include_local_lists: includeLocalLists,
        fuzzy_matching: fuzzyMatching,
        similarity_threshold: similarityThreshold / 100, // Convert from percentage to decimal
        use_opensanctions: useOpenSanctions
      });
      
      if (response.data && response.data.matches) {
        setResults(response.data.matches);
        navigate(`/compliance/sanctions-screenings/${response.data.id}`, {
          state: { 
            results: response.data.matches,
            screeningData: {
              clientId,
              entityName,
              entityType,
              country,
              includeGlobalLists,
              includeLocalLists,
              fuzzyMatching,
              similarityThreshold,
              useOpenSanctions
            }
          }
        });
      } else {
        setSuccess(true);
        setTimeout(() => {
          navigate(`/compliance/sanctions-screenings/${response.data.id}`);
        }, 1500);
      }
    } catch (err) {
      console.error('Error running sanctions screening:', err);
      setError(t('Failed to run sanctions screening. Please try again later.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <ToastProvider>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">
          {t('Run Sanctions Screening')}
        </h1>
        
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>{t('Sanctions Screening')}</CardTitle>
            <CardDescription>{t('Screen entities against international and local sanctions lists')}</CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <p className="text-base text-muted-foreground mb-6">
              {t('This form will run a sanctions screening for the selected client against local and international sanctions lists. The screening will identify if the entity is on any sanctions lists, which may require enhanced due diligence or reporting.')}
            </p>
            
            {error && (
              <Alert className="mb-6">
                <AlertCircle className="h-4 w-4 mr-2" />
                {error}
              </Alert>
            )}
            
            <form onSubmit={handleSubmit}>
              <div className="grid gap-6">
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="client">Client</Label>
                  <Select value={clientId} onValueChange={setClientId}>
                    <SelectTrigger id="client">
                      <SelectValue placeholder="Select a client" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Client #1</SelectItem>
                      <SelectItem value="2">Client #2</SelectItem>
                      <SelectItem value="3">Client #3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="entity-name">Entity Name</Label>
                  <Input
                    id="entity-name"
                    value={entityName}
                    onChange={(e) => setEntityName(e.target.value)}
                    placeholder="Enter entity name"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="entity-type">Entity Type</Label>
                    <Select value={entityType} onValueChange={setEntityType}>
                      <SelectTrigger id="entity-type">
                        <SelectValue placeholder="Select entity type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="individual">Individual</SelectItem>
                        <SelectItem value="company">Company</SelectItem>
                        <SelectItem value="organization">Organization</SelectItem>
                        <SelectItem value="government">Government Entity</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="country">Country (Optional)</Label>
                    <Input
                      id="country"
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      placeholder="Enter country"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="include-global-lists"
                      checked={includeGlobalLists}
                      onCheckedChange={(checked) => setIncludeGlobalLists(checked as boolean)}
                    />
                    <Label htmlFor="include-global-lists">{t('Include global sanctions lists')}</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="include-local-lists"
                      checked={includeLocalLists}
                      onCheckedChange={(checked) => setIncludeLocalLists(checked as boolean)}
                    />
                    <Label htmlFor="include-local-lists">{t('Include local sanctions lists')}</Label>
                  </div>
                </div>
                
                <div className="mt-6 border-t pt-6">
                  <h3 className="text-lg font-medium mb-4">{t('Advanced Matching Options')}</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="use-opensanctions"
                        checked={useOpenSanctions}
                        onCheckedChange={(checked) => setUseOpenSanctions(checked as boolean)}
                      />
                      <Label htmlFor="use-opensanctions">{t('Use OpenSanctions database')}</Label>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="fuzzy-matching"
                        checked={fuzzyMatching}
                        onCheckedChange={(checked) => setFuzzyMatching(checked as boolean)}
                      />
                      <Label htmlFor="fuzzy-matching">{t('Enable fuzzy name matching')}</Label>
                    </div>
                  </div>
                  
                  <div className="grid w-full items-center gap-2 mt-4">
                    <div className="flex justify-between">
                      <Label htmlFor="similarity-threshold">{t('Similarity Threshold')}: {similarityThreshold}%</Label>
                    </div>
                    <Slider
                      id="similarity-threshold"
                      disabled={!fuzzyMatching}
                      min={50}
                      max={100}
                      step={5}
                      value={[similarityThreshold]}
                      onValueChange={(value) => setSimilarityThreshold(value[0])}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>{t('More matches')}</span>
                      <span>{t('Exact matches')}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-end gap-2 mt-6">
                  <Button 
                    variant="outline" 
                    onClick={() => navigate('/compliance/dashboard')}
                    disabled={loading}
                  >
                    {t('Cancel')}
                  </Button>
                  <Button 
                    type="submit" 
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        {t('Running Screening...')}
                      </>
                    ) : (
                      t('Run Sanctions Screening')
                    )}
                  </Button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
        
        {results.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>{t('Sanctions Screening Results')}</CardTitle>
              <CardDescription>{t('Matches found in sanctions lists')}</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('Entity Name')}</TableHead>
                    <TableHead>{t('List Source')}</TableHead>
                    <TableHead>{t('Country')}</TableHead>
                    <TableHead className="text-right">{t('Similarity Score')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((match, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{match.name}</TableCell>
                      <TableCell>{match.list_source}</TableCell>
                      <TableCell>{match.country || '-'}</TableCell>
                      <TableCell className="text-right">
                        {Math.round(match.similarity_score * 100)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="flex justify-end mt-4">
                <Button variant="outline" className="mr-2">
                  {t('Export Results')}
                </Button>
                <Button onClick={() => navigate('/compliance/dashboard')}>
                  {t('Back to Dashboard')}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
        
        {success && (
          <Toast>
            <ToastTitle>{t('Success')}</ToastTitle>
            <ToastDescription>
              {t('Sanctions Screening initiated successfully')}
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default SanctionsScreeningForm;
