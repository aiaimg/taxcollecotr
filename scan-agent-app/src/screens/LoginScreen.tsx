import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { t } from '../utils/translations';
import { validateBadgeId, validatePin } from '../utils/validators';
import { formatBadgeId } from '../utils/formatters';

export default function LoginScreen() {
  const { login, isLoading } = useAuth();
  const [badgeId, setBadgeId] = useState('');
  const [pin, setPin] = useState('');
  const [errors, setErrors] = useState<{ badgeId?: string; pin?: string }>({});

  useEffect(() => {
    // Format badge ID as user types
    if (badgeId) {
      setBadgeId(formatBadgeId(badgeId));
    }
  }, [badgeId]);

  const validateForm = (): boolean => {
    const newErrors: { badgeId?: string; pin?: string } = {};

    if (!validateBadgeId(badgeId)) {
      newErrors.badgeId = t('login.invalidBadgeIdFormat');
    }

    if (!validatePin(pin)) {
      newErrors.pin = t('login.pinInvalid');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      const success = await login({
        badgeId: badgeId.replace(/-/g, ''),
        pin,
      });

      if (!success) {
        Alert.alert(t('login.loginFailedTitle'), t('login.loginFailedMessage'));
      }
    } catch (error) {
      console.error('Login error:', error);
      Alert.alert(t('login.loginErrorTitle'), t('login.loginErrorMessage'));
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContainer}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.logoContainer}>
          <Image
            source={require('../../assets/icon.png')}
            style={styles.logo}
            resizeMode="contain"
          />
          <Text style={styles.title}>{t('login.title')}</Text>
          <Text style={styles.subtitle}>{t('login.subtitle')}</Text>
        </View>

        <View style={styles.formContainer}>
          <View style={styles.inputContainer}>
            <Text style={styles.label}>{t('login.badgeId')}</Text>
            <TextInput
              style={[styles.input, errors.badgeId && styles.inputError]}
              placeholder={t('login.badgeIdPlaceholder')}
              value={badgeId}
              onChangeText={setBadgeId}
              keyboardType="numeric"
              maxLength={8}
              autoCapitalize="none"
              autoCorrect={false}
            />
            {errors.badgeId && (
              <Text style={styles.errorText}>{errors.badgeId}</Text>
            )}
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>{t('login.pin')}</Text>
            <TextInput
              style={[styles.input, errors.pin && styles.inputError]}
              placeholder={t('login.pinPlaceholder')}
              value={pin}
              onChangeText={setPin}
              secureTextEntry
              keyboardType="numeric"
              maxLength={6}
            />
            {errors.pin && (
              <Text style={styles.errorText}>{errors.pin}</Text>
            )}
          </View>

          <TouchableOpacity
            style={[styles.loginButton, isLoading && styles.buttonDisabled]}
            onPress={handleLogin}
            disabled={isLoading}
          >
            <Text style={styles.loginButtonText}>
              {isLoading ? t('login.loggingIn') : t('login.loginButton')}
            </Text>
          </TouchableOpacity>

          {/* Quick Access Button for Development */}
          <TouchableOpacity
            style={[styles.loginButton, { backgroundColor: '#34C759', marginTop: 16 }]}
            onPress={async () => {
              try {
                const success = await login({
                  badgeId: 'AGENT2806',
                  pin: '0000', // Dummy PIN
                  email: 'agent1@taxcollector.mg',
                  password: 'agent123',
                });

                if (!success) {
                  Alert.alert(t('login.loginFailedTitle'), t('login.loginFailedMessage'));
                }
              } catch (error) {
                console.error('Login error:', error);
                Alert.alert(t('login.loginErrorTitle'), t('login.loginErrorMessage'));
              }
            }}
            disabled={isLoading}
          >
            <Text style={styles.loginButtonText}>
              Quick Access (Dev)
            </Text>
          </TouchableOpacity>

          <Text style={styles.helpText}>
            {t('login.helpText')}
          </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  formContainer: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  inputError: {
    borderColor: '#ff3b30',
  },
  errorText: {
    color: '#ff3b30',
    fontSize: 12,
    marginTop: 4,
  },
  loginButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  loginButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  helpText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 14,
    marginTop: 20,
  },
});