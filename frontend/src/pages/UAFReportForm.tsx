import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert } from "@/components/ui/alert";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { AlertCircle, CalendarIcon, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Toast, ToastProvider, ToastViewport, ToastTitle, ToastDescription } from "@/components/ui/toast";

const UAFReportForm: React.FC = () => {
  const [clientId, setClientId] = useState<string>('');
  const [startDate, setStartDate] = useState<Date | undefined>(new Date(new Date().setMonth(new Date().getMonth() - 1)));
  const [endDate, setEndDate] = useState<Date | undefined>(new Date());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isStartDateOpen, setIsStartDateOpen] = useState(false);
  const [isEndDateOpen, setIsEndDateOpen] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!clientId) {
      setError('Please select a client');
      return;
    }
    
    if (!startDate || !endDate) {
      setError('Please select both start and end dates');
      return;
    }
    
    if (startDate > endDate) {
      setError('Start date cannot be after end date');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/compliance/uaf-reports`, {
        client_id: parseInt(clientId),
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString()
      }, {
        responseType: 'blob' // Set response type to blob
      });
      
      const contentType = response.headers['content-type'];
      if (contentType && contentType.includes('application/pdf')) {
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        const contentDisposition = response.headers['content-disposition'];
        const filename = contentDisposition
          ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
          : `uaf-report-${format(new Date(), 'yyyy-MM-dd')}.pdf`;
        
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        setSuccess(true);
        setTimeout(() => {
          setSuccess(false);
        }, 3000);
      } else {
        throw new Error('Invalid file format received');
      }
    } catch (err) {
      console.error('Error generating UAF report:', err);
      setError('Failed to generate UAF report. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ToastProvider>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">
          Generate UAF Report
        </h1>
        
        <Card className="mt-6">
          <CardContent className="p-6">
            <p className="text-base text-muted-foreground mb-6">
              This form will generate a UAF (Unidad de Análisis Financiero) report for the selected client
              and date range. The report will analyze transactions and identify any suspicious activities
              that need to be reported to regulatory authorities.
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
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="start-date">Start Date</Label>
                    <Popover open={isStartDateOpen} onOpenChange={setIsStartDateOpen}>
                      <PopoverTrigger asChild>
                        <Button
                          id="start-date"
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !startDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {startDate ? format(startDate, "PPP") : "Select start date"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={startDate}
                          onSelect={(date: Date | undefined) => {
                            setStartDate(date);
                            setIsStartDateOpen(false);
                          }}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                  
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="end-date">End Date</Label>
                    <Popover open={isEndDateOpen} onOpenChange={setIsEndDateOpen}>
                      <PopoverTrigger asChild>
                        <Button
                          id="end-date"
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !endDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {endDate ? format(endDate, "PPP") : "Select end date"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={endDate}
                          onSelect={(date: Date | undefined) => {
                            setEndDate(date);
                            setIsEndDateOpen(false);
                          }}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
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
                        Generating...
                      </>
                    ) : (
                      'Generate Report'
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
              UAF Report generated successfully
            </ToastDescription>
          </Toast>
        )}
        <ToastViewport />
      </div>
    </ToastProvider>
  );
};

export default UAFReportForm;
