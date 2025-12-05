import { StatusBar } from 'expo-status-bar';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { useEffect } from 'react';
import { store } from './src/store/store';
import './src/i18n';
import AppNavigator from './src/navigation/AppNavigator';
import { ErrorBoundary } from './src/components/common';
import { measureAppStartup } from './src/utils/performance';

export default function App() {
  useEffect(() => {
    // Measure app startup time
    measureAppStartup();
  }, []);

  return (
    <Provider store={store}>
      <SafeAreaProvider>
        <ErrorBoundary>
          <AppNavigator />
          <StatusBar style="auto" />
        </ErrorBoundary>
      </SafeAreaProvider>
    </Provider>
  );
}
