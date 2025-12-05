import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  Switch,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useNotifications } from '../../hooks/useNotifications';
import { NotificationPreferences } from '../../services/notificationService';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';

interface NotificationSettingItemProps {
  title: string;
  description: string;
  value: boolean;
  onValueChange: (value: boolean) => void;
  disabled?: boolean;
}

const NotificationSettingItem: React.FC<NotificationSettingItemProps> = ({
  title,
  description,
  value,
  onValueChange,
  disabled = false,
}) => {
  return (
    <View style={styles.settingItem}>
      <View style={styles.settingText}>
        <Text style={[styles.settingTitle, disabled && styles.disabledText]}>
          {title}
        </Text>
        <Text style={[styles.settingDescription, disabled && styles.disabledText]}>
          {description}
        </Text>
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        disabled={disabled}
        trackColor={{ false: colors.gray400, true: colors.primary }}
        thumbColor={value ? colors.white : colors.gray500}
      />
    </View>
  );
};

export const NotificationSettingsScreen: React.FC = () => {
  const navigation = useNavigation();
  const { 
    getNotificationPreferences, 
    updateNotificationPreferences,
    getLocalNotificationPreferences 
  } = useNotifications();
  
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    paymentReminders: true,
    paymentConfirmations: true,
    expirationAlerts: true,
    generalAlerts: true,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      // Try to get from backend first, fallback to local
      const backendPreferences = await getNotificationPreferences();
      if (backendPreferences) {
        setPreferences(backendPreferences);
      } else {
        const localPreferences = await getLocalNotificationPreferences();
        setPreferences(localPreferences);
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      // Fallback to local preferences
      const localPreferences = await getLocalNotificationPreferences();
      setPreferences(localPreferences);
    } finally {
      setLoading(false);
    }
  };

  const handlePreferenceChange = async (key: keyof NotificationPreferences, value: boolean) => {
    const newPreferences = { ...preferences, [key]: value };
    setPreferences(newPreferences);
    
    try {
      setSaving(true);
      await updateNotificationPreferences(newPreferences);
    } catch (error) {
      console.error('Error updating preferences:', error);
      Alert.alert('Erreur', 'Impossible de sauvegarder les préférences');
      // Revert to previous state
      setPreferences(preferences);
    } finally {
      setSaving(false);
    }
  };

  const handleDisableAll = async () => {
    const newPreferences = {
      paymentReminders: false,
      paymentConfirmations: false,
      expirationAlerts: false,
      generalAlerts: false,
    };
    
    setPreferences(newPreferences);
    
    try {
      setSaving(true);
      await updateNotificationPreferences(newPreferences);
    } catch (error) {
      console.error('Error disabling all notifications:', error);
      Alert.alert('Erreur', 'Impossible de désactiver les notifications');
      // Revert to previous state
      loadPreferences();
    } finally {
      setSaving(false);
    }
  };

  const handleEnableAll = async () => {
    const newPreferences = {
      paymentReminders: true,
      paymentConfirmations: true,
      expirationAlerts: true,
      generalAlerts: true,
    };
    
    setPreferences(newPreferences);
    
    try {
      setSaving(true);
      await updateNotificationPreferences(newPreferences);
    } catch (error) {
      console.error('Error enabling all notifications:', error);
      Alert.alert('Erreur', 'Impossible d\'activer les notifications');
      // Revert to previous state
      loadPreferences();
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Chargement des préférences...</Text>
      </View>
    );
  }

  const allEnabled = Object.values(preferences).every(value => value === true);
  const allDisabled = Object.values(preferences).every(value => value === false);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Paramètres de notification</Text>
        <Text style={styles.headerDescription}>
          Gérez les types de notifications que vous souhaitez recevoir
        </Text>
      </View>

      <View style={styles.quickActions}>
        <TouchableOpacity
          style={[styles.quickButton, allEnabled && styles.quickButtonActive]}
          onPress={handleEnableAll}
          disabled={saving}
        >
          <Text style={[styles.quickButtonText, allEnabled && styles.quickButtonTextActive]}>
            Tout activer
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.quickButton, allDisabled && styles.quickButtonActive]}
          onPress={handleDisableAll}
          disabled={saving}
        >
          <Text style={[styles.quickButtonText, allDisabled && styles.quickButtonTextActive]}>
            Tout désactiver
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.settingsContainer}>
        <NotificationSettingItem
          title="Rappels de paiement"
          description="Recevez des notifications pour les rappels de paiement de vos taxes"
          value={preferences.paymentReminders}
          onValueChange={(value) => handlePreferenceChange('paymentReminders', value)}
          disabled={saving}
        />

        <NotificationSettingItem
          title="Confirmations de paiement"
          description="Recevez des notifications lorsque vos paiements sont confirmés"
          value={preferences.paymentConfirmations}
          onValueChange={(value) => handlePreferenceChange('paymentConfirmations', value)}
          disabled={saving}
        />

        <NotificationSettingItem
          title="Alertes d'expiration"
          description="Recevez des notifications pour les alertes d'expiration de vos documents"
          value={preferences.expirationAlerts}
          onValueChange={(value) => handlePreferenceChange('expirationAlerts', value)}
          disabled={saving}
        />

        <NotificationSettingItem
          title="Alertes générales"
          description="Recevez des notifications pour les alertes générales et mises à jour"
          value={preferences.generalAlerts}
          onValueChange={(value) => handlePreferenceChange('generalAlerts', value)}
          disabled={saving}
        />
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Vous pouvez modifier ces paramètres à tout moment. Les notifications seront
          désactivées si vous refusez les permissions dans les paramètres de votre appareil.
        </Text>
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
    ...typography.body2,
    color: colors.text.secondary,
    marginTop: spacing.md,
  },
  header: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerTitle: {
    ...typography.h2,
    color: colors.text.primary,
    marginBottom: spacing.sm,
  },
  headerDescription: {
    ...typography.body2,
    color: colors.text.secondary,
    lineHeight: 22,
  },
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  quickButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    marginHorizontal: spacing.xs,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.background,
  },
  quickButtonActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  quickButtonText: {
    ...typography.body2,
    color: colors.text.primary,
    textAlign: 'center',
  },
  quickButtonTextActive: {
    color: colors.white,
    fontWeight: '600',
  },
  settingsContainer: {
    backgroundColor: colors.surface,
    marginTop: spacing.md,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  settingText: {
    flex: 1,
    marginRight: spacing.md,
  },
  settingTitle: {
    ...typography.body1,
    color: colors.text.primary,
    fontWeight: '600',
    marginBottom: 2,
  },
  settingDescription: {
    ...typography.body2,
    color: colors.text.secondary,
    lineHeight: 20,
  },
  disabledText: {
    color: colors.gray500,
  },
  footer: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
  },
  footerText: {
    ...typography.caption,
    color: colors.text.tertiary,
    textAlign: 'center',
    lineHeight: 18,
  },
});