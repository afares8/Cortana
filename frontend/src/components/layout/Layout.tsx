import { ReactNode, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
  title: string;
}

export default function Layout({ children, title }: LayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const navItems = [
    { path: '', label: 'Dashboard', icon: '📊' },
    { path: 'contracts', label: 'Contracts', icon: '📄' },
    { path: 'contracts/upload', label: 'Upload Contract', icon: '📤' },
    { path: 'ai-dashboard', label: 'AI Command Center', icon: '🧠' },
    { path: 'legal/clients', label: 'Legal Clients', icon: '👥' },
    { path: 'legal/contracts', label: 'Legal Contracts', icon: '📑' },
    { path: 'legal/workflows', label: 'Workflows', icon: '🔄' },
    { path: 'legal/tasks', label: 'Tasks', icon: '✅' },
    { path: 'legal/audit-logs', label: 'Audit Logs', icon: '📝' },
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-gray-900">LegalContractTracker</h1>
          </div>
          
          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none"
            >
              <span className="sr-only">Open menu</span>
              <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
          
          {/* Desktop menu */}
          <nav className="hidden md:flex space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path === '' ? '/' : `/${item.path}`}
                onClick={(e) => {
                  e.preventDefault();
                  console.log(`Navigating to: ${item.path === '' ? '/' : `/${item.path}`}, current hash: ${location.hash}`);
                  navigate(item.path === '' ? '/' : `/${item.path}`);
                }}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  (location.hash === `#/${item.path}` || (item.path === '' && location.hash === '#/'))
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Link>
            ))}
            <button 
              onClick={handleLogout}
              className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            >
              <span className="mr-2">🚪</span>
              Logout
            </button>
          </nav>
        </div>
        
        {/* Mobile menu, show/hide based on menu state */}
        {mobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path === '' ? '/' : `/${item.path}`}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    (location.hash === `#/${item.path}` || (item.path === '' && location.hash === '#/'))
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    console.log(`Mobile: Navigating to: ${item.path === '' ? '/' : `/${item.path}`}, current hash: ${location.hash}`);
                    setMobileMenuOpen(false);
                    navigate(item.path === '' ? '/' : `/${item.path}`);
                  }}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
              <button 
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="flex w-full items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              >
                <span className="mr-2">🚪</span>
                Logout
              </button>
            </div>
          </div>
        )}
      </header>
      
      {/* Main content */}
      <main className="flex-grow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          </div>
          {children}
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-white shadow-sm mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} LegalContractTracker. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
