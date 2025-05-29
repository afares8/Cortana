import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Code2, Plus, Edit, Trash2 } from 'lucide-react';
import { Function } from '../types';
import { getFunctions } from '../api/adminApi';

const FunctionsPage: React.FC = () => {
  const { t } = useTranslation();
  const [functions, setFunctions] = useState<Function[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedFunction, setSelectedFunction] = useState<Function | null>(null);

  useEffect(() => {
    const fetchFunctions = async () => {
      try {
        setLoading(true);
        const data = await getFunctions();
        setFunctions(data);
        setError(null);
      } catch (err) {
        setError('Failed to load functions');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchFunctions();
  }, []);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this function?')) {
      try {
        setFunctions(functions.filter(func => func.id !== id));
      } catch (err) {
        setError('Failed to delete function');
        console.error(err);
      }
    }
  };

  const handleEdit = (func: Function) => {
    setSelectedFunction(func);
    setShowCreateModal(true);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <Code2 className="h-8 w-8 mr-3 text-blue-600" />
          <h1 className="text-2xl font-bold">Department Functions</h1>
        </div>
        <button
          onClick={() => {
            setSelectedFunction(null);
            setShowCreateModal(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Function
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : functions.length === 0 ? (
        <div className="bg-gray-100 p-8 rounded-lg text-center">
          <Code2 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Functions Found</h2>
          <p className="text-gray-600 mb-4">
            Create your first department function to enable business automation.
          </p>
          <button
            onClick={() => {
              setSelectedFunction(null);
              setShowCreateModal(true);
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-md inline-flex items-center"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create Function
          </button>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Department
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Schema
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {functions.map((func) => (
                <tr key={func.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {func.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{func.description}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">Department {func.department_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-800"
                      onClick={() => {
                      }}
                    >
                      View Schema
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => handleEdit(func)}
                      className="text-indigo-600 hover:text-indigo-900 mr-4"
                    >
                      <Edit className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(func.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Function Form Modal would be implemented here */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">
              {selectedFunction ? 'Edit Function' : 'Create Function'}
            </h2>
            {/* Function form would be implemented here */}
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="bg-gray-300 text-gray-800 px-4 py-2 rounded-md mr-2"
              >
                Cancel
              </button>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md">
                {selectedFunction ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FunctionsPage;
