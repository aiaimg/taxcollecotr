/**
 * OfflineIndicator Component - Displays network status and sync information
 */

import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from 'react-i18next';
import useNetworkStatus from '../../hooks/useNetworkStatus';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';

interface OfflineIndicatorProps {
  showSyncInfo?: boolean;
  compact?: boolean;
}

const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({ 
  showSyncInfo = true, 
  compact = false 
}) => {
  const { t } = useTranslation();
  const {
    isOnline,
    isOffline,
    isSyncing,
    formattedLastSync,
    pendingActionsCount,
  } = useNetworkStatus();

  // Don't show anything if online and no sync info requested
  if (isOnline && !showSyncInfo) {
    return null;
  }

  // Determine the status to display
  const getStatusContent = () => {
    if (isSyncing) {
      return {
        icon: 'sync' as const,
        text: t('offline.syncing'),
        color: colors.info,
        backgroundColor: colors.infoBackground,
        showSpinner: true,
      };
    }
    
    if (isOffline) {
      return {
        icon: 'cloud-offline' as const,
        text: t('offline.offline'),
        color: colors.warning,
        backgroundColor: colors.warningBackground,
        showSpinner: false,
      };
    }
    
    if (pendingActionsCount > 0) {
      return {
        icon: 'time' as const,
        text: `${pendingActionsCount} ${t('offline.pendingActions')}`,
        color: colors.info,
        backgroundColor: colors.infoBackground,
        showSpinner: false,
      };
    }
    
    // Online with last sync info
    if (formattedLastSync) {
      return {
        icon: 'checkmark-circle' as const,
        text: `${t('offline.lastSync')}: ${formattedLastSync}`,
        color: colors.success,
        backgroundColor: colors.successBackground,
        showSpinner: false,
      };
    }
    
    // Default online state
    return {
      icon: 'cloud-done' as const,
      text: t('offline.online'),
      color: colors.success,
      backgroundColor: colors.successBackground,
      showSpinner: false,
    };
  };

  const status = getStatusContent();

  if (compact) {
    return (
      <View style={[styles.containerCompact, { backgroundColor: status.backgroundColor }]}>
        {status.showSpinner && (
          <ActivityIndicator size="small" color={status.color} style={styles.spinnerCompact} />
        )}
        {!status.showSpinner && (
          <Ionicons name={status.icon} size={14} color={status.color} style={styles.iconCompact} />
        )}
        <Text style={[styles.textCompact, { color: status.color }]}>
          {status.text}
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: status.backgroundColor }]}>
      <View style={styles.content}>
        {status.showSpinner && (
          <ActivityIndicator size="small" color={status.color} style={styles.spinner} />
        )}
        {!status.showSpinner && (
          <Ionicons name={status.icon} size={16} color={status.color} style={styles.icon} />
        )}
        <Text style={[styles.text, { color: status.color }]}>
          {status.text}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    marginHorizontal: spacing.md,
    marginVertical: spacing.sm,
  },
  containerCompact: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 4,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    marginRight: spacing.sm,
  },
  iconCompact: {
    marginRight: spacing.xs,
  },
  spinner: {
    marginRight: spacing.sm,
  },
  spinnerCompact: {
    marginRight: spacing.xs,
  },
  text: {
    ...typography.body2,
    fontWeight: '500',
    textAlign: 'center',
  },
  textCompact: {
    ...typography.caption,
    fontWeight: '500',
  },
});

export default OfflineIndicator;