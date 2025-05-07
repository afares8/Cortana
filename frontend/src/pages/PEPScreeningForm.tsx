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
import { PEPScreeningMatch } from "@/modules/compliance/types";

const PEPScreeningForm: React.FC = () => {
  const { t } = useTranslation();
  const [clientId, setClientId] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [idNumber, setIdNumber] = useState<string>('');
  const [nationality, setNationality] = useState<string>('');
  const [includeAliases, setIncludeAliases] = useState<boolean>(true);
  const [includeRelatives, setIncludeRelatives] = useState<boolean>(false);
  const [fuzzyMatching, setFuzzyMatching] = useState<boolean>(true);
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(70);
  const [results, setResults] = useState<PEPScreeningMatch[]>([]);
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
    
    if (!fullName) {
      setError(t('Please enter a full name'));
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/compliance/pep-screening`, {
        client_id: parseInt(clientId),
        full_name: fullName,
        id_number: idNumber,
        nationality: nationality,
        include_aliases: includeAliases,
        include_relatives: includeRelatives,
        fuzzy_matching: fuzzyMatching,
        similarity_threshold: similarityThreshold / 100 // Convert from percentage to decimal
      });
      
      if (response.data && response.data.matches) {
        setResults(response.data.matches);
        navigate(`/compliance/pep-screenings/${response.data.id}`, {
          state: { 
            results: response.data.matches,
            screeningData: {
              clientId,
              fullName,
              idNumber,
              nationality,
              includeAliases,
              includeRelatives,
              fuzzyMatching,
              similarityThreshold
            }
          }
        });
      } else {
        setSuccess(true);
        setTimeout(() => {
          navigate(`/compliance/pep-screenings/${response.data.id}`);
        }, 1500);
      }
    } catch (err) {
      console.error('Error running PEP screening:', err);
      setError(t('Failed to run PEP screening. Please try again later.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <ToastProvider>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">
          {t('Run PEP Screening')}
        </h1>
        
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>{t('PEP Screening')}</CardTitle>
            <CardDescription>{t('Screen individuals against Politically Exposed Persons databases')}</CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <p className="text-base text-muted-foreground mb-6">
              {t('This form will run a Politically Exposed Person (PEP) screening for the selected client against local and international PEP databases. The screening will identify if the person is a PEP or related to a PEP, which may require enhanced due diligence.')}
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
                  <Label htmlFor="full-name">Full Name</Label>
                  <Input
                    id="full-name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Enter full name"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="id-number">ID Number (Optional)</Label>
                    <Input
                      id="id-number"
                      value={idNumber}
                      onChange={(e) => setIdNumber(e.target.value)}
                      placeholder="Enter ID number"
                    />
                  </div>
                  
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="nationality">Nationality (Optional)</Label>
                    <Input
                      id="nationality"
                      value={nationality}
                      onChange={(e) => setNationality(e.target.value)}
                      placeholder="Enter nationality"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="include-aliases"
                      checked={includeAliases}
                      onCheckedChange={(checked) => setIncludeAliases(checked as boolean)}
                    />
                    <Label htmlFor="include-aliases">{t('Include known aliases')}</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="include-relatives"
                      checked={includeRelatives}
                      onCheckedChange={(checked) => setIncludeRelatives(checked as boolean)}
                    />
                    <Label htmlFor="include-relatives">{t('Include close relatives')}</Label>
                  </div>
                </div>
                
                <div className="mt-6 border-t pt-6">
                  <h3 className="text-lg font-medium mb-4">{t('Fuzzy Matching Options')}</h3>
                  
                  <div className="flex items-center space-x-2 mb-4">
                    <Checkbox
                      id="fuzzy-matching"
                      checked={fuzzyMatching}
                      onCheckedChange={(checked) => setFuzzyMatching(checked as boolean)}
                    />
                    <Label htmlFor="fuzzy-matching">{t('Enable fuzzy name matching')}</Label>
                  </div>
                  
                  <div className="grid w-full items-center gap-2">
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
                      t('Run PEP Screening')
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
              <CardTitle>{t('PEP Screening Results')}</CardTitle>
              <CardDescription>{t('Matches found with similarity scores')}</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('Name')}</TableHead>
                    <TableHead>{t('Position')}</TableHead>
                    <TableHead>{t('Country')}</TableHead>
                    <TableHead className="text-right">{t('Similarity Score')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((match, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{match.name}</TableCell>
                      <TableCell>{match.position}</TableCell>
                      <TableCell>{match.country}</TableCell>
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
              {t('PEP Screening initiated successfully')}
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default PEPScreeningForm;
