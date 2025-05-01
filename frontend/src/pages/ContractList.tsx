import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getContracts } from '../lib/api';
import { Contract } from '../types';
import PageLayout from '../components/layout/PageLayout';

export default function ContractList() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [clientName, setClientName] = useState('');
  const [contractType, setContractType] = useState('');
  const [responsibleLawyer, setResponsibleLawyer] = useState('');
  const [status, setStatus] = useState('');

  useEffect(() => {
    fetchContracts();
  }, []);

  const fetchContracts = async (filters = {}) => {
    setIsLoading(true);
    try {
      const data = await getContracts(filters);
      setContracts(data);
      setError('');
    } catch (err) {
      console.error('Error fetching contracts:', err);
      setError('Failed to load contracts');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilter = (e: React.FormEvent) => {
    e.preventDefault();
    const filters: Record<string, string> = {};
    
    if (clientName) filters.client_name = clientName;
    if (contractType) filters.contract_type = contractType;
    if (responsibleLawyer) filters.responsible_lawyer = responsibleLawyer;
    if (status) filters.status = status;
    
    fetchContracts(filters);
  };

  const clearFilters = () => {
    setClientName('');
    setContractType('');
    setResponsibleLawyer('');
    setStatus('');
    fetchContracts();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-red-100 text-red-800';
      case 'terminated':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <PageLayout title="Contracts">
      <div className="flex justify-between items-center mb-6">
        <Link
          to="/contracts/upload"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Upload New Contract
        </Link>
      </div>

      {/* Filter Form */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <h2 className="text-lg font-semibold mb-4">Filter Contracts</h2>
        <form onSubmit={handleFilter} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Client Name
            </label>
            <input
              type="text"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="Search by client name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contract Type
            </label>
            <input
              type="text"
              value={contractType}
              onChange={(e) => setContractType(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="Search by type"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Responsible Lawyer
            </label>
            <input
              type="text"
              value={responsibleLawyer}
              onChange={(e) => setResponsibleLawyer(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="Search by lawyer"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="terminated">Terminated</option>
            </select>
          </div>
          
          <div className="flex space-x-2 md:col-span-2 lg:col-span-4">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Apply Filters
            </button>
            <button
              type="button"
              onClick={clearFilters}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-lg">Loading contracts...</div>
        </div>
      ) : (
        <>
          {/* Contracts Table */}
          {contracts.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white rounded-lg overflow-hidden shadow-md">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="py-3 px-4 text-left">Title</th>
                    <th className="py-3 px-4 text-left">Client</th>
                    <th className="py-3 px-4 text-left">Type</th>
                    <th className="py-3 px-4 text-left">Expiration</th>
                    <th className="py-3 px-4 text-left">Status</th>
                    <th className="py-3 px-4 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {contracts.map((contract) => (
                    <tr key={contract.id} className="hover:bg-gray-50">
                      <td className="py-3 px-4">{contract.title}</td>
                      <td className="py-3 px-4">{contract.client_name}</td>
                      <td className="py-3 px-4">{contract.contract_type}</td>
                      <td className="py-3 px-4">{formatDate(contract.expiration_date)}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(contract.status)}`}>
                          {contract.status.charAt(0).toUpperCase() + contract.status.slice(1)}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <Link
                          to={`/contracts/${contract.id}`}
                          className="text-blue-500 hover:text-blue-700"
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <p className="text-gray-600 mb-4">No contracts found.</p>
              <Link
                to="/contracts/upload"
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Upload Your First Contract
              </Link>
            </div>
          )}
        </>
      )}
    </PageLayout>
  );
}
