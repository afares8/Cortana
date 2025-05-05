import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, AlertCircle, Clock, CheckCircle, XCircle, ChevronRight, Search, RefreshCw, Calendar } from 'lucide-react';
import { getSubmissionLogs } from '../api/trafficApi';
import { TrafficSubmission } from '../types';

const SubmissionLogs = () => {
  const navigate = useNavigate();
  const [logs, setLogs] = useState<TrafficSubmission[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<TrafficSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    client: '',
    movementType: '',
    startDate: '',
    endDate: ''
  });

  useEffect(() => {
    fetchLogs();
  }, []);

  useEffect(() => {
    filterLogs();
  }, [logs, searchQuery, filters]);

  const fetchLogs = async () => {
    try {
      setIsLoading(true);
      const data = await getSubmissionLogs();
      setLogs(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching submission logs:', err);
      setError('Error al cargar el historial de envíos. Por favor, inténtelo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const filterLogs = () => {
    let filtered = [...logs];
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(log => 
        (log.dmce_number && log.dmce_number.toLowerCase().includes(query)) ||
        log.client_name.toLowerCase().includes(query) ||
        log.client_id.toLowerCase().includes(query)
      );
    }
    
    if (filters.status) {
      filtered = filtered.filter(log => log.status === filters.status);
    }
    
    if (filters.client) {
      filtered = filtered.filter(log => log.client_name === filters.client);
    }
    
    if (filters.movementType) {
      filtered = filtered.filter(log => log.movement_type === filters.movementType);
    }
    
    if (filters.startDate) {
      const startDate = new Date(filters.startDate);
      filtered = filtered.filter(log => new Date(log.submission_date) >= startDate);
    }
    
    if (filters.endDate) {
      const endDate = new Date(filters.endDate);
      endDate.setHours(23, 59, 59, 999);
      filtered = filtered.filter(log => new Date(log.submission_date) <= endDate);
    }
    
    setFilteredLogs(filtered);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Submitted':
        return 'text-green-600 bg-green-100';
      case 'Failed':
        return 'text-red-600 bg-red-100';
      case 'Pending':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Submitted':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'Failed':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'Pending':
        return <Clock className="h-5 w-5 text-yellow-600" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />;
    }
  };

  const getUniqueClients = () => {
    const clients = new Set<string>();
    logs.forEach(log => clients.add(log.client_name));
    return Array.from(clients);
  };

  const getUniqueMovementTypes = () => {
    const types = new Set<string>();
    logs.forEach(log => types.add(log.movement_type));
    return Array.from(types);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Historial de Envíos DMCE</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => navigate('/traffic/dashboard')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Volver al Panel
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
      
      <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 space-y-4 md:space-y-0">
          <div className="relative w-full md:w-64">
            <input
              type="text"
              placeholder="Buscar por DMCE o cliente..."
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
              <option value="Submitted">Enviado</option>
              <option value="Failed">Fallido</option>
              <option value="Pending">Pendiente</option>
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
            
            <div className="flex items-center">
              <div className="flex items-center mr-2">
                <Calendar className="h-4 w-4 mr-1 text-gray-500" />
                <span className="text-sm text-gray-500">Desde:</span>
              </div>
              <input
                type="date"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filters.startDate}
                onChange={(e) => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
              />
            </div>
            
            <div className="flex items-center">
              <div className="flex items-center mr-2">
                <Calendar className="h-4 w-4 mr-1 text-gray-500" />
                <span className="text-sm text-gray-500">Hasta:</span>
              </div>
              <input
                type="date"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filters.endDate}
                onChange={(e) => setFilters(prev => ({ ...prev, endDate: e.target.value }))}
              />
            </div>
            
            <button
              onClick={fetchLogs}
              className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              Actualizar
            </button>
          </div>
        </div>
        
        {isLoading ? (
          <div className="py-8 text-center text-gray-500">
            <Clock className="h-8 w-8 mx-auto mb-2 animate-spin" />
            <p>Cargando historial...</p>
          </div>
        ) : filteredLogs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DMCE</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valor</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Artículos</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-3 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(log.status)}
                        <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(log.status)}`}>
                          {log.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {log.dmce_number || 'Pendiente'}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{log.client_name}</div>
                      <div className="text-xs text-gray-400">{log.client_id}</div>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(log.submission_date).toLocaleDateString()}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.movement_type === 'Exit' ? 'Salida' : 'Transferencia'}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      ${log.total_value.toFixed(2)}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.total_items}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button
                        onClick={() => navigate(`/traffic/logs/${log.id}`)}
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
            <p>No se encontraron registros de envíos</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubmissionLogs;
