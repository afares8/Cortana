import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, AlertCircle, Clock, CheckCircle, ArrowRight, Truck, Tag, DollarSign, Package } from 'lucide-react';
import { getRecord, submitToDMCE } from '../api/trafficApi';
import { InvoiceRecord, SubmissionRequest } from '../types';
import DMCEManualLogin from '../components/DMCEManualLogin';

const RecordDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [record, setRecord] = useState<InvoiceRecord | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [showManualLogin, setShowManualLogin] = useState(false);

  useEffect(() => {
    if (id) {
      fetchRecord(parseInt(id));
    }
  }, [id]);

  const fetchRecord = async (recordId: number) => {
    try {
      setIsLoading(true);
      const data = await getRecord(recordId);
      setRecord(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching record:', err);
      setError('Error al cargar los detalles del registro. Por favor, inténtelo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!record || !id) return;
    
    if (record.status === 'Submitted') {
      setSubmitError('Este registro ya ha sido enviado al portal DMCE.');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setSubmitError(null);
      setSubmitSuccess(null);
      
      const request: SubmissionRequest = {
        record_id: parseInt(id)
      };
      
      const response = await submitToDMCE(request);
      
      if (response.success) {
        setSubmitSuccess(`Registro enviado exitosamente al portal DMCE. Número DMCE: ${response.dmce_number || 'Pendiente'}`);
        fetchRecord(parseInt(id));
      } else {
        if (response.error && response.error.includes('login')) {
          setSubmitError('Error de inicio de sesión en el portal DMCE. Se requiere inicio de sesión manual.');
          setShowManualLogin(true);
        } else {
          setSubmitError('Error al enviar al portal DMCE: ' + response.message);
        }
      }
    } catch (err) {
      console.error('Error submitting to DMCE:', err);
      
      setSubmitError('Error al enviar al portal DMCE. Se intentará inicio de sesión manual.');
      setShowManualLogin(true);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleManualLoginSuccess = () => {
    setShowManualLogin(false);
    setTimeout(() => {
      handleSubmit();
    }, 1000);
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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Detalles del Registro {record ? `#${record.id}` : ''}
        </h1>
        <div className="flex space-x-2">
          <button
            onClick={() => navigate('/traffic/records')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Volver a Registros
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
          <p>Cargando detalles del registro...</p>
        </div>
      ) : record ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200 mb-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Información de Factura</h2>
                  <p className="text-gray-500 text-sm">
                    Subido el {new Date(record.upload_date).toLocaleDateString()} a las {new Date(record.upload_date).toLocaleTimeString()}
                  </p>
                </div>
                <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(record.status)}`}>
                  {record.status}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Número de Factura</h3>
                  <p className="text-gray-900">{record.invoice_number}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Fecha de Factura</h3>
                  <p className="text-gray-900">{new Date(record.invoice_date).toLocaleDateString()}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Cliente</h3>
                  <p className="text-gray-900">{record.client_name}</p>
                  <p className="text-sm text-gray-500">ID: {record.client_id}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Tipo de Movimiento</h3>
                  <p className="text-gray-900">{record.movement_type === 'Exit' ? 'Salida' : 'Transferencia'}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Valor Total</h3>
                  <p className="text-gray-900">${record.total_value.toFixed(2)}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Peso Total</h3>
                  <p className="text-gray-900">{record.total_weight.toFixed(2)} kg</p>
                </div>
              </div>
              
              {record.is_consolidated && (
                <div className="bg-blue-50 p-4 rounded-md mb-6">
                  <h3 className="text-sm font-medium text-blue-700 mb-2">Registro Consolidado</h3>
                  <p className="text-sm text-blue-600">
                    Este registro es una consolidación de múltiples facturas.
                  </p>
                  {record.original_invoice_ids && record.original_invoice_ids.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-blue-700">Facturas originales:</p>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {record.original_invoice_ids.map(origId => (
                          <span key={origId} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                            #{origId}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {record.consolidated_into_id && (
                <div className="bg-yellow-50 p-4 rounded-md mb-6">
                  <h3 className="text-sm font-medium text-yellow-700 mb-2">Registro Consolidado en Otro</h3>
                  <p className="text-sm text-yellow-600">
                    Este registro ha sido consolidado en el registro #{record.consolidated_into_id}.
                  </p>
                  <button
                    onClick={() => navigate(`/traffic/record/${record.consolidated_into_id}`)}
                    className="mt-2 text-sm font-medium text-yellow-700 hover:text-yellow-800 flex items-center"
                  >
                    Ver Registro Consolidado
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </button>
                </div>
              )}
              
              {record.ai_suggestions && record.ai_suggestions.length > 0 && (
                <div className="bg-purple-50 p-4 rounded-md mb-6">
                  <h3 className="text-sm font-medium text-purple-700 mb-2">Sugerencias de IA</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {record.ai_suggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-purple-600">
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {record.validation_errors && Object.keys(record.validation_errors).length > 0 && (
                <div className="bg-red-50 p-4 rounded-md mb-6">
                  <h3 className="text-sm font-medium text-red-700 mb-2">Errores de Validación</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {Object.entries(record.validation_errors).map(([field, error], index) => (
                      <li key={index} className="text-sm text-red-600">
                        <span className="font-medium">{field}:</span> {error as string}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Artículos</h3>
              
              {record.items.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cantidad</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unidad</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Peso</th>
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valor</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {record.items.map((item) => (
                        <tr key={item.id} className="hover:bg-gray-50">
                          <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.tariff_code}</td>
                          <td className="px-3 py-4 text-sm text-gray-500">{item.description}</td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">{item.quantity}</td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">{item.unit}</td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">{item.weight} kg</td>
                          <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">${item.value.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 italic">No hay artículos en este registro.</p>
              )}
            </div>
          </div>
          
          <div className="lg:col-span-1">
            <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Acciones</h2>
              
              {submitSuccess && (
                <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
                  <div className="flex items-center">
                    <CheckCircle className="h-5 w-5 mr-2" />
                    <p>{submitSuccess}</p>
                  </div>
                </div>
              )}
              
              {submitError && (
                <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
                  <div className="flex items-center">
                    <AlertCircle className="h-5 w-5 mr-2" />
                    <p>{submitError}</p>
                  </div>
                </div>
              )}
              
              <div className="space-y-4">
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting || record.status === 'Submitted' || record.consolidated_into_id !== undefined}
                  className={`w-full px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 flex items-center justify-center ${
                    isSubmitting || record.status === 'Submitted' || record.consolidated_into_id !== undefined
                      ? 'opacity-70 cursor-not-allowed'
                      : ''
                  }`}
                >
                  {isSubmitting ? (
                    <>
                      <span className="mr-2">Enviando...</span>
                      <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                    </>
                  ) : (
                    <>
                      <Truck className="h-5 w-5 mr-2" />
                      Enviar al Portal DMCE
                    </>
                  )}
                </button>
                
                {record.status === 'Submitted' && record.submission_id && (
                  <button
                    onClick={() => navigate(`/traffic/logs/${record.submission_id}`)}
                    className="w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center justify-center"
                  >
                    <FileText className="h-5 w-5 mr-2" />
                    Ver Detalles de Envío
                  </button>
                )}
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
                      <p className="text-lg font-semibold text-gray-900">{record.items.length}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <div className="bg-green-100 p-2 rounded-full mr-3">
                      <DollarSign className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Valor Total</p>
                      <p className="text-lg font-semibold text-gray-900">${record.total_value.toFixed(2)}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <div className="bg-yellow-100 p-2 rounded-full mr-3">
                      <Package className="h-5 w-5 text-yellow-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Peso Total</p>
                      <p className="text-lg font-semibold text-gray-900">{record.total_weight.toFixed(2)} kg</p>
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
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Registro No Encontrado</h2>
          <p className="text-gray-500 mb-4">
            No se pudo encontrar el registro solicitado. Es posible que haya sido eliminado o que no tenga permisos para verlo.
          </p>
          <button
            onClick={() => navigate('/traffic/records')}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Volver a Registros
          </button>
        </div>
      )}
      
      {/* Manual Login Popup */}
      <DMCEManualLogin
        open={showManualLogin}
        onClose={() => setShowManualLogin(false)}
        onSuccess={handleManualLoginSuccess}
      />
    </div>
  );
};

export default RecordDetail;
