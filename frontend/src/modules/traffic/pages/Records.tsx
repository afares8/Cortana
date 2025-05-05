import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, CheckSquare, AlertCircle, Clock, ChevronRight, Search, RefreshCw } from 'lucide-react';
import { getRecords, consolidateInvoices } from '../api/trafficApi';
import { InvoiceRecord, ConsolidationRequest } from '../types';

const Records = () => {
  const navigate = useNavigate();
  const [records, setRecords] = useState<InvoiceRecord[]>([]);
  const [filteredRecords, setFilteredRecords] = useState<InvoiceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRecords, setSelectedRecords] = useState<number[]>([]);
  const [isConsolidating, setIsConsolidating] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    client: '',
    movementType: ''
  });

  useEffect(() => {
    fetchRecords();
  }, []);

  useEffect(() => {
    filterRecords();
  }, [records, searchQuery, filters]);

  const fetchRecords = async () => {
    try {
      setIsLoading(true);
      const data = await getRecords();
      setRecords(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching records:', err);
      setError('Error al cargar los registros. Por favor, inténtelo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const filterRecords = () => {
    let filtered = [...records];
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(record => 
        record.invoice_number.toLowerCase().includes(query) ||
        record.client_name.toLowerCase().includes(query) ||
        record.client_id.toLowerCase().includes(query)
      );
    }
    
    if (filters.status) {
      filtered = filtered.filter(record => record.status === filters.status);
    }
    
    if (filters.client) {
      filtered = filtered.filter(record => record.client_name === filters.client);
    }
    
    if (filters.movementType) {
      filtered = filtered.filter(record => record.movement_type === filters.movementType);
    }
    
    setFilteredRecords(filtered);
  };

  const handleSelectRecord = (id: number) => {
    setSelectedRecords(prev => {
      if (prev.includes(id)) {
        return prev.filter(recordId => recordId !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedRecords.length === filteredRecords.length) {
      setSelectedRecords([]);
    } else {
      setSelectedRecords(filteredRecords.map(record => record.id));
    }
  };

  const handleConsolidate = async () => {
    if (selectedRecords.length < 2) {
      setError('Seleccione al menos dos registros para consolidar.');
      return;
    }
    
    const firstRecord = records.find(r => r.id === selectedRecords[0]);
    if (!firstRecord) return;
    
    const allSameClient = selectedRecords.every(id => {
      const record = records.find(r => r.id === id);
      return record && record.client_id === firstRecord.client_id;
    });
    
    const allSameMovementType = selectedRecords.every(id => {
      const record = records.find(r => r.id === id);
      return record && record.movement_type === firstRecord.movement_type;
    });
    
    if (!allSameClient) {
      setError('Todos los registros seleccionados deben pertenecer al mismo cliente.');
      return;
    }
    
    if (!allSameMovementType) {
      setError('Todos los registros seleccionados deben tener el mismo tipo de movimiento.');
      return;
    }
    
    try {
      setIsConsolidating(true);
      setError(null);
      
      const request: ConsolidationRequest = {
        invoice_record_ids: selectedRecords
      };
      
      const response = await consolidateInvoices(request);
      
      if (response.success) {
        setSuccess(`Registros consolidados exitosamente en el registro #${response.consolidated_record.id}`);
        fetchRecords(); // Refresh the records
        setSelectedRecords([]);
      } else {
        setError('Error al consolidar registros: ' + response.message);
      }
    } catch (err) {
      console.error('Error consolidating records:', err);
      setError('Error al consolidar registros. Por favor, inténtelo de nuevo.');
    } finally {
      setIsConsolidating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Validated':
        return 'text-green-600 bg-green-100';
      case 'Error':
        return 'text-red-600 bg-red-100';
      case 'Consolidated':
        return 'text-blue-600 bg-blue-100';
      case 'Submitted':
        return 'text-purple-600 bg-purple-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getUniqueClients = () => {
    const clients = new Set<string>();
    records.forEach(record => clients.add(record.client_name));
    return Array.from(clients);
  };

  const getUniqueMovementTypes = () => {
    const types = new Set<string>();
    records.forEach(record => types.add(record.movement_type));
    return Array.from(types);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Registros de Facturas</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => navigate('/traffic/dashboard')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Volver al Panel
          </button>
          <button
            onClick={() => navigate('/traffic/upload')}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Cargar Nueva Factura
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 mr-2" />
            <p>{error}</p>
          </div>
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
          <div className="flex items-center">
            <CheckSquare className="h-5 w-5 mr-2" />
            <p>{success}</p>
          </div>
        </div>
      )}
      
      <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 space-y-4 md:space-y-0">
          <div className="relative w-full md:w-64">
            <input
              type="text"
              placeholder="Buscar facturas..."
              className="w-full px-3 py-2 pl-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <select
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
            >
              <option value="">Todos los estados</option>
              <option value="Validated">Validado</option>
              <option value="Error">Error</option>
              <option value="Consolidated">Consolidado</option>
              <option value="Submitted">Enviado</option>
            </select>
            
            <select
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.client}
              onChange={(e) => setFilters(prev => ({ ...prev, client: e.target.value }))}
            >
              <option value="">Todos los clientes</option>
              {getUniqueClients().map(client => (
                <option key={client} value={client}>{client}</option>
              ))}
            </select>
            
            <select
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.movementType}
              onChange={(e) => setFilters(prev => ({ ...prev, movementType: e.target.value }))}
            >
              <option value="">Todos los tipos</option>
              {getUniqueMovementTypes().map(type => (
                <option key={type} value={type}>{type === 'Exit' ? 'Salida' : 'Transferencia'}</option>
              ))}
            </select>
            
            <button
              onClick={fetchRecords}
              className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              Actualizar
            </button>
          </div>
        </div>
        
        {selectedRecords.length > 0 && (
          <div className="bg-blue-50 p-4 rounded-md mb-6 flex justify-between items-center">
            <div>
              <span className="font-medium text-blue-700">{selectedRecords.length} registros seleccionados</span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleConsolidate}
                disabled={isConsolidating || selectedRecords.length < 2}
                className={`px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 flex items-center ${
                  isConsolidating || selectedRecords.length < 2 ? 'opacity-70 cursor-not-allowed' : ''
                }`}
              >
                {isConsolidating ? (
                  <>
                    <span className="mr-2">Consolidando...</span>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  </>
                ) : (
                  'Consolidar Seleccionados'
                )}
              </button>
              <button
                onClick={() => setSelectedRecords([])}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancelar Selección
              </button>
            </div>
          </div>
        )}
        
        {isLoading ? (
          <div className="py-8 text-center text-gray-500">
            <Clock className="h-8 w-8 mx-auto mb-2 animate-spin" />
            <p>Cargando registros...</p>
          </div>
        ) : filteredRecords.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-3 text-left">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedRecords.length === filteredRecords.length && filteredRecords.length > 0}
                        onChange={handleSelectAll}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </div>
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Factura</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valor</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredRecords.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-3 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedRecords.includes(record.id)}
                        onChange={() => handleSelectRecord(record.id)}
                        disabled={record.status === 'Consolidated' || record.status === 'Submitted'}
                        className={`h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded ${
                          record.status === 'Consolidated' || record.status === 'Submitted' ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{record.invoice_number}</td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{record.client_name}</div>
                      <div className="text-xs text-gray-400">{record.client_id}</div>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(record.invoice_date).toLocaleDateString()}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      {record.movement_type === 'Exit' ? 'Salida' : 'Transferencia'}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      ${record.total_value.toFixed(2)}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(record.status)}`}>
                        {record.status}
                      </span>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button
                        onClick={() => navigate(`/traffic/record/${record.id}`)}
                        className="text-blue-600 hover:text-blue-800 flex items-center"
                      >
                        <FileText className="h-4 w-4 mr-1" />
                        Ver
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-gray-500">
            <AlertCircle className="h-8 w-8 mx-auto mb-2" />
            <p>No se encontraron registros</p>
            <button 
              className="mt-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
              onClick={() => navigate('/traffic/upload')}
            >
              Cargar Nueva Factura
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Records;
