import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { getLocales } from 'expo-localization';

import fr from './fr.json';
import mg from './mg.json';

const resources = {
  fr: { translation: fr },
  mg: { translation: mg },
};

i18n.use(initReactI18next).init({
  resources,
  lng: getLocales()[0]?.languageCode || 'fr',
  fallbackLng: 'fr',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
