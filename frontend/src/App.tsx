import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';

import Dashboard from './pages/Dashboard';
import ContractList from './pages/ContractList';
import ContractDetail from './pages/ContractDetail';
import ContractUpload from './pages/ContractUpload';

const queryClient = new QueryClient();

if (typeof window !== 'undefined') {
  localStorage.setItem('token', 'dummy-token');
  
  const path = window.location.pathname;
  if (path === '/login' || path === '/register') {
    window.location.href = '/';
  }
}

const RedirectToDashboard = () => {
  useEffect(() => {
    window.location.href = '/';
  }, []);
  
  return null;
};

function App() {
  useEffect(() => {
    localStorage.setItem('token', 'dummy-token');
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Direct redirects for login and register using custom component */}
          <Route path="/login" element={<RedirectToDashboard />} />
          <Route path="/register" element={<RedirectToDashboard />} />
          
          {/* All routes are now public */}
          <Route path="/" element={<Dashboard />} />
          <Route path="/contracts" element={<ContractList />} />
          <Route path="/contracts/:id" element={<ContractDetail />} />
          <Route path="/contracts/upload" element={<ContractUpload />} />
          
          {/* Catch-all redirect to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App
