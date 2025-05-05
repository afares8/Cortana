import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, AlertCircle, CheckCircle, X } from 'lucide-react';
import { uploadInvoiceData } from '../api/trafficApi';
import { InvoiceDataUpload, InvoiceRecord } from '../types';

const Upload = () => {
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [uploadedRecords, setUploadedRecords] = useState<InvoiceRecord[]>([]);
  const [formData, setFormData] = useState({
    invoice_number: '',
    invoice_date: '',
    client_name: '',
    client_id: '',
    movement_type: 'Exit',
    total_value: '',
    total_weight: '',
    items: [
      {
        tariff_code: '',
        description: '',
        quantity: '',
        unit: 'units',
        weight: '',
        value: '',
        volume: ''
      }
    ]
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleItemChange = (index: number, e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const updatedItems = [...prev.items];
      updatedItems[index] = {
        ...updatedItems[index],
        [name]: value
      };
      return {
        ...prev,
        items: updatedItems
      };
    });
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [
        ...prev.items,
        {
          tariff_code: '',
          description: '',
          quantity: '',
          unit: 'units',
          weight: '',
          value: '',
          volume: ''
        }
      ]
    }));
  };

  const removeItem = (index: number) => {
    if (formData.items.length === 1) {
      return; // Keep at least one item
    }
    
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUploading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const preparedData: InvoiceDataUpload = {
        data: {
          invoice_number: formData.invoice_number,
          invoice_date: formData.invoice_date,
          client_name: formData.client_name,
          client_id: formData.client_id,
          movement_type: formData.movement_type,
          total_value: parseFloat(formData.total_value),
          total_weight: parseFloat(formData.total_weight),
          items: formData.items.map(item => ({
            tariff_code: item.tariff_code,
            description: item.description,
            quantity: parseFloat(item.quantity),
            unit: item.unit,
            weight: parseFloat(item.weight),
            value: parseFloat(item.value),
            volume: item.volume ? parseFloat(item.volume) : undefined
          }))
        }
      };
      
      const response = await uploadInvoiceData(preparedData);
      setUploadedRecords(response);
      setSuccess('Datos de factura cargados exitosamente');
      
      setFormData({
        invoice_number: '',
        invoice_date: '',
        client_name: '',
        client_id: '',
        movement_type: 'Exit',
        total_value: '',
        total_weight: '',
        items: [
          {
            tariff_code: '',
            description: '',
            quantity: '',
            unit: 'units',
            weight: '',
            value: '',
            volume: ''
          }
        ]
      });
      
    } catch (err) {
      console.error('Error uploading invoice data:', err);
      setError('Error al cargar los datos de la factura. Por favor, inténtelo de nuevo.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Cargar Factura</h1>
        <button
          onClick={() => navigate('/traffic/dashboard')}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Volver al Panel
        </button>
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
            <CheckCircle className="h-5 w-5 mr-2" />
            <p>{success}</p>
          </div>
          
          <div className="mt-4">
            <h3 className="font-medium text-green-800 mb-2">Registros Cargados:</h3>
            <ul className="list-disc pl-5">
              {uploadedRecords.map(record => (
                <li key={record.id} className="mb-1">
                  <span className="font-medium">{record.invoice_number}</span> - 
                  <span className="ml-2">{record.client_name}</span>
                  <button
                    onClick={() => navigate(`/traffic/record/${record.id}`)}
                    className="ml-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    Ver Detalles
                  </button>
                </li>
              ))}
            </ul>
            
            <div className="mt-4 flex space-x-4">
              <button
                onClick={() => navigate('/traffic/records')}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Ver Todos los Registros
              </button>
              
              <button
                onClick={() => {
                  setSuccess(null);
                  setUploadedRecords([]);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cargar Otra Factura
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label htmlFor="invoice_number" className="block text-sm font-medium text-gray-700 mb-1">
                Número de Factura
              </label>
              <input
                type="text"
                id="invoice_number"
                name="invoice_number"
                value={formData.invoice_number}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="invoice_date" className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de Factura
              </label>
              <input
                type="date"
                id="invoice_date"
                name="invoice_date"
                value={formData.invoice_date}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="client_name" className="block text-sm font-medium text-gray-700 mb-1">
                Nombre del Cliente
              </label>
              <input
                type="text"
                id="client_name"
                name="client_name"
                value={formData.client_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="client_id" className="block text-sm font-medium text-gray-700 mb-1">
                ID del Cliente
              </label>
              <input
                type="text"
                id="client_id"
                name="client_id"
                value={formData.client_id}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="movement_type" className="block text-sm font-medium text-gray-700 mb-1">
                Tipo de Movimiento
              </label>
              <select
                id="movement_type"
                name="movement_type"
                value={formData.movement_type}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Exit">Salida</option>
                <option value="Transfer">Transferencia</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="total_value" className="block text-sm font-medium text-gray-700 mb-1">
                Valor Total
              </label>
              <input
                type="number"
                id="total_value"
                name="total_value"
                value={formData.total_value}
                onChange={handleChange}
                required
                min="0"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="total_weight" className="block text-sm font-medium text-gray-700 mb-1">
                Peso Total (kg)
              </label>
              <input
                type="number"
                id="total_weight"
                name="total_weight"
                value={formData.total_weight}
                onChange={handleChange}
                required
                min="0"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <h2 className="text-lg font-medium text-gray-900 mb-4">Artículos</h2>
          
          {formData.items.map((item, index) => (
            <div key={index} className="border border-gray-200 rounded-md p-4 mb-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-md font-medium text-gray-700">Artículo {index + 1}</h3>
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="text-gray-500 hover:text-red-500"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label htmlFor={`tariff_code_${index}`} className="block text-sm font-medium text-gray-700 mb-1">
                    Código Arancelario
                  </label>
                  <input
                    type="text"
                    id={`tariff_code_${index}`}
                    name="tariff_code"
                    value={item.tariff_code}
                    onChange={(e) => handleItemChange(index, e)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div className="md:col-span-2">
                  <label htmlFor={`description_${index}`} className="block text-sm font-medium text-gray-700 mb-1">
                    Descripción
                  </label>
                  <input
                    type="text"
                    id={`description_${index}`}
                    name="description"
                    value={item.description}
                    onChange={(e) => handleItemChange(index, e)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label htmlFor={`quantity_${index}`} className="block text-sm font-medium text-gray-700 mb-1">
                    Cantidad
                  </label>
                  <input
                    type="number"
                    id={`quantity_${index}`}
                    name="quantity"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(index, e)}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label htmlFor={`unit_${index}`} className="block text-sm font-medium text-gray-700 mb-1">
                    Unidad
                  </label>
                  <select
                    id={`unit_${index}`}
                    name="unit"
                    value={item.unit}
                    onChange={(e) => handleItemChange(index, e)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="units">Unidades</option>
                    <option value="kg">Kilogramos</option>
                    <option value="liters">Litros</option>
                    <option value="boxes">Cajas</option>
                    <option value="pallets">Paletas</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor={`weight_${index}`} className="block text-sm font-medium text-gray-700 mb-1">
                    Peso (kg)
                  </label>
                  <input
                    type="number"
                    id={`weight_${index}`}
                    name="weight"
                    value={item.weight}
                    onChange={(e) => handleItemChange(index, e)}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label htmlFor={`value_${index}`} className="block text-sm font-medium text-gray-700 mb-1">
                    Valor
                  </label>
                  <input
                    type="number"
                    id={`value_${index}`}
                    name="value"
                    value={item.value}
                    onChange={(e) => handleItemChange(index, e)}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label htmlFor={`volume_${index}`} className="block text-sm font-medium text-gray-700 mb-1">
                    Volumen (opcional)
                  </label>
                  <input
                    type="number"
                    id={`volume_${index}`}
                    name="volume"
                    value={item.volume}
                    onChange={(e) => handleItemChange(index, e)}
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          ))}
          
          <div className="mb-6">
            <button
              type="button"
              onClick={addItem}
              className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100"
            >
              + Agregar Artículo
            </button>
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isUploading}
              className={`px-6 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700 flex items-center ${
                isUploading ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {isUploading ? (
                <>
                  <span className="mr-2">Cargando...</span>
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                </>
              ) : (
                <>
                  <UploadIcon className="h-5 w-5 mr-2" />
                  Cargar Factura
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Upload;
