import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import ProtectedRoute from './components/auth/ProtectedRoute';

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
import NewClient from './modules/legal/pages/clients/NewClient';
import ClientDetail from './modules/legal/pages/ClientDetail';
import LegalContractList from './modules/legal/pages/ContractList';
import LegalContractDetail from './modules/legal/pages/ContractDetail';
import WorkflowList from './modules/legal/pages/WorkflowList';
import WorkflowDetail from './modules/legal/pages/WorkflowDetail';
import TaskList from './modules/legal/pages/TaskList';
import TaskDetail from './modules/legal/pages/TaskDetail';
import AuditLogList from './modules/legal/pages/AuditLogList';
import LegalDashboard from './modules/legal/pages/LegalDashboard';

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

function App() {
  useEffect(() => {
    console.log('App initialized');
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>
        <Router>
          <AuthProvider>
            <Routes>
              {/* Auth routes */}
              <Route path="/login" element={<Login onLoginSuccess={() => {}} />} />
              <Route path="/register" element={<Navigate to="/login" replace />} />
              
              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="contracts" element={
                <ProtectedRoute>
                  <ContractList />
                </ProtectedRoute>
              } />
              <Route path="contracts/upload" element={
                <ProtectedRoute>
                  <ContractUpload />
                </ProtectedRoute>
              } />
              <Route path="contracts/:id" element={
                <ProtectedRoute>
                  <ContractDetail />
                </ProtectedRoute>
              } />
              
              {/* AI features */}
              <Route path="ai-dashboard" element={
                <ProtectedRoute>
                  <AIDashboard />
                </ProtectedRoute>
              } />
              <Route path="contracts/:id/analyze" element={
                <ProtectedRoute>
                  <ContractDetail />
                </ProtectedRoute>
              } />
              
              {/* Compliance Module Routes */}
              <Route path="compliance/dashboard" element={
                <ProtectedRoute>
                  <ComplianceDashboard />
                </ProtectedRoute>
              } />
              <Route path="compliance/uaf-report/new" element={
                <ProtectedRoute>
                  <UAFReportForm />
                </ProtectedRoute>
              } />
              <Route path="compliance/reports/:id" element={
                <ProtectedRoute>
                  <ComplianceDashboard />
                </ProtectedRoute>
              } />
              <Route path="compliance/pep-screening/new" element={
                <ProtectedRoute>
                  <PEPScreeningForm />
                </ProtectedRoute>
              } />
              <Route path="compliance/pep-screenings/:id" element={
                <ProtectedRoute>
                  <ComplianceDashboard />
                </ProtectedRoute>
              } />
              <Route path="compliance/sanctions-screening/new" element={
                <ProtectedRoute>
                  <SanctionsScreeningForm />
                </ProtectedRoute>
              } />
              <Route path="compliance/sanctions-screenings/:id" element={
                <ProtectedRoute>
                  <ComplianceDashboard />
                </ProtectedRoute>
              } />
              <Route path="compliance/verify-customer" element={
                <ProtectedRoute>
                  <ComplianceCheckPage />
                </ProtectedRoute>
              } />
              <Route path="compliance/country-risk-map" element={
                <ProtectedRoute>
                  <CountryRiskMap />
                </ProtectedRoute>
              } />
              
              {/* Legal Module Routes */}
              <Route path="legal/dashboard" element={
                <ProtectedRoute>
                  <LegalDashboard />
                </ProtectedRoute>
              } />
              <Route path="legal/clients" element={
                <ProtectedRoute>
                  <ClientList />
                </ProtectedRoute>
              } />
              <Route path="legal/clients/new" element={
                <ProtectedRoute>
                  <NewClient />
                </ProtectedRoute>
              } />
              <Route path="legal/clients/:id" element={
                <ProtectedRoute>
                  <ClientDetail />
                </ProtectedRoute>
              } />
              <Route path="legal/contracts" element={
                <ProtectedRoute>
                  <LegalContractList />
                </ProtectedRoute>
              } />
              <Route path="legal/contracts/:id" element={
                <ProtectedRoute>
                  <LegalContractDetail />
                </ProtectedRoute>
              } />
              <Route path="legal/workflows" element={
                <ProtectedRoute>
                  <WorkflowList />
                </ProtectedRoute>
              } />
              <Route path="legal/workflows/:id" element={
                <ProtectedRoute>
                  <WorkflowDetail />
                </ProtectedRoute>
              } />
              <Route path="legal/tasks" element={
                <ProtectedRoute>
                  <TaskList />
                </ProtectedRoute>
              } />
              <Route path="legal/tasks/:id" element={
                <ProtectedRoute>
                  <TaskDetail />
                </ProtectedRoute>
              } />
              <Route path="legal/audit-logs" element={
                <ProtectedRoute>
                  <AuditLogList />
                </ProtectedRoute>
              } />
              
              {/* User Management Module Routes */}
              <Route path="users" element={
                <ProtectedRoute>
                  <UserList />
                </ProtectedRoute>
              } key="user-list" />
              <Route path="users/new" element={
                <ProtectedRoute>
                  <UserForm />
                </ProtectedRoute>
              } key="user-new" />
              <Route path="users/:id" element={
                <ProtectedRoute>
                  <UserForm />
                </ProtectedRoute>
              } key="user-detail" />
              <Route path="users/:id/edit" element={
                <ProtectedRoute>
                  <UserForm />
                </ProtectedRoute>
              } key="user-edit" />
              <Route path="users/:id/reset-password" element={
                <ProtectedRoute>
                  <UserForm />
                </ProtectedRoute>
              } key="user-reset-password" />
              <Route path="users/:id/lock" element={
                <ProtectedRoute>
                  <UserForm />
                </ProtectedRoute>
              } key="user-lock" />
              <Route path="users/:id/unlock" element={
                <ProtectedRoute>
                  <UserForm />
                </ProtectedRoute>
              } key="user-unlock" />
              
              {/* Accounting Module Routes */}
              <Route path="accounting/dashboard" element={
                <ProtectedRoute>
                  <AccountingDashboard />
                </ProtectedRoute>
              } />
              <Route path="accounting/admin/users" element={
                <ProtectedRoute>
                  <UserAccessManagement />
                </ProtectedRoute>
              } />
              <Route path="accounting/notifications" element={
                <ProtectedRoute>
                  <NotificationsPage />
                </ProtectedRoute>
              } />
              <Route path="accounting/audit" element={
                <ProtectedRoute>
                  <AuditLogPage />
                </ProtectedRoute>
              } />
              <Route path="accounting/documents" element={
                <ProtectedRoute>
                  <DocumentGenerationPage />
                </ProtectedRoute>
              } />
              <Route path="accounting/email-drafts" element={
                <ProtectedRoute>
                  <EmailDraftPage />
                </ProtectedRoute>
              } />
              
              {/* Traffic Module Routes */}
              <Route path="traffic/dashboard" element={
                <ProtectedRoute>
                  <TrafficDashboard />
                </ProtectedRoute>
              } />
              <Route path="traffic/upload" element={
                <ProtectedRoute>
                  <TrafficUpload />
                </ProtectedRoute>
              } />
              <Route path="traffic/records" element={
                <ProtectedRoute>
                  <TrafficRecords />
                </ProtectedRoute>
              } />
              <Route path="traffic/record/:id" element={
                <ProtectedRoute>
                  <TrafficRecordDetail />
                </ProtectedRoute>
              } />
              <Route path="traffic/logs" element={
                <ProtectedRoute>
                  <TrafficSubmissionLogs />
                </ProtectedRoute>
              } />
              <Route path="traffic/logs/:id" element={
                <ProtectedRoute>
                  <TrafficSubmissionDetail />
                </ProtectedRoute>
              } />
              
              {/* Admin Module Routes */}
              <Route path="admin" element={
                <ProtectedRoute>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              <Route path="admin/departments" element={
                <ProtectedRoute>
                  <DepartmentsPage />
                </ProtectedRoute>
              } />
              <Route path="admin/roles" element={
                <ProtectedRoute>
                  <RolesPage />
                </ProtectedRoute>
              } />
              <Route path="admin/functions" element={
                <ProtectedRoute>
                  <FunctionsPage />
                </ProtectedRoute>
              } />
              <Route path="admin/automation" element={
                <ProtectedRoute>
                  <AutomationRulesPage />
                </ProtectedRoute>
              } />
              <Route path="admin/ai-profiles" element={
                <ProtectedRoute>
                  <AIProfilesPage />
                </ProtectedRoute>
              } />
              <Route path="admin/templates" element={
                <ProtectedRoute>
                  <TemplatesPage />
                </ProtectedRoute>
              } />
              <Route path="admin/audit" element={
                <ProtectedRoute>
                  <AuditLogsPage />
                </ProtectedRoute>
              } />
              
              {/* Artur Module Routes */}
              <Route path="admin/artur" element={
                <ProtectedRoute>
                  <ArturDashboard />
                </ProtectedRoute>
              } />
              <Route path="admin/artur/suggestions" element={
                <ProtectedRoute>
                  <SuggestionsFeed />
                </ProtectedRoute>
              } />
              <Route path="admin/artur/simulation" element={
                <ProtectedRoute>
                  <SimulationView />
                </ProtectedRoute>
              } />
              <Route path="admin/artur/simulation/:id" element={
                <ProtectedRoute>
                  <SimulationDetail />
                </ProtectedRoute>
              } />
              <Route path="admin/artur/interventions" element={
                <ProtectedRoute>
                  <InterventionLog />
                </ProtectedRoute>
              } />
              <Route path="admin/artur/kpi" element={
                <ProtectedRoute>
                  <KpiGraphs />
                </ProtectedRoute>
              } />
              
              {/* Catch-all redirect to dashboard */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AuthProvider>
        </Router>
      </I18nextProvider>
    </QueryClientProvider>
  );
}

export default App
