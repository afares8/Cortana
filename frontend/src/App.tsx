import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';

import Dashboard from './pages/Dashboard';
import ContractList from './pages/ContractList';
import ContractDetail from './pages/ContractDetail';
import ContractUpload from './pages/ContractUpload';

const queryClient = new QueryClient();

function AuthWrapper() {
  useEffect(() => {
    localStorage.setItem('token', 'dummy-token');
  }, []);

  const location = useLocation();
  
  if (location.pathname === '/login' || location.pathname === '/register') {
    return <Navigate to="/" replace />;
  }
  
  return (
    <Routes>
      {/* All routes are now public */}
      <Route path="/" element={<Dashboard />} />
      <Route path="/contracts" element={<ContractList />} />
      <Route path="/contracts/:id" element={<ContractDetail />} />
      <Route path="/contracts/upload" element={<ContractUpload />} />
      
      {/* Catch-all redirect to dashboard */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthWrapper />
      </Router>
    </QueryClientProvider>
  );
}

export default App
