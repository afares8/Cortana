import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

const LanguageToggle: React.FC = () => {
  const { i18n, t } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'es' ? 'en' : 'es';
    i18n.changeLanguage(newLang);
    localStorage.setItem('i18nextLng', newLang);
  };

  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
      aria-label={t('common.labels.language')}
    >
      <Globe className="h-4 w-4" />
      <span>{i18n.language === 'es' ? t('common.labels.english') : t('common.labels.spanish')}</span>
    </button>
  );
};

export default LanguageToggle;
