import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import Ionicons from '@expo/vector-icons/Ionicons';

import { userProfileService } from '../../services/userProfileService';
import authService from '../../services/authService';
import biometricService from '../../services/biometricService';
import storageService from '../../services/storageService';
import { UserProfile } from '../../types/models';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';

type RootStackParamList = {
  Settings: undefined;
  Login: undefined;
};

type SettingsScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Settings'>;

const SettingsScreen: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigation = useNavigation<SettingsScreenNavigationProp>();
  
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const [language, setLanguage] = useState<'fr' | 'mg'>('fr');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [biometricAvailable, setBiometricAvailable] = useState(false);

  useEffect(() => {
    loadSettings();
    checkBiometricAvailability();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const userProfile = await userProfileService.getProfile();
      setProfile(userProfile);
      
      setLanguage(userProfile.preferred_language);
      setNotificationsEnabled(userProfile.notifications_enabled);
      setBiometricEnabled(userProfile.biometric_enabled);
    } catch (error) {
      console.error('Error loading settings:', error);
      Alert.alert(
        t('settings.error.title'),
        t('settings.error.loadFailed'),
        [{ text: t('common.ok'), style: 'default' }]
      );
    } finally {
      setLoading(false);
    }
  };

  const checkBiometricAvailability = async () => {
    try {
      const available = await biometricService.isAvailable();
      setBiometricAvailable(available);
    } catch (error) {
      console.error('Error checking biometric availability:', error);
      setBiometricAvailable(false);
    }
  };

  const handleLanguageChange = async (newLanguage: 'fr' | 'mg') => {
    try {
      setSaving(true);
      
      await userProfileService.updatePreferences({
        preferred_language: newLanguage,
      });
      
      setLanguage(newLanguage);
      await i18n.changeLanguage(newLanguage);
      
      Alert.alert(
        t('settings.success.title'),
        t('settings.success.languageUpdated')
      );
    } catch (error) {
      console.error('Error updating language:', error);
      Alert.alert(
        t('settings.error.title'),
        t('settings.error.languageUpdateFailed')
      );
      setLanguage(language);
    } finally {
      setSaving(false);
    }
  };

  const handleNotificationsToggle = async (enabled: boolean) => {
    try {
      setSaving(true);
      
      await userProfileService.updatePreferences({
        notifications_enabled: enabled,
      });
      
      setNotificationsEnabled(enabled);
      
      Alert.alert(
        t('settings.success.title'),
        enabled ? t('settings.success.notificationsEnabled') : t('settings.success.notificationsDisabled')
      );
    } catch (error) {
      console.error('Error updating notifications:', error);
      Alert.alert(
        t('settings.error.title'),
        t('settings.error.notificationsUpdateFailed')
      );
      setNotificationsEnabled(notificationsEnabled);
    } finally {
      setSaving(false);
    }
  };

  const handleBiometricToggle = async (enabled: boolean) => {
    try {
      if (enabled && !biometricAvailable) {
        Alert.alert(
          t('settings.error.title'),
          t('settings.error.biometricNotAvailable')
        );
        return;
      }
      
      setSaving(true);
      
      if (enabled) {
        const authenticated = await biometricService.authenticate(
          t('settings.biometric.setupMessage')
        );
        
        if (!authenticated) {
          Alert.alert(
            t('settings.error.title'),
            t('settings.error.biometricSetupFailed')
          );
          setSaving(false);
          return;
        }
      }
      
      await userProfileService.updatePreferences({
        biometric_enabled: enabled,
      });
      
      setBiometricEnabled(enabled);
      
      Alert.alert(
        t('settings.success.title'),
        enabled ? t('settings.success.biometricEnabled') : t('settings.success.biometricDisabled')
      );
    } catch (error) {
      console.error('Error updating biometric setting:', error);
      Alert.alert(
        t('settings.error.title'),
        t('settings.error.biometricUpdateFailed')
      );
      setBiometricEnabled(biometricEnabled);
    } finally {
      setSaving(false);
    }
  };

  const showLanguageOptions = () => {
    Alert.alert(
      t('settings.language.title'),
      t('settings.language.select'),
      [
        { text: t('settings.language.french'), onPress: () => handleLanguageChange('fr') },
        { text: t('settings.language.malagasy'), onPress: () => handleLanguageChange('mg') },
        { text: t('common.cancel'), style: 'cancel' },
      ]
    );
  };

  const handleLogout = () => {
    Alert.alert(
      t('settings.logout.title'),
      t('settings.logout.message'),
      [
        { text: t('common.cancel'), style: 'cancel' },
        { 
          text: t('settings.logout.confirm'), 
          style: 'destructive',
          onPress: performLogout,
        },
      ]
    );
  };

  const performLogout = async () => {
    try {
      setSaving(true);
      
      await authService.logout();
      await storageService.clear();
      
      navigation.reset({
        index: 0,
        routes: [{ name: 'Login' }],
      });
    } catch (error) {
      console.error('Error during logout:', error);
      Alert.alert(
        t('settings.error.title'),
        t('settings.error.logoutFailed')
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>{t('settings.loading')}</Text>
      </View>
    );
  }

  const getLanguageDisplayName = (lang: string) => {
    switch (lang) {
      case 'fr':
        return t('settings.language.french');
      case 'mg':
        return t('settings.language.malagasy');
      default:
        return lang;
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('settings.language.title')}</Text>
          
          <TouchableOpacity 
            style={styles.settingRow} 
            onPress={showLanguageOptions}
            disabled={saving}
          >
            <View style={styles.settingLeft}>
              <Ionicons name="language-outline" size={24} color={colors.primary} />
              <View style={styles.settingTextContainer}>
                <Text style={styles.settingLabel}>{t('settings.language.current')}</Text>
                <Text style={styles.settingValue}>{getLanguageDisplayName(language)}</Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.text.secondary} />
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('settings.notifications.title')}</Text>
          
          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <Ionicons name="notifications-outline" size={24} color={colors.primary} />
              <View style={styles.settingTextContainer}>
                <Text style={styles.settingLabel}>{t('settings.notifications.push')}</Text>
                <Text style={styles.settingDescription}>
                  {t('settings.notifications.pushDescription')}
                </Text>
              </View>
            </View>
            <Switch
              value={notificationsEnabled}
              onValueChange={handleNotificationsToggle}
              disabled={saving}
              trackColor={{ false: colors.text.secondary, true: colors.primary }}
              thumbColor={colors.white}
            />
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('settings.security.title')}</Text>
          
          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <Ionicons name="finger-print-outline" size={24} color={colors.primary} />
              <View style={styles.settingTextContainer}>
                <Text style={styles.settingLabel}>{t('settings.security.biometric')}</Text>
                <Text style={styles.settingDescription}>
                  {biometricAvailable 
                    ? t('settings.security.biometricDescription') 
                    : t('settings.security.biometricNotAvailable')
                  }
                </Text>
              </View>
            </View>
            <Switch
              value={biometricEnabled}
              onValueChange={handleBiometricToggle}
              disabled={saving || !biometricAvailable}
              trackColor={{ false: colors.text.secondary, true: colors.primary }}
              thumbColor={colors.white}
            />
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('settings.account.title')}</Text>
          
          <TouchableOpacity 
            style={styles.settingRow} 
            onPress={handleLogout}
            disabled={saving}
          >
            <View style={styles.settingLeft}>
              <Ionicons name="log-out-outline" size={24} color={colors.error} />
              <View style={styles.settingTextContainer}>
                <Text style={[styles.settingLabel, styles.dangerText]}>
                  {t('settings.account.logout')}
                </Text>
                <Text style={styles.settingDescription}>
                  {t('settings.account.logoutDescription')}
                </Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.text.secondary} />
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.base,
    color: colors.text.secondary,
  },
  content: {
    padding: spacing.lg,
  },
  section: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold,
    color: colors.text.primary,
    marginBottom: spacing.md,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.sm,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingTextContainer: {
    marginLeft: spacing.md,
    flex: 1,
  },
  settingLabel: {
    fontSize: typography.fontSize.base,
    color: colors.text.primary,
    fontWeight: typography.fontWeight.medium,
  },
  settingValue: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
    marginTop: 2,
  },
  settingDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
    marginTop: 2,
  },
  dangerText: {
    color: colors.error,
  },
});

export default SettingsScreen;