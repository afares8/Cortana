import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { login } from '../lib/api';

interface LoginProps {
  onLoginSuccess: () => void;
}

export default function Login({ onLoginSuccess }: LoginProps) {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await login({ username: email, password });
      localStorage.setItem('token', response.access_token);
      onLoginSuccess();
      navigate('/');
    } catch (err) {
      setError(t('auth.errors.invalidCredentials'));
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
          {t('common.enterpriseManagement')}
        </h2>
        <h3 className="text-xl font-medium text-center text-gray-600 mb-6">
          {t('auth.login')}
        </h3>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" 
               role="alert" 
               aria-live="assertive">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              {t('auth.email')}
            </label>
            <input
              id="email"
              type="email"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder={t('auth.email')}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              aria-required="true"
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
              {t('auth.password')}
            </label>
            <input
              id="password"
              type="password"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder={t('auth.password')}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              aria-required="true"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <button
              type="submit"
              className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              disabled={isLoading}
              aria-busy={isLoading}
            >
              {isLoading ? t('common.loading') : t('auth.login')}
            </button>
            <a
              className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800"
              href="/register"
              onClick={(e) => {
                e.preventDefault();
                navigate('/register');
              }}
            >
              {t('auth.register')}
            </a>
          </div>
        </form>
      </div>
    </div>
  );
}
