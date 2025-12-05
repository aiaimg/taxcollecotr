import { useEffect, useCallback } from 'react';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch } from '../store/hooks';
import { notificationService } from '../services/notificationService';
import { Notification } from '../types/models';
import { addNotification, setUnreadCount } from '../store/slices/notificationSlice';
import { RootStackParamList } from '../types/navigation';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

export const useNotifications = () => {
  const navigation = useNavigation<NavigationProp>();
  const dispatch = useAppDispatch();

  // Handle foreground notifications
  const handleForegroundNotification = useCallback((notification: Notification) => {
    // Add notification to Redux store
    dispatch(addNotification(notification));
    
    // Update unread count
    notificationService.getUnreadCount().then(count => {
      dispatch(setUnreadCount(count));
    });
  }, [dispatch]);

  // Handle background/terminated notifications
  const handleBackgroundNotification = useCallback((notification: Notification) => {
    // Navigate to appropriate screen based on notification type
    const { type, data } = notification;
    
    switch (type) {
      case 'RAPPEL_PAIEMENT':
      case 'CONFIRMATION_PAIEMENT':
        // Navigate to payment history or vehicle detail
        if (data?.vehiclePlaque) {
          navigation.navigate('VehicleStack', {
            screen: 'VehicleDetail',
            params: { plaque: data.vehiclePlaque as string }
          });
        } else {
          navigation.navigate('Main', { screen: 'Vehicles' });
        }
        break;
      case 'EXPIRATION':
        // Navigate to vehicle detail or payment method
        if (data?.vehiclePlaque) {
          navigation.navigate('VehicleStack', {
            screen: 'VehicleDetail',
            params: { plaque: data.vehiclePlaque as string }
          });
        } else {
          navigation.navigate('Main', { screen: 'Vehicles' });
        }
        break;
      case 'ALERTE':
      default:
        // Navigate to notifications screen
        navigation.navigate('Main', { screen: 'Notifications' });
        break;
    }
  }, [navigation]);

  // Initialize notifications on app start
  useEffect(() => {
    const initializeNotifications = async () => {
      try {
        // Initialize notification service
        await notificationService.initialize();
        
        // Setup notification handlers
        notificationService.setupForegroundNotificationHandler(handleForegroundNotification);
        notificationService.setupBackgroundNotificationHandler(handleBackgroundNotification);
        
        // Get initial unread count
        const unreadCount = await notificationService.getUnreadCount();
        dispatch(setUnreadCount(unreadCount));
      } catch (error) {
        console.error('Error initializing notifications:', error);
      }
    };

    initializeNotifications();

    // Cleanup on unmount
    return () => {
      notificationService.cleanup();
    };
  }, [dispatch, handleForegroundNotification, handleBackgroundNotification]);

  return {
    // Expose notification service methods
    markAsRead: notificationService.markAsRead,
    markAllAsRead: notificationService.markAllAsRead,
    getNotifications: notificationService.getNotifications,
    getNotificationPreferences: notificationService.getNotificationPreferences,
    updateNotificationPreferences: notificationService.updateNotificationPreferences,
    getLocalNotificationPreferences: notificationService.getLocalNotificationPreferences,
    getUnreadCount: notificationService.getUnreadCount,
  };
};