import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getContract, deleteContract, updateContract } from '../lib/api';
import { Contract } from '../types';
import PageLayout from '../components/layout/PageLayout';

export default function ContractDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contract, setContract] = useState<Contract | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<Partial<Contract>>({});
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (id) {
      fetchContract(parseInt(id));
    }
  }, [id]);

  const fetchContract = async (contractId: number) => {
    setIsLoading(true);
    try {
      const data = await getContract(contractId);
      setContract(data);
      setFormData(data);
      setError('');
    } catch (err) {
      console.error('Error fetching contract:', err);
      setError('Failed to load contract details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !formData) return;

    try {
      const updatedContract = await updateContract(parseInt(id), formData);
      setContract(updatedContract);
      setIsEditing(false);
      setError('');
    } catch (err) {
      console.error('Error updating contract:', err);
      setError('Failed to update contract');
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    
    setIsDeleting(true);
    try {
      await deleteContract(parseInt(id));
      navigate('/contracts');
    } catch (err) {
      console.error('Error deleting contract:', err);
      setError('Failed to delete contract');
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading contract details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {error}
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
        Contract not found
      </div>
    );
  }

  return (
    <PageLayout title={contract.title}>
      <div className="mb-6 flex justify-between items-center">
        <div>
          <Link to="/contracts" className="text-blue-500 hover:underline mb-2 inline-block">
            &larr; Back to Contracts
          </Link>
        </div>
        <div className="flex space-x-2">
          {!isEditing ? (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Edit Contract
              </button>
              <button
                onClick={handleDelete}
                className={`px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 ${
                  isDeleting ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Delete Contract'}
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsEditing(false)}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Cancel Editing
            </button>
          )}
        </div>
      </div>

      {isEditing ? (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Edit Contract</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title || ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Client Name
                </label>
                <input
                  type="text"
                  name="client_name"
                  value={formData.client_name || ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contract Type
                </label>
                <input
                  type="text"
                  name="contract_type"
                  value={formData.contract_type || ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Responsible Lawyer
                </label>
                <input
                  type="text"
                  name="responsible_lawyer"
                  value={formData.responsible_lawyer || ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  name="start_date"
                  value={formData.start_date ? formData.start_date.split('T')[0] : ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expiration Date
                </label>
                <input
                  type="date"
                  name="expiration_date"
                  value={formData.expiration_date ? formData.expiration_date.split('T')[0] : ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  name="status"
                  value={formData.status || ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  required
                >
                  <option value="active">Active</option>
                  <option value="expired">Expired</option>
                  <option value="terminated">Terminated</option>
                </select>
              </div>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description || ''}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                rows={4}
              />
            </div>
            
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Save Changes
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">Contract Information</h3>
              <div className="space-y-3">
                <div>
                  <span className="text-gray-600 font-medium">Client:</span>
                  <p>{contract.client_name}</p>
                </div>
                <div>
                  <span className="text-gray-600 font-medium">Type:</span>
                  <p>{contract.contract_type}</p>
                </div>
                <div>
                  <span className="text-gray-600 font-medium">Responsible Lawyer:</span>
                  <p>{contract.responsible_lawyer}</p>
                </div>
                <div>
                  <span className="text-gray-600 font-medium">Status:</span>
                  <p className="capitalize">{contract.status}</p>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Dates</h3>
              <div className="space-y-3">
                <div>
                  <span className="text-gray-600 font-medium">Start Date:</span>
                  <p>{formatDate(contract.start_date)}</p>
                </div>
                <div>
                  <span className="text-gray-600 font-medium">Expiration Date:</span>
                  <p>{formatDate(contract.expiration_date)}</p>
                </div>
                <div>
                  <span className="text-gray-600 font-medium">Created:</span>
                  <p>{formatDate(contract.created_at)}</p>
                </div>
                {contract.updated_at && (
                  <div>
                    <span className="text-gray-600 font-medium">Last Updated:</span>
                    <p>{formatDate(contract.updated_at)}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {contract.description && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">Description</h3>
              <p className="text-gray-700">{contract.description}</p>
            </div>
          )}
          
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Document</h3>
            <a
              href={`http://localhost:8000/${contract.file_path}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
            >
              View Document
            </a>
          </div>
        </div>
      )}
    </PageLayout>
  );
}
