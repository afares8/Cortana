import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, AlertCircle, Clock, CheckCircle, XCircle, ArrowLeft, Truck, Tag, DollarSign, Package, Download } from 'lucide-react';
import { getSubmissionLog } from '../api/trafficApi';
import { TrafficSubmission } from '../types';

const SubmissionDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [submission, setSubmission] = useState<TrafficSubmission | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchSubmission(parseInt(id));
    }
  }, [id]);

  const fetchSubmission = async (submissionId: number) => {
    try {
      setIsLoading(true);
      const data = await getSubmissionLog(submissionId);
      setSubmission(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching submission:', err);
      setError('Error al cargar los detalles del envío. Por favor, inténtelo de nuevo.');
    } finally {
      setIsLoading(false);
    }
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
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'Failed':
        return <XCircle className="h-6 w-6 text-red-600" />;
      case 'Pending':
        return <Clock className="h-6 w-6 text-yellow-600" />;
      default:
        return <AlertCircle className="h-6 w-6 text-gray-600" />;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Detalles del Envío {submission ? `#${submission.id}` : ''}
        </h1>
        <div className="flex space-x-2">
          <button
            onClick={() => navigate('/traffic/logs')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver al Historial
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
      
      {isLoading ? (
        <div className="py-8 text-center text-gray-500">
          <Clock className="h-8 w-8 mx-auto mb-2 animate-spin" />
          <p>Cargando detalles del envío...</p>
        </div>
      ) : submission ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200 mb-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Información de Envío DMCE</h2>
                  <p className="text-gray-500 text-sm">
                    Enviado el {new Date(submission.submission_date).toLocaleDateString()} a las {new Date(submission.submission_date).toLocaleTimeString()}
                  </p>
                </div>
                <div className="flex items-center">
                  {getStatusIcon(submission.status)}
                  <span className={`ml-2 px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(submission.status)}`}>
                    {submission.status}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Número DMCE</h3>
                  <p className="text-gray-900 font-medium">{submission.dmce_number || 'Pendiente'}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Fecha de Envío</h3>
                  <p className="text-gray-900">{new Date(submission.submission_date).toLocaleDateString()}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Cliente</h3>
                  <p className="text-gray-900">{submission.client_name}</p>
                  <p className="text-sm text-gray-500">ID: {submission.client_id}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Tipo de Movimiento</h3>
                  <p className="text-gray-900">{submission.movement_type === 'Exit' ? 'Salida' : 'Transferencia'}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Valor Total</h3>
                  <p className="text-gray-900">${submission.total_value.toFixed(2)}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Peso Total</h3>
                  <p className="text-gray-900">{submission.total_weight.toFixed(2)} kg</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Total de Artículos</h3>
                  <p className="text-gray-900">{submission.total_items}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Consolidado</h3>
                  <p className="text-gray-900">{submission.is_consolidated ? 'Sí' : 'No'}</p>
                </div>
              </div>
              
              {submission.error_message && (
                <div className="bg-red-50 p-4 rounded-md mb-6">
                  <h3 className="text-sm font-medium text-red-700 mb-2">Error de Envío</h3>
                  <p className="text-sm text-red-600">
                    {submission.error_message}
                  </p>
                </div>
              )}
              
              {submission.is_consolidated && submission.original_invoice_ids && submission.original_invoice_ids.length > 0 && (
                <div className="bg-blue-50 p-4 rounded-md mb-6">
                  <h3 className="text-sm font-medium text-blue-700 mb-2">Facturas Consolidadas</h3>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {submission.original_invoice_ids.map(origId => (
                      <span key={origId} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                        #{origId}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Facturas Incluidas</h3>
              
              {submission.invoice_records && submission.invoice_records.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Factura</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valor</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Peso</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Artículos</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {submission.invoice_records.map((record) => (
                        <tr key={record.id} className="hover:bg-gray-50">
                          <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{record.invoice_number}</td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(record.invoice_date).toLocaleDateString()}
                          </td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">${record.total_value.toFixed(2)}</td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">{record.total_weight.toFixed(2)} kg</td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">{record.items.length}</td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                            <button
                              onClick={() => navigate(`/traffic/record/${record.id}`)}
                              className="text-blue-600 hover:text-blue-800 flex items-center"
                            >
                              <FileText className="h-4 w-4 mr-1" />
                              Ver Detalles
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 italic">No hay facturas asociadas a este envío.</p>
              )}
            </div>
          </div>
          
          <div className="lg:col-span-1">
            <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Acciones</h2>
              
              <div className="space-y-4">
                {submission.dmce_number && (
                  <button
                    className="w-full px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 flex items-center justify-center"
                  >
                    <Download className="h-5 w-5 mr-2" />
                    Descargar DMCE
                  </button>
                )}
                
                <button
                  onClick={() => navigate(`/traffic/records`)}
                  className="w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center justify-center"
                >
                  <FileText className="h-5 w-5 mr-2" />
                  Ver Todos los Registros
                </button>
              </div>
              
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Resumen</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center">
                    <div className="bg-blue-100 p-2 rounded-full mr-3">
                      <Tag className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Total de Artículos</p>
                      <p className="text-lg font-semibold text-gray-900">{submission.total_items}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <div className="bg-green-100 p-2 rounded-full mr-3">
                      <DollarSign className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Valor Total</p>
                      <p className="text-lg font-semibold text-gray-900">${submission.total_value.toFixed(2)}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <div className="bg-yellow-100 p-2 rounded-full mr-3">
                      <Package className="h-5 w-5 text-yellow-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Peso Total</p>
                      <p className="text-lg font-semibold text-gray-900">{submission.total_weight.toFixed(2)} kg</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200 text-center">
          <AlertCircle className="h-12 w-12 mx-auto mb-4 text-red-500" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Envío No Encontrado</h2>
          <p className="text-gray-500 mb-4">
            No se pudo encontrar el envío solicitado. Es posible que haya sido eliminado o que no tenga permisos para verlo.
          </p>
          <button
            onClick={() => navigate('/traffic/logs')}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Volver al Historial
          </button>
        </div>
      )}
    </div>
  );
};

export default SubmissionDetail;
