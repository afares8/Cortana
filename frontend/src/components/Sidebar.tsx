import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  Home, 
  FileText, 
  Users, 
  Settings, 
  LogOut,
  DollarSign,
  UserCog,
  Shield,
  UserCheck,
  Activity,
  Building2,
  Cpu,
  GitBranch,
  BarChart3,
  Brain
} from 'lucide-react';

const Sidebar = () => {
  const { t } = useTranslation();
  const isAdmin = true;

  return (
    <div className="w-64 bg-gray-800 text-white h-full flex flex-col">
      <div className="p-5 border-b border-gray-700">
        <h1 className="text-2xl font-bold">Cortana</h1>
        <p className="text-gray-400 text-sm">{t('common.enterpriseManagement')}</p>
      </div>
      
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {/* Dashboard */}
          <li>
            <Link to="/" className="flex items-center p-2 rounded hover:bg-gray-700">
              <Home className="h-5 w-5 mr-3" />
              {t('common.navigation.dashboard')}
            </Link>
          </li>
          
          {/* Legal */}
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">
              {t('common.navigation.legal')}
            </div>
            <ul className="space-y-1">
              <li>
                <Link to="/legal/clients" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Users className="h-5 w-5 mr-3" />
                  {t('common.navigation.clients')}
                </Link>
              </li>
              <li>
                <Link to="/legal/contracts" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <FileText className="h-5 w-5 mr-3" />
                  {t('common.navigation.contracts')}
                </Link>
              </li>
            </ul>
          </li>
          
          {/* Compliance */}
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">
              {t('common.navigation.compliance')}
            </div>
            <ul className="space-y-1">
              <li>
                <Link to="/compliance/dashboard" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Shield className="h-5 w-5 mr-3" />
                  {t('common.navigation.dashboard')}
                </Link>
              </li>
              <li>
                <Link to="/compliance/verify-customer" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <UserCheck className="h-5 w-5 mr-3" />
                  {t('common.navigation.customerVerification')}
                </Link>
              </li>
              <li>
                <Link to="/diagnostics" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Activity className="h-5 w-5 mr-3" />
                  {t('common.navigation.diagnostics', 'Diagnostics')}
                </Link>
              </li>
            </ul>
          </li>
          
          {/* Accounting */}
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">
              {t('common.navigation.accounting')}
            </div>
            <ul className="space-y-1">
              <li>
                <Link to="/accounting/dashboard" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <DollarSign className="h-5 w-5 mr-3" />
                  {t('common.navigation.dashboard')}
                </Link>
              </li>
              {isAdmin && (
                <li>
                  <Link to="/accounting/admin/users" className="flex items-center p-2 rounded hover:bg-gray-700">
                    <UserCog className="h-5 w-5 mr-3" />
                    {t('common.navigation.userAccess')}
                  </Link>
                </li>
              )}
            </ul>
          </li>
          
          {/* User Management */}
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">
              {t('common.navigation.userManagement')}
            </div>
            <ul className="space-y-1">
              <li>
                <Link 
                  to="/users" 
                  className="flex items-center p-2 rounded hover:bg-gray-700"
                  onClick={(e) => {
                    e.stopPropagation(); // Prevent event bubbling but allow default navigation
                  }}
                >
                  <Users className="h-5 w-5 mr-3" />
                  {t('common.navigation.users')}
                </Link>
              </li>
              <li>
                <Link 
                  to="/users/new" 
                  className="flex items-center p-2 rounded hover:bg-gray-700"
                  onClick={(e) => {
                    e.stopPropagation(); // Prevent event bubbling but allow default navigation
                  }}
                >
                  <UserCog className="h-5 w-5 mr-3" />
                  {t('common.navigation.newUser')}
                </Link>
              </li>
            </ul>
          </li>
          
          {/* Administration */}
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">
              {t('common.navigation.administration')}
            </div>
            <ul className="space-y-1">
              <li>
                <Link to="/admin" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Home className="h-5 w-5 mr-3" />
                  {t('common.navigation.dashboard')}
                </Link>
              </li>
              <li>
                <Link to="/admin/departments" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Building2 className="h-5 w-5 mr-3" />
                  {t('common.navigation.departments')}
                </Link>
              </li>
              <li>
                <Link to="/admin/roles" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <UserCog className="h-5 w-5 mr-3" />
                  {t('common.navigation.roles')}
                </Link>
              </li>
              <li>
                <Link to="/admin/automation" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <GitBranch className="h-5 w-5 mr-3" />
                  {t('common.navigation.automation')}
                </Link>
              </li>
              <li>
                <Link to="/admin/ai-profiles" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Cpu className="h-5 w-5 mr-3" />
                  {t('common.navigation.aiProfiles')}
                </Link>
              </li>
              <li>
                <Link to="/admin/audit" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <BarChart3 className="h-5 w-5 mr-3" />
                  {t('common.navigation.auditLogs')}
                </Link>
              </li>
              
              {/* Artur Autonomous Governance */}
              <li>
                <Link to="/admin/artur" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Brain className="h-5 w-5 mr-3" />
                  Artur Executive Dashboard
                </Link>
              </li>
              <li>
                <Link to="/admin/artur/suggestions" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Brain className="h-5 w-5 mr-3" />
                  Suggestion Feed
                </Link>
              </li>
              <li>
                <Link to="/admin/artur/simulation" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Brain className="h-5 w-5 mr-3" />
                  Intervention Simulator
                </Link>
              </li>
              <li>
                <Link to="/admin/artur/interventions" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Brain className="h-5 w-5 mr-3" />
                  Timeline View
                </Link>
              </li>
              <li>
                <Link to="/admin/artur/kpi" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Brain className="h-5 w-5 mr-3" />
                  Intelligent Insights
                </Link>
              </li>
            </ul>
          </li>
          
          {/* Account */}
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">
              {t('common.navigation.account')}
            </div>
            <ul className="space-y-1">
              <li>
                <Link to="/settings" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Settings className="h-5 w-5 mr-3" />
                  {t('common.navigation.settings')}
                </Link>
              </li>
              <li>
                <Link to="/login" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <LogOut className="h-5 w-5 mr-3" />
                  {t('common.logout')}
                </Link>
              </li>
            </ul>
          </li>
        </ul>
      </nav>
      
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center">
          <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center mr-2">
            <span className="text-sm font-semibold">WM</span>
          </div>
          <div>
            <p className="text-sm font-semibold">Walid Magnate</p>
            <p className="text-xs text-gray-400">Admin</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
