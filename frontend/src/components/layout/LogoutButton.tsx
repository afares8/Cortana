import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

interface LogoutButtonProps {
  className?: string;
}

const LogoutButton: React.FC<LogoutButtonProps> = ({ className = '' }) => {
  const { logout } = useAuth();
  const { t } = useTranslation();

  return (
    <button
      onClick={logout}
      className={`px-4 py-2 text-white bg-red-600 hover:bg-red-700 rounded-md ${className}`}
    >
      {t('common.logout')}
    </button>
  );
};

export default LogoutButton;
