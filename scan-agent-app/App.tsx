import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from './src/context/AuthContext';
import { ScannerProvider } from './src/context/ScannerContext';
import { LanguageProvider } from './src/context/LanguageContext';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  return (
    <SafeAreaProvider>
      <LanguageProvider>
        <AuthProvider>
          <ScannerProvider>
            <StatusBar style="auto" />
            <AppNavigator />
          </ScannerProvider>
        </AuthProvider>
      </LanguageProvider>
    </SafeAreaProvider>
  );
}
