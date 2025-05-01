import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createContract } from '../lib/api';
import PageLayout from '../components/layout/PageLayout';

export default function ContractUpload() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    client_name: '',
    contract_type: '',
    start_date: '',
    expiration_date: '',
    responsible_lawyer: '',
    description: '',
  });
  const [file, setFile] = useState<File | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    const uploadData = new FormData();
    uploadData.append('file', file);
    
    Object.entries(formData).forEach(([key, value]) => {
      uploadData.append(key, value);
    });
    
    try {
      const response = await createContract(uploadData);
      navigate(`/contracts/${response.id}`);
    } catch (err: any) {
      console.error('Error uploading contract:', err);
      setError(err.response?.data?.detail || 'Failed to upload contract');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageLayout title="Upload New Contract">
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contract Title *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Client Name *
              </label>
              <input
                type="text"
                name="client_name"
                value={formData.client_name}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contract Type *
              </label>
              <input
                type="text"
                name="contract_type"
                value={formData.contract_type}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="e.g., Service Agreement, NDA, Employment"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Responsible Lawyer *
              </label>
              <input
                type="text"
                name="responsible_lawyer"
                value={formData.responsible_lawyer}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date *
              </label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expiration Date *
              </label>
              <input
                type="date"
                name="expiration_date"
                value={formData.expiration_date}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded"
              rows={4}
              placeholder="Additional details about the contract..."
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Upload Contract Document *
            </label>
            <input
              type="file"
              onChange={handleFileChange}
              className="w-full p-2 border border-gray-300 rounded"
              accept=".pdf,.doc,.docx,.txt"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Accepted formats: PDF, DOC, DOCX, TXT
            </p>
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => navigate('/contracts')}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 mr-2"
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              disabled={isLoading}
            >
              {isLoading ? 'Uploading...' : 'Upload Contract'}
            </button>
          </div>
        </form>
      </div>
    </PageLayout>
  );
}
