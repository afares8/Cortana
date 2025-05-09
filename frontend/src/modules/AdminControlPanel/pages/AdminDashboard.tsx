import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { 
  Building2, 
  Users, 
  Code2, 
  GitBranch, 
  Cpu, 
  FileCode, 
  BarChart3 
} from 'lucide-react';

const AdminDashboard: React.FC = () => {
  const { t } = useTranslation();

  const modules = [
    {
      title: 'Departments',
      description: 'Create and manage business departments',
      icon: <Building2 size={24} />,
      link: '/admin/departments'
    },
    {
      title: 'Roles & Permissions',
      description: 'Manage roles and assign permissions',
      icon: <Users size={24} />,
      link: '/admin/roles'
    },
    {
      title: 'Functions',
      description: 'Define department-specific functions',
      icon: <Code2 size={24} />,
      link: '/admin/functions'
    },
    {
      title: 'Automation Rules',
      description: 'Create workflow automation rules',
      icon: <GitBranch size={24} />,
      link: '/admin/automation'
    },
    {
      title: 'AI Profiles',
      description: 'Configure AI models for departments',
      icon: <Cpu size={24} />,
      link: '/admin/ai-profiles'
    },
    {
      title: 'Department Templates',
      description: 'Create and apply department templates',
      icon: <FileCode size={24} />,
      link: '/admin/templates'
    },
    {
      title: 'Audit Logs',
      description: 'View system activity and audit logs',
      icon: <BarChart3 size={24} />,
      link: '/admin/audit'
    }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Business Administration</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modules.map((module, index) => (
          <Link 
            key={index} 
            to={module.link}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200"
          >
            <div className="flex items-center mb-4">
              <div className="p-2 bg-blue-100 rounded-lg text-blue-600 mr-4">
                {module.icon}
              </div>
              <h2 className="text-xl font-semibold">{module.title}</h2>
            </div>
            <p className="text-gray-600">{module.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default AdminDashboard;
