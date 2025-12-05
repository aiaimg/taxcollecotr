import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useLanguage } from '../context/LanguageContext';
import { Language } from '../utils/translations';

interface LanguageSelectorProps {
  style?: object;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({ style }) => {
  const { language, setLanguage } = useLanguage();

  const languages = [
    { code: 'fr' as Language, label: 'Français', nativeLabel: 'Français' },
    { code: 'mg' as Language, label: 'Malagasy', nativeLabel: 'Malagasy' },
  ];

  const handleLanguageChange = async (langCode: Language) => {
    await setLanguage(langCode);
  };

  return (
    <View style={[styles.container, style]}>
      <Text style={styles.title}>Langue / Fiteny</Text>
      {languages.map((lang) => (
        <TouchableOpacity
          key={lang.code}
          style={[
            styles.languageOption,
            language === lang.code && styles.selectedOption,
          ]}
          onPress={() => handleLanguageChange(lang.code)}
        >
          <Text style={[
            styles.languageText,
            language === lang.code && styles.selectedText,
          ]}>
            {lang.nativeLabel}
          </Text>
          <Text style={[
            styles.languageSubtext,
            language === lang.code && styles.selectedSubtext,
          ]}>
            {lang.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    marginVertical: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  languageOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginVertical: 4,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  selectedOption: {
    backgroundColor: '#007bff',
    borderColor: '#007bff',
  },
  languageText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  selectedText: {
    color: '#fff',
  },
  languageSubtext: {
    fontSize: 14,
    color: '#6c757d',
  },
  selectedSubtext: {
    color: '#e3f2fd',
  },
});