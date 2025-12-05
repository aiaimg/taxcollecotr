import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { useNotifications } from '../../hooks/useNotifications';
import { Notification, NotificationType } from '../../types/models';
import { markAsRead, setNotifications, setLoading } from '../../store/slices/notificationSlice';
import { notificationService } from '../../services/notificationService';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';

const NotificationIcon = ({ type }: { type: NotificationType }) => {
  let icon = '🔔';
  let color = colors.primary;

  switch (type) {
    case 'RAPPEL_PAIEMENT':
      icon = '💳';
      color = colors.warning;
      break;
    case 'CONFIRMATION_PAIEMENT':
      icon = '✅';
      color = colors.success;
      break;
    case 'EXPIRATION':
      icon = '⏰';
      color = colors.error;
      break;
    case 'ALERTE':
    default:
      icon = '🔔';
      color = colors.info;
      break;
  }

  return (
    <View style={[styles.iconContainer, { backgroundColor: `${color}20` }]}>
      <Text style={[styles.icon, { color }]}>{icon}</Text>
    </View>
  );
};

const NotificationItem = ({ 
  notification, 
  onPress 
}: { 
  notification: Notification; 
  onPress: (notification: Notification) => void; 
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return "À l'instant";
    } else if (diffInHours < 24) {
      return `Il y a ${Math.floor(diffInHours)}h`;
    } else {
      return date.toLocaleDateString('fr-FR', { 
        day: 'numeric', 
        month: 'short', 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
  };

  return (
    <TouchableOpacity
      style={[styles.notificationItem, !notification.est_lue && styles.unreadItem]}
      onPress={() => onPress(notification)}
    >
      <View style={styles.notificationContent}>
        <NotificationIcon type={notification.type} />
        <View style={styles.notificationText}>
          <Text style={[styles.notificationTitleText, !notification.est_lue && styles.unreadTitleText]}>
            {notification.titre}
          </Text>
          <Text style={styles.notificationContentText} numberOfLines={2}>
            {notification.contenu}
          </Text>
          <Text style={styles.notificationDate}>
            {formatDate(notification.date_creation)}
          </Text>
        </View>
      </View>
      {!notification.est_lue && <View style={styles.unreadDot} />}
    </TouchableOpacity>
  );
};

export const NotificationsScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const { notifications, loading } = useAppSelector(state => state.notifications);
  const { getNotifications, markAsRead } = useNotifications();
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      dispatch(setLoading(true));
      const notificationsData = await getNotifications();
      dispatch(setNotifications(notificationsData));
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleNotificationPress = async (notification: Notification) => {
    try {
      // Mark as read if unread
      if (!notification.est_lue) {
        dispatch(markAsRead(notification.id) as any);
      }
      
      // Navigate based on notification data
      if (notification.data?.vehiclePlaque) {
        navigation.navigate('VehicleStack', {
          screen: 'VehicleDetail',
          params: { plaque: notification.data.vehiclePlaque as string }
        });
      }
    } catch (error) {
      console.error('Error handling notification press:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const { markAllAsRead } = useNotifications();
      await markAllAsRead();
      
      // Update local state
      const updatedNotifications = notifications.map(notification => ({
        ...notification,
        est_lue: true,
      }));
      dispatch(setNotifications(updatedNotifications));
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de marquer toutes les notifications comme lues');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadNotifications();
    setRefreshing(false);
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>🔔</Text>
      <Text style={styles.emptyTitle}>Aucune notification</Text>
      <Text style={styles.emptyText}>
        Vous n'avez pas encore de notifications. Les notifications apparaîtront ici.
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Notifications</Text>
        {notifications.some(n => !n.est_lue) && (
          <TouchableOpacity
            style={styles.markAllButton}
            onPress={handleMarkAllAsRead}
          >
            <Text style={styles.markAllText}>Tout marquer comme lu</Text>
          </TouchableOpacity>
        )}
      </View>

      {loading && notifications.length === 0 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <NotificationItem
              notification={item}
              onPress={handleNotificationPress}
            />
          )}
          contentContainerStyle={notifications.length === 0 ? styles.emptyList : null}
          ListEmptyComponent={renderEmptyState}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ItemSeparatorComponent={() => <View style={styles.separator} />}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerTitle: {
    ...typography.h2,
    color: colors.text.primary,
  },
  markAllButton: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  markAllText: {
    ...typography.body2,
    color: colors.primary,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyList: {
    flex: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: spacing.lg,
  },
  emptyTitle: {
    ...typography.h3,
    color: colors.text.primary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  emptyText: {
    ...typography.body2,
    color: colors.text.secondary,
    textAlign: 'center',
    lineHeight: 22,
  },
  notificationItem: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
  },
  unreadItem: {
    backgroundColor: `${colors.primary}08`,
  },
  notificationContent: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    flex: 1,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  icon: {
    fontSize: 24,
  },
  notificationText: {
    flex: 1,
    marginRight: spacing.sm,
  },
  notificationTitleText: {
    ...typography.body1,
    color: colors.text.primary,
    fontWeight: '600',
    marginBottom: 2,
  },
  unreadTitleText: {
    fontWeight: '700',
  },
  notificationContentText: {
    ...typography.body2,
    color: colors.text.secondary,
    marginBottom: 4,
    lineHeight: 20,
  },
  notificationDate: {
    ...typography.caption,
    color: colors.text.tertiary,
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
    marginTop: 6,
  },
  separator: {
    height: 1,
    backgroundColor: colors.border,
    marginLeft: spacing.lg,
  },
});