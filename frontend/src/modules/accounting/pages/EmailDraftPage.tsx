import React, { useEffect, useState } from 'react';
import { getCompanies, getObligations, createEmailDraft } from '../api/accountingApi';
import { Company, Obligation, EmailDraftRequest, EmailDraftResponse } from '../types';
import { Loader2, Mail, Copy, AlertCircle } from 'lucide-react';

const EmailDraftPage: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [obligations, setObligations] = useState<Obligation[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [selectedObligation, setSelectedObligation] = useState<string>('');
  const [recipient, setRecipient] = useState<string>('');
  const [context, setContext] = useState<string>('');
  const [emailDraft, setEmailDraft] = useState<EmailDraftResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchCompanies = async () => {
    try {
      const data = await getCompanies();
      setCompanies(data);
    } catch (error) {
      console.error('Error fetching companies:', error);
      setError('Failed to load companies');
    }
  };

  const fetchObligations = async (companyId: string) => {
    if (!companyId) {
      setObligations([]);
      return;
    }
    
    try {
      const data = await getObligations({ company_id: parseInt(companyId) });
      setObligations(data);
    } catch (error) {
      console.error('Error fetching obligations:', error);
      setError('Failed to load obligations');
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  const handleCompanyChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const companyId = event.target.value;
    setSelectedCompany(companyId);
    setSelectedObligation('');
    fetchObligations(companyId);
  };

  const handleObligationChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedObligation(event.target.value);
  };

  const handleGenerateEmailDraft = async () => {
    if (!selectedCompany || !recipient || !context) {
      setError('Please fill in all required fields');
      return;
    }
    
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const request: EmailDraftRequest = {
        company_id: selectedCompany,
        recipient,
        context,
        obligation_id: selectedObligation || undefined
      };
      
      const data = await createEmailDraft(request);
      
      if (data.error) {
        setError(data.error);
      } else {
        setEmailDraft(data);
        setSuccess('Email draft generated successfully!');
      }
    } catch (error) {
      console.error('Error generating email draft:', error);
      setError('Failed to generate email draft');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyToClipboard = () => {
    if (!emailDraft) return;
    
    const textToCopy = `${emailDraft.subject}\n\n${emailDraft.body}`;
    navigator.clipboard.writeText(textToCopy)
      .then(() => {
        setSuccess('Copied to clipboard!');
        setTimeout(() => setSuccess(null), 3000);
      })
      .catch(() => {
        setError('Failed to copy to clipboard');
      });
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6 flex items-center">
        <Mail className="h-8 w-8 mr-2" />
        AI Email Draft Generator
      </h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Generate Email Draft</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company *
              </label>
              <select
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedCompany}
                onChange={handleCompanyChange}
                required
              >
                <option value="">Select a company</option>
                {companies.map((company) => (
                  <option key={company.id} value={company.id.toString()}>
                    {company.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Obligation (Optional)
              </label>
              <select
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedObligation}
                onChange={handleObligationChange}
                disabled={!selectedCompany}
              >
                <option value="">None</option>
                {obligations.map((obligation) => (
                  <option key={obligation.id} value={obligation.id.toString()}>
                    {obligation.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recipient *
              </label>
              <select
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                required
              >
                <option value="">Select a recipient</option>
                <option value="DGI">DGI (Dirección General de Ingresos)</option>
                <option value="CSS">CSS (Caja de Seguro Social)</option>
                <option value="Municipio">Municipio</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Context *
              </label>
              <textarea
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="E.g., Declaración fuera de tiempo de la planilla de abril"
                required
              />
            </div>
            
            <button
              className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              onClick={handleGenerateEmailDraft}
              disabled={loading || !selectedCompany || !recipient || !context}
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin h-4 w-4 mr-2" />
                  Generating...
                </>
              ) : (
                'Generate Email Draft'
              )}
            </button>
          </div>
        </div>
        
        {emailDraft && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Generated Email Draft</h2>
            
            <div className="mb-4">
              <h3 className="text-md font-medium text-gray-700 mb-1">Subject:</h3>
              <div className="p-2 bg-gray-50 rounded border border-gray-200">
                {emailDraft.subject}
              </div>
            </div>
            
            <div className="mb-4">
              <h3 className="text-md font-medium text-gray-700 mb-1">Body:</h3>
              <div className="p-2 bg-gray-50 rounded border border-gray-200 whitespace-pre-wrap">
                {emailDraft.body}
              </div>
            </div>
            
            <button
              className="flex items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              onClick={handleCopyToClipboard}
            >
              <Copy className="h-4 w-4 mr-2" />
              Copy to Clipboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailDraftPage;
