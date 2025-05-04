import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import { AlertCircle, Loader2 } from "lucide-react";
import { Toast, ToastProvider, ToastViewport, ToastTitle, ToastDescription } from "@/components/ui/toast";

const PEPScreeningForm: React.FC = () => {
  const [clientId, setClientId] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [idNumber, setIdNumber] = useState<string>('');
  const [nationality, setNationality] = useState<string>('');
  const [includeAliases, setIncludeAliases] = useState<boolean>(true);
  const [includeRelatives, setIncludeRelatives] = useState<boolean>(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!clientId) {
      setError('Please select a client');
      return;
    }
    
    if (!fullName) {
      setError('Please enter a full name');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/compliance/pep-screenings`, {
        client_id: parseInt(clientId),
        full_name: fullName,
        id_number: idNumber,
        nationality: nationality,
        include_aliases: includeAliases,
        include_relatives: includeRelatives
      });
      
      setSuccess(true);
      setTimeout(() => {
        navigate(`/compliance/pep-screenings/${response.data.id}`);
      }, 1500);
    } catch (err) {
      console.error('Error running PEP screening:', err);
      setError('Failed to run PEP screening. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ToastProvider>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">
          Run PEP Screening
        </h1>
        
        <Card className="mt-6">
          <CardContent className="p-6">
            <p className="text-base text-muted-foreground mb-6">
              This form will run a Politically Exposed Person (PEP) screening for the selected client
              against local and international PEP databases. The screening will identify if the person
              is a PEP or related to a PEP, which may require enhanced due diligence.
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
                    <Label htmlFor="include-aliases">Include known aliases</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="include-relatives"
                      checked={includeRelatives}
                      onCheckedChange={(checked) => setIncludeRelatives(checked as boolean)}
                    />
                    <Label htmlFor="include-relatives">Include close relatives</Label>
                  </div>
                </div>
                
                <div className="flex justify-end gap-2 mt-6">
                  <Button 
                    variant="outline" 
                    onClick={() => navigate('/compliance/dashboard')}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  <Button 
                    type="submit" 
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Running Screening...
                      </>
                    ) : (
                      'Run PEP Screening'
                    )}
                  </Button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
        
        {success && (
          <Toast>
            <ToastTitle>Success</ToastTitle>
            <ToastDescription>
              PEP Screening initiated successfully
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default PEPScreeningForm;
