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

const SanctionsScreeningForm: React.FC = () => {
  const [clientId, setClientId] = useState<string>('');
  const [entityName, setEntityName] = useState<string>('');
  const [entityType, setEntityType] = useState<string>('individual');
  const [country, setCountry] = useState<string>('');
  const [includeGlobalLists, setIncludeGlobalLists] = useState<boolean>(true);
  const [includeLocalLists, setIncludeLocalLists] = useState<boolean>(true);
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
    
    if (!entityName) {
      setError('Please enter an entity name');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/compliance/sanctions-screenings`, {
        client_id: parseInt(clientId),
        entity_name: entityName,
        entity_type: entityType,
        country: country,
        include_global_lists: includeGlobalLists,
        include_local_lists: includeLocalLists
      });
      
      setSuccess(true);
      setTimeout(() => {
        navigate(`/compliance/sanctions-screenings/${response.data.id}`);
      }, 1500);
    } catch (err) {
      console.error('Error running sanctions screening:', err);
      setError('Failed to run sanctions screening. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ToastProvider>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">
          Run Sanctions Screening
        </h1>
        
        <Card className="mt-6">
          <CardContent className="p-6">
            <p className="text-base text-muted-foreground mb-6">
              This form will run a sanctions screening for the selected client
              against local and international sanctions lists. The screening will identify if the entity
              is on any sanctions lists, which may require enhanced due diligence or reporting.
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
                    <Label htmlFor="include-global-lists">Include global sanctions lists</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="include-local-lists"
                      checked={includeLocalLists}
                      onCheckedChange={(checked) => setIncludeLocalLists(checked as boolean)}
                    />
                    <Label htmlFor="include-local-lists">Include local sanctions lists</Label>
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
                      'Run Sanctions Screening'
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
              Sanctions Screening initiated successfully
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default SanctionsScreeningForm;
