import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginBypass() {
  const navigate = useNavigate();

  useEffect(() => {
    // Simula un token válido
    localStorage.setItem('token', 'fake-token');

    // Simula usuario con permisos totales
    localStorage.setItem(
      'user',
      JSON.stringify({
        id: 1,
        email: 'admin@example.com',
        name: 'Admin Test',
        role: 'superadmin',
        permissions: ['*'],
      })
    );

    // Redirige al dashboard o inicio
    navigate('/');
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-md text-center">
        <h2 className="text-xl font-bold text-gray-800">Autenticación desactivada</h2>
        <p className="mt-4 text-gray-600">Estás entrando automáticamente en modo desarrollo.</p>
        <p className="mt-2 text-gray-400 text-sm">Admin: admin@example.com</p>
      </div>
    </div>
  );
}

