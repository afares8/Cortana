import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslation from './locales/en.json';
import esTranslation from './locales/es.json';

const isDevelopment = import.meta.env.MODE === 'development' || false;

localStorage.setItem('i18nextLng', 'es');

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslation
      },
      es: {
        translation: esTranslation
      }
    },
    fallbackLng: 'es', // Set Spanish as fallback
    lng: 'es', // Force Spanish language
    debug: isDevelopment,
    interpolation: {
      escapeValue: false // React already escapes values
    }
  });

export default i18n;
