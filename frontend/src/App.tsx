import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';

import Dashboard from './pages/Dashboard';
import ContractList from './pages/ContractList';
import ContractDetail from './pages/ContractDetail';
import ContractUpload from './pages/ContractUpload';
import AIDashboard from './pages/AIDashboard';
import ComplianceDashboard from './pages/ComplianceDashboard';
import UAFReportForm from './pages/UAFReportForm';
import PEPScreeningForm from './pages/PEPScreeningForm';
import SanctionsScreeningForm from './pages/SanctionsScreeningForm';
import ComplianceCheckPage from './pages/ComplianceCheckPage';
import CountryRiskMap from './pages/CountryRiskMap';

import ClientList from './modules/legal/pages/ClientList';
import ClientDetail from './modules/legal/pages/ClientDetail';
import LegalContractList from './modules/legal/pages/ContractList';
import LegalContractDetail from './modules/legal/pages/ContractDetail';
import WorkflowList from './modules/legal/pages/WorkflowList';
import WorkflowDetail from './modules/legal/pages/WorkflowDetail';
import TaskList from './modules/legal/pages/TaskList';
import TaskDetail from './modules/legal/pages/TaskDetail';
import AuditLogList from './modules/legal/pages/AuditLogList';

import UserList from './modules/users/pages/UserList';
import UserForm from './modules/users/pages/UserForm';

import AccountingDashboard from './modules/accounting/pages/AccountingDashboard';
import UserAccessManagement from './modules/accounting/pages/UserAccessManagement';
import NotificationsPage from './modules/accounting/pages/NotificationsPage';
import AuditLogPage from './modules/accounting/pages/AuditLogPage';
import DocumentGenerationPage from './modules/accounting/pages/DocumentGenerationPage';
import EmailDraftPage from './modules/accounting/pages/EmailDraftPage';

import TrafficDashboard from './modules/traffic/pages/Dashboard';
import TrafficUpload from './modules/traffic/pages/Upload';
import TrafficRecords from './modules/traffic/pages/Records';
import TrafficRecordDetail from './modules/traffic/pages/RecordDetail';
import TrafficSubmissionLogs from './modules/traffic/pages/SubmissionLogs';
import TrafficSubmissionDetail from './modules/traffic/pages/SubmissionDetail';

import AdminDashboard from './modules/AdminControlPanel/pages/AdminDashboard';
import DepartmentsPage from './modules/AdminControlPanel/pages/DepartmentsPage';
import RolesPage from './modules/AdminControlPanel/pages/RolesPage';
import FunctionsPage from './modules/AdminControlPanel/pages/FunctionsPage';
import AutomationRulesPage from './modules/AdminControlPanel/pages/AutomationRulesPage';
import AIProfilesPage from './modules/AdminControlPanel/pages/AIProfilesPage';
import TemplatesPage from './modules/AdminControlPanel/pages/TemplatesPage';
import AuditLogsPage from './modules/AdminControlPanel/pages/AuditLogsPage';

import { 
  ArturDashboard, 
  SuggestionsFeed, 
  SimulationView, 
  SimulationDetail,
  InterventionLog, 
  KpiGraphs 
} from './modules/Artur';

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
      <I18nextProvider i18n={i18n}>
        <Router>
          <Routes>
            {/* Direct redirects for login and register */}
            <Route path="login" element={<Navigate to="/" replace />} />
            <Route path="register" element={<Navigate to="/" replace />} />
          
          {/* All routes are now public */}
          <Route path="/" element={<Dashboard />} />
          <Route path="contracts" element={<ContractList />} />
          <Route path="contracts/upload" element={<ContractUpload />} />
          <Route path="contracts/:id" element={<ContractDetail />} />
          
          {/* AI features */}
          <Route path="ai-dashboard" element={<AIDashboard />} />
          <Route path="contracts/:id/analyze" element={<ContractDetail />} />
          
          {/* Compliance Module Routes */}
          <Route path="compliance/dashboard" element={<ComplianceDashboard />} />
          <Route path="compliance/uaf-report/new" element={<UAFReportForm />} />
          <Route path="compliance/reports/:id" element={<ComplianceDashboard />} />
          <Route path="compliance/pep-screening/new" element={<PEPScreeningForm />} />
          <Route path="compliance/pep-screenings/:id" element={<ComplianceDashboard />} />
          <Route path="compliance/sanctions-screening/new" element={<SanctionsScreeningForm />} />
          <Route path="compliance/sanctions-screenings/:id" element={<ComplianceDashboard />} />
          <Route path="compliance/verify-customer" element={<ComplianceCheckPage />} />
          <Route path="compliance/country-risk-map" element={<CountryRiskMap />} />
          
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
          
          {/* User Management Module Routes */}
          <Route path="users" element={<UserList />} key="user-list" />
          <Route path="users/new" element={<UserForm />} key="user-new" />
          <Route path="users/:id" element={<UserForm />} key="user-detail" />
          <Route path="users/:id/edit" element={<UserForm />} key="user-edit" />
          <Route path="users/:id/reset-password" element={<UserForm />} key="user-reset-password" />
          <Route path="users/:id/lock" element={<UserForm />} key="user-lock" />
          <Route path="users/:id/unlock" element={<UserForm />} key="user-unlock" />
          
          {/* Accounting Module Routes */}
          <Route path="accounting/dashboard" element={<AccountingDashboard />} />
          <Route path="accounting/admin/users" element={<UserAccessManagement />} />
          <Route path="accounting/notifications" element={<NotificationsPage />} />
          <Route path="accounting/audit" element={<AuditLogPage />} />
          <Route path="accounting/documents" element={<DocumentGenerationPage />} />
          <Route path="accounting/email-drafts" element={<EmailDraftPage />} />
          
          {/* Traffic Module Routes */}
          <Route path="traffic/dashboard" element={<TrafficDashboard />} />
          <Route path="traffic/upload" element={<TrafficUpload />} />
          <Route path="traffic/records" element={<TrafficRecords />} />
          <Route path="traffic/record/:id" element={<TrafficRecordDetail />} />
          <Route path="traffic/logs" element={<TrafficSubmissionLogs />} />
          <Route path="traffic/logs/:id" element={<TrafficSubmissionDetail />} />
          
          {/* Admin Module Routes */}
          <Route path="admin" element={<AdminDashboard />} />
          <Route path="admin/departments" element={<DepartmentsPage />} />
          <Route path="admin/roles" element={<RolesPage />} />
          <Route path="admin/functions" element={<FunctionsPage />} />
          <Route path="admin/automation" element={<AutomationRulesPage />} />
          <Route path="admin/ai-profiles" element={<AIProfilesPage />} />
          <Route path="admin/templates" element={<TemplatesPage />} />
          <Route path="admin/audit" element={<AuditLogsPage />} />
          
          {/* Artur Module Routes */}
          <Route path="admin/artur" element={<ArturDashboard />} />
          <Route path="admin/artur/suggestions" element={<SuggestionsFeed />} />
          <Route path="admin/artur/simulation" element={<SimulationView />} />
          <Route path="admin/artur/simulation/:id" element={<SimulationDetail />} />
          <Route path="admin/artur/interventions" element={<InterventionLog />} />
          <Route path="admin/artur/kpi" element={<KpiGraphs />} />
          
          {/* Catch-all redirect to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
      </I18nextProvider>
    </QueryClientProvider>
  );
}

export default App
