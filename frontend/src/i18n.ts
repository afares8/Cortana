import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const enTranslation = require('./locales/en.json');
const esTranslation = require('./locales/es.json');

const isDevelopment = process.env.NODE_ENV === 'development' || false;

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
    fallbackLng: 'en',
    debug: isDevelopment,
    interpolation: {
      escapeValue: false // React already escapes values
    }
  });

export default i18n;
