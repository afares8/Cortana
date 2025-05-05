import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Database, BarChart2, Clock, AlertCircle } from 'lucide-react';
import { getRecords, getSubmissionLogs } from '../api/trafficApi';
import { InvoiceRecord, TrafficSubmission } from '../types';

const TrafficDashboard = () => {
  const navigate = useNavigate();
  const [pendingRecords, setPendingRecords] = useState<InvoiceRecord[]>([]);
  const [recentSubmissions, setRecentSubmissions] = useState<TrafficSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const [recordsData, submissionsData] = await Promise.all([
          getRecords({ limit: 5, status: 'Validated' }),
          getSubmissionLogs({ limit: 5 })
        ]);
        
        setPendingRecords(recordsData);
        setRecentSubmissions(submissionsData);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Error al cargar los datos del panel. Por favor, inténtelo de nuevo.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

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

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Panel de Tráfico</h1>
      
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
          <p>{error}</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div 
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => navigate('/traffic/upload')}
        >
          <div className="flex items-center mb-4">
            <div className="bg-blue-100 p-3 rounded-full mr-4">
              <Upload className="h-6 w-6 text-blue-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Cargar Factura</h2>
          </div>
          <p className="text-gray-600">Subir nuevos datos de factura para procesamiento</p>
        </div>
        
        <div 
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => navigate('/traffic/records')}
        >
          <div className="flex items-center mb-4">
            <div className="bg-purple-100 p-3 rounded-full mr-4">
              <FileText className="h-6 w-6 text-purple-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Registros</h2>
          </div>
          <p className="text-gray-600">Ver y gestionar registros de facturas</p>
        </div>
        
        <div 
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => navigate('/traffic/logs')}
        >
          <div className="flex items-center mb-4">
            <div className="bg-green-100 p-3 rounded-full mr-4">
              <Database className="h-6 w-6 text-green-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Historial</h2>
          </div>
          <p className="text-gray-600">Ver historial de presentaciones DMCE</p>
        </div>
        
        <div 
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => navigate('/traffic/stats')}
        >
          <div className="flex items-center mb-4">
            <div className="bg-yellow-100 p-3 rounded-full mr-4">
              <BarChart2 className="h-6 w-6 text-yellow-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Estadísticas</h2>
          </div>
          <p className="text-gray-600">Ver estadísticas y análisis de tráfico</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Facturas Pendientes</h2>
            <button 
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              onClick={() => navigate('/traffic/records')}
            >
              Ver Todos
            </button>
          </div>
          
          {isLoading ? (
            <div className="py-4 text-center text-gray-500">
              <Clock className="h-5 w-5 mx-auto mb-2 animate-spin" />
              <p>Cargando...</p>
            </div>
          ) : pendingRecords.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Factura</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valor</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pendingRecords.map((record) => (
                    <tr 
                      key={record.id} 
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => navigate(`/traffic/record/${record.id}`)}
                    >
                      <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{record.invoice_number}</td>
                      <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">{record.client_name}</td>
                      <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">${record.total_value.toFixed(2)}</td>
                      <td className="px-3 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(record.status)}`}>
                          {record.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-8 text-center text-gray-500">
              <AlertCircle className="h-8 w-8 mx-auto mb-2" />
              <p>No hay facturas pendientes</p>
              <button 
                className="mt-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
                onClick={() => navigate('/traffic/upload')}
              >
                Cargar Nueva Factura
              </button>
            </div>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Presentaciones Recientes</h2>
            <button 
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              onClick={() => navigate('/traffic/logs')}
            >
              Ver Historial
            </button>
          </div>
          
          {isLoading ? (
            <div className="py-4 text-center text-gray-500">
              <Clock className="h-5 w-5 mx-auto mb-2 animate-spin" />
              <p>Cargando...</p>
            </div>
          ) : recentSubmissions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DMCE</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentSubmissions.map((submission) => (
                    <tr 
                      key={submission.id} 
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => navigate(`/traffic/logs/${submission.id}`)}
                    >
                      <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{submission.dmce_number || 'Pendiente'}</td>
                      <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">{submission.client_name}</td>
                      <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(submission.submission_date).toLocaleDateString()}
                      </td>
                      <td className="px-3 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(submission.status)}`}>
                          {submission.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-8 text-center text-gray-500">
              <AlertCircle className="h-8 w-8 mx-auto mb-2" />
              <p>No hay presentaciones recientes</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrafficDashboard;
