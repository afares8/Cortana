import { ReactNode, useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Search, X, Menu, LogOut, ChevronRight, ChevronDown, Bell, Settings, Shield, FileText, Users, Activity, CheckSquare, Database, Brain, BarChart2, BarChart3, Truck, DollarSign, Mail, UserCog, Building2, GitBranch, Cpu } from 'lucide-react';
import NotificationCenter from '../../modules/notifications/components/NotificationCenter';
import LanguageToggle from '../LanguageToggle';
import SettingsPanel from '../settings/SettingsPanel';
import { searchAll } from '../../modules/search/api/searchApi';
import type { SearchResult } from '../../modules/search/api/searchApi';

interface LayoutProps {
  children: ReactNode;
  title: string;
}

interface NavItem {
  path: string;
  label: string;
  icon: ReactNode;
  section?: string;
  children?: NavItem[];
  comingSoon?: boolean;
}

export default function Layout({ children, title }: LayoutProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [settingsPanelOpen, setSettingsPanelOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    dashboard: true,
    admin: true,
    contracts: true,
    legal: true,
    compliance: true,
    traffic: true,
    ai: true,
    accounting: true,
    users: true
  });

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const navItems: NavItem[] = [
    { 
      path: '', 
      label: 'common.navigation.dashboard', 
      icon: <BarChart2 className="h-5 w-5" aria-label="Panel de control" />, 
      section: 'dashboard'
    },
    {
      path: 'legal',
      label: 'common.navigation.legalAndContracts',
      icon: <Shield className="h-5 w-5" aria-label="Legal y contratos" />,
      section: 'legal',
      children: [
        { path: 'legal/dashboard', label: 'common.navigation.dashboard', icon: <BarChart2 className="h-4 w-4" /> },
        { path: 'compliance/dashboard', label: 'compliance.dashboard', icon: <BarChart2 className="h-4 w-4" /> },
        { path: 'legal/contracts', label: 'common.navigation.allContracts', icon: <FileText className="h-4 w-4" /> },
        { path: 'legal/contracts/upload', label: 'common.navigation.uploadContract', icon: <FileText className="h-4 w-4" /> },
        { path: 'legal/clients', label: 'common.navigation.clients', icon: <Users className="h-4 w-4" /> },
        { path: 'legal/workflows', label: 'common.navigation.workflows', icon: <Activity className="h-4 w-4" /> },
        { path: 'legal/tasks', label: 'common.navigation.tasks', icon: <CheckSquare className="h-4 w-4" /> },
        { path: 'legal/audit-logs', label: 'common.navigation.auditLogs', icon: <Database className="h-4 w-4" /> },
        //{ path: 'legal/compliance/pep', label: 'common.navigation.pepScreening', icon: <Users className="h-4 w-4" /> },
        //{ path: 'legal/compliance/sanctions', label: 'common.navigation.sanctionsScreening', icon: <Shield className="h-4 w-4" /> },
        //{ path: 'legal/compliance/uaf', label: 'common.navigation.uafReport', icon: <FileText className="h-4 w-4" /> },
        { path: 'ai-dashboard', label: 'common.navigation.legalAssistant', icon: <Brain className="h-4 w-4" /> }
      ]
    },
    { 
      path: 'users', 
      label: 'common.navigation.userManagement', 
      icon: <UserCog className="h-5 w-5" aria-label="Gestión de usuarios" />, 
      section: 'users',
      children: [
        { path: 'users', label: 'common.navigation.users', icon: <Users className="h-4 w-4" /> },
        { path: 'users/new', label: 'common.navigation.newUser', icon: <UserCog className="h-4 w-4" /> }
      ]
    },
    { 
      path: 'traffic', 
      label: 'common.navigation.traffic', 
      icon: <Truck className="h-5 w-5" />, 
      section: 'traffic',
      children: [
        { path: 'traffic/dashboard', label: 'common.navigation.panel', icon: <BarChart2 className="h-4 w-4" /> },
        { path: 'traffic/upload', label: 'common.navigation.uploadInvoice', icon: <FileText className="h-4 w-4" /> },
        { path: 'traffic/records', label: 'common.navigation.records', icon: <Database className="h-4 w-4" /> },
        { path: 'traffic/logs', label: 'common.navigation.history', icon: <Activity className="h-4 w-4" /> }
      ]
    },

    { 
      path: 'accounting', 
      label: 'common.navigation.accounting', 
      icon: <DollarSign className="h-5 w-5" />, 
      section: 'accounting',
      children: [
        { path: 'accounting/dashboard', label: 'common.navigation.dashboard', icon: <BarChart2 className="h-4 w-4" /> },
        { path: 'accounting/documents', label: 'common.navigation.documents', icon: <FileText className="h-4 w-4" /> },
        { path: 'accounting/notifications', label: 'common.navigation.notifications', icon: <Bell className="h-4 w-4" /> },
        { path: 'accounting/audit', label: 'common.navigation.auditLogs', icon: <Database className="h-4 w-4" /> },
        { path: 'accounting/email-drafts', label: 'common.navigation.emailDrafts', icon: <Mail className="h-4 w-4" /> },
        { path: 'accounting/admin/users', label: 'common.navigation.userAccess', icon: <UserCog className="h-4 w-4" /> }
      ]
    },
    { 
      path: 'admin', 
      label: 'common.navigation.administration', 
      icon: <Settings className="h-5 w-5" />, 
      section: 'admin',
      children: [
        { path: 'admin', label: 'common.navigation.dashboard', icon: <BarChart2 className="h-4 w-4" /> },
        { path: 'admin/departments', label: 'common.navigation.departments', icon: <Building2 className="h-4 w-4" /> },
        { path: 'admin/roles', label: 'common.navigation.roles', icon: <UserCog className="h-4 w-4" /> },
        { path: 'admin/automation', label: 'common.navigation.automation', icon: <GitBranch className="h-4 w-4" />, comingSoon: true },
        { path: 'admin/ai-profiles', label: 'common.navigation.aiProfiles', icon: <Cpu className="h-4 w-4" />, comingSoon: true },
        { path: 'admin/audit', label: 'common.navigation.auditLogs', icon: <BarChart3 className="h-4 w-4" /> },
        { path: 'admin/artur', label: 'common.navigation.arturDashboard', icon: <Brain className="h-4 w-4" /> },
        { path: 'admin/artur/suggestions', label: 'common.navigation.arturSuggestions', icon: <Brain className="h-4 w-4" /> },
        { path: 'admin/artur/simulation', label: 'common.navigation.arturSimulation', icon: <Brain className="h-4 w-4" />, comingSoon: true },
        { path: 'admin/artur/interventions', label: 'common.navigation.arturInterventions', icon: <Brain className="h-4 w-4" />, comingSoon: true },
        { path: 'admin/artur/kpi', label: 'common.navigation.arturKPI', icon: <Brain className="h-4 w-4" />, comingSoon: true }
      ]
    }
  ];

  const getCurrentSection = () => {
    const path = location.hash.replace('#/', '');
    if (path.startsWith('legal/')) return 'legal';
    if (path === 'ai-dashboard') return 'legal';
    if (path.startsWith('traffic/')) return 'traffic';
    if (path.startsWith('accounting/')) return 'accounting';
    if (path.startsWith('users/')) return 'users';
    if (path.startsWith('admin/')) return 'admin';
    return 'dashboard';
  };

  const currentSection = getCurrentSection();

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const results = await searchAll(query);
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      handleSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);


  const renderContextualPanel = () => {
    switch (currentSection) {
      case 'legal':
        return (
          <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
            <h3 className="font-medium text-gray-900 mb-3">{t('legal.department')}</h3>
            <div className="space-y-2">
              <button 
                onClick={() => navigate('legal/dashboard')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">📊</span>
                {t('common.navigation.dashboard')}
              </button>
              <button 
                onClick={() => navigate('ai-dashboard')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">🧠</span>
                {t('common.navigation.legalAssistant')}
              </button>
              <button 
                onClick={() => navigate('legal/contracts/upload')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">📤</span>
                {t('common.navigation.uploadContract')}
              </button>
              <button 
                onClick={() => navigate('legal/clients/new')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">➕</span>
                {t('legal.addNewClient')}
              </button>
              <button 
                onClick={() => navigate('legal/workflows/new')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">🔄</span>
                {t('legal.createWorkflow')}
              </button>
              <button 
                onClick={() => navigate('legal/tasks/new')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">✅</span>
                {t('legal.createTask')}
              </button>
            </div>
            
            <h3 className="font-medium text-gray-900 mt-6 mb-3">{t('common.recentActivity')}</h3>
            <div className="space-y-2">
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-sm font-medium text-gray-800">Contract Review</p>
                <p className="text-xs text-gray-600">Updated 2 hours ago</p>
              </div>
              <div className="p-3 bg-yellow-50 rounded-md">
                <p className="text-sm font-medium text-yellow-800">TechStart Inc. NDA</p>
                <p className="text-xs text-yellow-700">Expires in 30 days</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-md">
                <p className="text-sm font-medium text-blue-800">UAF Report - Q2 2025</p>
                <p className="text-xs text-blue-700">Due in 15 days</p>
              </div>
            </div>
          </div>
        );
      

      
      case 'traffic':
        return (
          <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
            <h3 className="font-medium text-gray-900 mb-3">{t('traffic.actions')}</h3>
            <div className="space-y-2">
              <button 
                onClick={() => navigate('/traffic/dashboard')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">📊</span>
                {t('common.navigation.dashboard')}
              </button>
              <button 
                onClick={() => navigate('/traffic/upload')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">📤</span>
                {t('traffic.uploadInvoice')}
              </button>
              <button 
                onClick={() => navigate('/traffic/records')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">📋</span>
                {t('traffic.viewRecords')}
              </button>
            </div>
            
            <h3 className="font-medium text-gray-900 mt-6 mb-3">{t('common.recentActivity')}</h3>
            <div className="space-y-2">
              <div className="p-3 bg-orange-50 rounded-md">
                <p className="text-sm font-medium text-orange-800">{t('traffic.dmceDeclaration')}</p>
                <p className="text-xs text-orange-700">{t('traffic.sentDaysAgo', { days: 2 })}</p>
              </div>
              <div className="p-3 bg-orange-50 rounded-md">
                <p className="text-sm font-medium text-orange-800">{t('traffic.invoiceConsolidation')}</p>
                <p className="text-xs text-orange-700">{t('traffic.completedWeeksAgo', { weeks: 1 })}</p>
              </div>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
            <h3 className="font-medium text-gray-900 mb-3">{t('dashboard.quickActions')}</h3>
            <div className="space-y-2">
              <button 
                onClick={() => navigate('/contracts/upload')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">📤</span>
                {t('dashboard.uploadNewContract')}
              </button>
              <button 
                onClick={() => navigate('/legal/clients')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">👥</span>
                {t('dashboard.viewClients')}
              </button>
              <button 
                onClick={() => navigate('/compliance/dashboard')}
                className="w-full text-left px-3 py-2 text-sm rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-2">📊</span>
                {t('dashboard.complianceDashboard')}
              </button>
            </div>
            
            <h3 className="font-medium text-gray-900 mt-6 mb-3">{t('dashboard.systemStatus')}</h3>
            <div className="p-3 bg-green-50 rounded-md">
              <p className="text-sm font-medium text-green-800">{t('dashboard.allSystemsOperational')}</p>
              <p className="text-xs text-green-700">{t('dashboard.lastUpdated')}: {new Date().toLocaleTimeString()}</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <h1 
              onClick={() => navigate('/')} 
              className="text-xl font-bold text-gray-900 cursor-pointer"
            >
              Cortana
            </h1>
          </div>
          
          {/* Global Search */}
          <div className="flex-1 max-w-lg mx-4 relative">
            <div className="relative">
              <input
                type="text"
                placeholder={t('common.searchPlaceholder')}
                className="w-full py-2 pl-10 pr-4 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setSearchOpen(true)}
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" aria-label="Buscar" />
              </div>
              {searchQuery && (
                <button
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => {
                    setSearchQuery('');
                    setSearchResults([]);
                  }}
                >
                  <X className="h-5 w-5 text-gray-400" aria-label="Limpiar búsqueda" />
                </button>
              )}
            </div>
            
            {/* Search Results Dropdown */}
            {searchOpen && searchQuery && (
              <div className="absolute mt-1 w-full bg-white rounded-md shadow-lg z-10">
                <div className="py-1">
                  {isSearching ? (
                    <div className="px-4 py-2 text-sm text-gray-500">{t('common.searching')}</div>
                  ) : searchResults.length > 0 ? (
                    <>
                      {searchResults.map((result) => (
                        <div
                          key={result.id}
                          className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                          onClick={() => {
                            navigate(result.path);
                            setSearchOpen(false);
                            setSearchQuery('');
                          }}
                        >
                          <div className="flex items-start">
                            <div className="flex-shrink-0 mt-1">
                              {result.type === 'contract' && <FileText className="h-4 w-4 text-blue-500" aria-label="Contrato" />}
                              {result.type === 'client' && <Users className="h-4 w-4 text-green-500" aria-label="Cliente" />}
                              {result.type === 'compliance' && <Shield className="h-4 w-4 text-red-500" aria-label="Cumplimiento" />}
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">{result.title}</p>
                              <p className="text-xs text-gray-500">{result.excerpt}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                      <div className="px-4 py-2 text-xs text-gray-500 border-t">
                        {t('common.pressEnterForAllResults')}
                      </div>
                    </>
                  ) : (
                    <div className="px-4 py-2 text-sm text-gray-500">{t('common.noResultsFound')}</div>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Desktop Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <NotificationCenter />
            <LanguageToggle />
            <button 
              onClick={() => setSettingsPanelOpen(true)}
              className="text-gray-500 hover:text-gray-700"
            >
              <Settings className="h-5 w-5" aria-label="Configuración" />
            </button>
            <button 
              onClick={handleLogout}
              className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            >
              <LogOut className="h-5 w-5 mr-2" aria-label="Cerrar sesión" />
              {t('common.logout')}
            </button>
          </div>
          
          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <NotificationCenter />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none"
            >
              <span className="sr-only">{t('common.openMenu')}</span>
              <Menu className="h-6 w-6" aria-label="Menú móvil" />
            </button>
          </div>
        </div>
        
        {/* Mobile menu, show/hide based on menu state */}
        {mobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {navItems.map((item) => (
                <div key={item.path}>
                  {item.children ? (
                    <div>
                      <button
                        onClick={() => toggleSection(item.section || '')}
                        className="flex w-full items-center justify-between px-3 py-2 text-sm font-medium rounded-md text-left text-gray-700"
                      >
                        <div className="flex items-center">
                          {item.icon}
                          <span className="ml-2">{t(item.label)}</span>
                        </div>
                        {expandedSections[item.section || ''] ? (
                          <ChevronDown className="h-4 w-4" aria-label="Contraer sección" />
                        ) : (
                          <ChevronRight className="h-4 w-4" aria-label="Expandir sección" />
                        )}
                      </button>
                      
                      {expandedSections[item.section || ''] && item.children.map((child) => (
                        <button
                          key={child.path}
                          onClick={() => {
                            navigate(`/${child.path}`);
                            setMobileMenuOpen(false);
                          }}
                          className="flex w-full items-center px-3 py-2 pl-8 text-sm font-medium rounded-md text-left text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                          aria-disabled={child.comingSoon}
                        >
                          {child.icon}
                          <span className="ml-2">{t(child.label)}</span>
                          {child.comingSoon && (
                            <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-500 rounded-full" aria-label={t('common.navigation.comingSoon')}>
                              {t('common.navigation.comingSoon')}
                            </span>
                          )}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <button
                      onClick={() => {
                        navigate(item.path === '' ? '/' : `/${item.path}`);
                        setMobileMenuOpen(false);
                      }}
                      className={`flex w-full items-center px-3 py-2 text-sm font-medium rounded-md text-left ${
                        (location.hash === `#/${item.path}` || 
                         (item.path === '' && location.hash === '#/') ||
                         (item.path !== '' && location.hash.startsWith(`#/${item.path}`)))
                          ? 'bg-gray-100 text-gray-900'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      {item.icon}
                      <span className="ml-2">{t(item.label)}</span>
                    </button>
                  )}
                </div>
              ))}
              <button 
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="flex w-full items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              >
                <LogOut className="h-5 w-5" />
                <span className="ml-2">{t('common.logout')}</span>
              </button>
              <div className="px-3 py-2">
                <LanguageToggle />
              </div>
            </div>
          </div>
        )}
      </header>
      
      {/* Main content with sidebar */}
      <div className="flex-grow flex">
        {/* Sidebar - Desktop only */}
        <div className="hidden md:block w-64 bg-white shadow-sm p-4 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto">
          <nav className="space-y-1">
            {navItems.map((item) => (
              <div key={item.path}>
                {item.children ? (
                  <div className="mb-2">
                    <button
                      onClick={() => toggleSection(item.section || '')}
                      className="flex w-full items-center justify-between px-3 py-2 text-sm font-medium rounded-md text-left text-gray-700 hover:bg-gray-50"
                    >
                      <div className="flex items-center">
                        {item.icon}
                        <span className="ml-2">{t(item.label)}</span>
                      </div>
                      {expandedSections[item.section || ''] ? (
                        <ChevronDown className="h-4 w-4" aria-label="Contraer sección" />
                      ) : (
                        <ChevronRight className="h-4 w-4" aria-label="Expandir sección" />
                      )}
                    </button>
                    
                    {expandedSections[item.section || ''] && (
                      <div className="ml-4 mt-1 space-y-1">
                        {item.children.map((child) => (
                          <button
                            key={child.path}
                            onClick={() => navigate(`/${child.path}`)}
                            className={`flex w-full items-center px-3 py-2 text-sm font-medium rounded-md text-left ${
                              location.hash === `#/${child.path}` 
                                ? 'bg-gray-100 text-gray-900'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`}
                            aria-disabled={child.comingSoon}
                          >
                            {child.icon}
                            <span className="ml-2">{t(child.label)}</span>
                            {child.comingSoon && (
                              <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-500 rounded-full" aria-label={t('common.navigation.comingSoon')}>
                                {t('common.navigation.comingSoon')}
                              </span>
                            )}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <button
                    onClick={() => navigate(item.path === '' ? '/' : `/${item.path}`)}
                    className={`flex w-full items-center px-3 py-2 text-sm font-medium rounded-md text-left ${
                      (location.hash === `#/${item.path}` || 
                       (item.path === '' && location.hash === '#/') ||
                       (item.path !== '' && location.hash.startsWith(`#/${item.path}`)))
                        ? 'bg-gray-100 text-gray-900'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    {item.icon}
                    <span className="ml-2">{t(item.label)}</span>
                  </button>
                )}
              </div>
            ))}
          </nav>
        </div>
        
        {/* Main content area */}
        <main className="flex-grow p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row">
              {/* Main content */}
              <div className="md:flex-1">
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
                </div>
                {children}
              </div>
              
              {/* Contextual side panel - Desktop only */}
              <div className="hidden md:block md:w-80 md:ml-6">
                {renderContextualPanel()}
              </div>
            </div>
          </div>
        </main>
      </div>
      
      {/* Footer */}
      <footer className="bg-white shadow-sm mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} Cortana. {t('common.allRightsReserved')}
          </p>
        </div>
      </footer>
      
      <SettingsPanel isOpen={settingsPanelOpen} onClose={() => setSettingsPanelOpen(false)} />
    </div>
  );
}
