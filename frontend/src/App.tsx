import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';

import Dashboard from './pages/Dashboard';
import ContractList from './pages/ContractList';
import ContractDetail from './pages/ContractDetail';
import ContractUpload from './pages/ContractUpload';
import AIDashboard from './pages/AIDashboard';

import ClientList from './modules/legal/pages/ClientList';
import ClientDetail from './modules/legal/pages/ClientDetail';
import LegalContractList from './modules/legal/pages/ContractList';
import LegalContractDetail from './modules/legal/pages/ContractDetail';
import WorkflowList from './modules/legal/pages/WorkflowList';
import WorkflowDetail from './modules/legal/pages/WorkflowDetail';
import TaskList from './modules/legal/pages/TaskList';
import TaskDetail from './modules/legal/pages/TaskDetail';
import AuditLogList from './modules/legal/pages/AuditLogList';

const queryClient = new QueryClient();

if (typeof window !== 'undefined') {
  localStorage.setItem('token', 'dummy-token');
}

function App() {
  useEffect(() => {
    localStorage.setItem('token', 'dummy-token');
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Direct redirects for login and register */}
          <Route path="login" element={<Navigate to="/" replace />} />
          <Route path="register" element={<Navigate to="/" replace />} />
          
          {/* All routes are now public */}
          <Route path="/" element={<Dashboard />} />
          <Route path="contracts" element={<ContractList />} />
          <Route path="contracts/:id" element={<ContractDetail />} />
          <Route path="contracts/upload" element={<ContractUpload />} />
          
          {/* AI features */}
          <Route path="ai-dashboard" element={<AIDashboard />} />
          <Route path="contracts/:id/analyze" element={<ContractDetail />} />
          
          {/* Legal Module Routes */}
          <Route path="legal/clients" element={<ClientList />} />
          <Route path="legal/clients/:id" element={<ClientDetail />} />
          <Route path="legal/contracts" element={<LegalContractList />} />
          <Route path="legal/contracts/:id" element={<LegalContractDetail />} />
          <Route path="legal/workflows" element={<WorkflowList />} />
          <Route path="legal/workflows/:id" element={<WorkflowDetail />} />
          <Route path="legal/tasks" element={<TaskList />} />
          <Route path="legal/tasks/:id" element={<TaskDetail />} />
          <Route path="legal/audit-logs" element={<AuditLogList />} />
          
          {/* Catch-all redirect to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App
