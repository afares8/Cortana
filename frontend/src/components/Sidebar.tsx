import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Home, 
  FileText, 
  Users, 
  Settings, 
  LogOut,
  DollarSign,
  UserCog
} from 'lucide-react';

const Sidebar = () => {
  const isAdmin = true;

  return (
    <div className="w-64 bg-gray-800 text-white h-full flex flex-col">
      <div className="p-5 border-b border-gray-700">
        <h1 className="text-2xl font-bold">Cortana</h1>
        <p className="text-gray-400 text-sm">Enterprise Management</p>
      </div>
      
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <li>
            <Link to="/" className="flex items-center p-2 rounded hover:bg-gray-700">
              <Home className="h-5 w-5 mr-3" />
              Dashboard
            </Link>
          </li>
          
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">Legal</div>
            <ul className="space-y-1">
              <li>
                <Link to="/legal/clients" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Users className="h-5 w-5 mr-3" />
                  Clients
                </Link>
              </li>
              <li>
                <Link to="/legal/contracts" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <FileText className="h-5 w-5 mr-3" />
                  Contracts
                </Link>
              </li>
            </ul>
          </li>
          
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">Accounting</div>
            <ul className="space-y-1">
              <li>
                <Link to="/accounting/dashboard" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <DollarSign className="h-5 w-5 mr-3" />
                  Dashboard
                </Link>
              </li>
              {isAdmin && (
                <li>
                  <Link to="/accounting/admin/users" className="flex items-center p-2 rounded hover:bg-gray-700">
                    <UserCog className="h-5 w-5 mr-3" />
                    User Access
                  </Link>
                </li>
              )}
            </ul>
          </li>
          
          <li className="pt-4">
            <div className="text-gray-400 text-xs uppercase font-semibold mb-2 pl-2">Account</div>
            <ul className="space-y-1">
              <li>
                <Link to="/settings" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <Settings className="h-5 w-5 mr-3" />
                  Settings
                </Link>
              </li>
              <li>
                <Link to="/login" className="flex items-center p-2 rounded hover:bg-gray-700">
                  <LogOut className="h-5 w-5 mr-3" />
                  Logout
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
