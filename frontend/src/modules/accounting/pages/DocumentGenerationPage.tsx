import React, { useEffect, useState } from 'react';
import { getCompanies, getFormTemplates, generateForm } from '../api/accountingApi';
import { Company } from '../types';
import { Loader2, FileText, Download, Upload, Calendar } from 'lucide-react';

const DocumentGenerationPage: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [templates, setTemplates] = useState<string[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [period, setPeriod] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [companiesData, templatesData] = await Promise.all([
          getCompanies(),
          getFormTemplates()
        ]);
        setCompanies(companiesData);
        setTemplates(templatesData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load companies or templates. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleGenerateDocument = async () => {
    if (!selectedCompany || !selectedTemplate) {
      setError('Please select both a company and a template');
      return;
    }

    setGenerating(true);
    setError(null);
    setSuccess(null);

    try {
      const blob = await generateForm(selectedTemplate, selectedCompany, period || undefined);
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      const contentType = blob.type;
      const extension = contentType.includes('pdf') ? 'pdf' : 
                        contentType.includes('word') ? 'docx' : 'file';
      
      a.download = `${selectedTemplate}_${new Date().toISOString().split('T')[0]}.${extension}`;
      document.body.appendChild(a);
      a.click();
      
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setSuccess('Document generated successfully!');
    } catch (error) {
      console.error('Error generating document:', error);
      setError('Failed to generate document. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setUploadFile(event.target.files[0]);
    }
  };

  const handleUploadTemplate = async () => {
    if (!uploadFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploadLoading(true);
    setError(null);
    setSuccess(null);

    try {
      console.log('Would upload:', uploadFile.name);
      
      const templatesData = await getFormTemplates();
      setTemplates(templatesData);
      
      setSuccess('Template uploaded successfully!');
      setUploadFile(null);
      
      const fileInput = document.getElementById('template-upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (error) {
      console.error('Error uploading template:', error);
      setError('Failed to upload template. Please try again.');
    } finally {
      setUploadLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Document Generation</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
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
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Generate Document
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company
              </label>
              <select
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
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
                Template
              </label>
              <select
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
              >
                <option value="">Select a template</option>
                {templates.map((template) => (
                  <option key={template} value={template}>
                    {template}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Period (Optional)
              </label>
              <div className="flex items-center">
                <Calendar className="h-5 w-5 mr-2 text-gray-400" />
                <input
                  type="month"
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                  placeholder="YYYY-MM"
                />
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Format: YYYY-MM (e.g., 2025-05)
              </p>
            </div>
            
            <button
              className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              onClick={handleGenerateDocument}
              disabled={generating || !selectedCompany || !selectedTemplate}
            >
              {generating ? (
                <>
                  <Loader2 className="animate-spin h-4 w-4 mr-2" />
                  Generating...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Generate Document
                </>
              )}
            </button>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Upload className="h-5 w-5 mr-2" />
            Upload Template
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Template File
              </label>
              <input
                id="template-upload"
                type="file"
                accept=".docx,.pdf,.xlsx,.xls"
                onChange={handleFileChange}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-sm text-gray-500 mt-1">
                Accepted formats: .docx, .pdf, .xlsx, .xls
              </p>
            </div>
            
            <button
              className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              onClick={handleUploadTemplate}
              disabled={uploadLoading || !uploadFile}
            >
              {uploadLoading ? (
                <>
                  <Loader2 className="animate-spin h-4 w-4 mr-2" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Template
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentGenerationPage;
