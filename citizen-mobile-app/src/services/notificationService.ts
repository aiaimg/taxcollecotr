import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import apiClient from '../api/client';
import { Notification, NotificationType } from '../types/models';
import storageService from './storageService';

export interface NotificationToken {
  token: string;
  platform: 'ios' | 'android' | 'web';
}

export interface NotificationPreferences {
  paymentReminders: boolean;
  paymentConfirmations: boolean;
  expirationAlerts: boolean;
  generalAlerts: boolean;
}

class NotificationService {
  private static instance: NotificationService;
  private notificationListener: any;
  private responseListener: any;

  private constructor() {}

  static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  async initialize(): Promise<void> {
    // Configure notification handler
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
        shouldShowBanner: true,
        shouldShowList: true,
      }),
    });

    // Request permissions
    await this.requestPermissions();
    
    // Register for push notifications
    await this.registerForPushNotifications();
  }

  async requestPermissions(): Promise<boolean> {
    if (!Device.isDevice) {
      console.log('Must use physical device for Push Notifications');
      return false;
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return false;
    }
    
    return true;
  }

  async registerForPushNotifications(): Promise<string | null> {
    try {
      const hasPermission = await this.requestPermissions();
      if (!hasPermission) {
        return null;
      }

      const token = (await Notifications.getExpoPushTokenAsync()).data;
      
      // Store token locally
      await storageService.set('pushToken', token);
      
      // Register with backend
      await this.registerTokenWithBackend(token);
      
      return token;
    } catch (error: any) {
      // Suppress specific error on web/simulators where push service is not available
      if (error?.message?.includes('push service not available') || error?.code === 'ERR_PUSH_SERVICE_NOT_AVAILABLE') {
        console.log('Push notifications are not available in this environment');
        return null;
      }
      console.error('Error registering for push notifications:', error);
      return null;
    }
  }

  async registerTokenWithBackend(token: string): Promise<void> {
    try {
      const platform = Platform.OS as 'ios' | 'android' | 'web';
      const tokenData: NotificationToken = { token, platform };
      
      await apiClient.post('/api/notifications/register-token/', tokenData);
    } catch (error) {
      console.error('Error registering token with backend:', error);
      throw error;
    }
  }

  async unregisterToken(): Promise<void> {
    try {
      const token = await storageService.get<string>('pushToken');
      if (token) {
        await apiClient.post('/api/notifications/unregister-token/', { token });
        await storageService.delete('pushToken');
      }
    } catch (error) {
      console.error('Error unregistering token:', error);
    }
  }

  // Foreground notification handler
  setupForegroundNotificationHandler(onNotification: (notification: Notification) => void): void {
    this.notificationListener = Notifications.addNotificationReceivedListener((response) => {
      const notification = this.parseExpoNotification(response);
      onNotification(notification);
    });
  }

  // Background/terminated notification handler
  setupBackgroundNotificationHandler(onNotification: (notification: Notification) => void): void {
    this.responseListener = Notifications.addNotificationResponseReceivedListener((response) => {
      const notification = this.parseExpoNotification(response.notification);
      onNotification(notification);
    });
  }

  // Parse Expo notification to our Notification model
  private parseExpoNotification(expoNotification: Notifications.Notification): Notification {
    const { request } = expoNotification;
    const content = request.content;
    
    return {
      id: Date.now(), // Use timestamp as temporary ID for local notifications
      titre: content.title || 'Notification',
      contenu: content.body || '',
      type: this.determineNotificationType(content.data),
      est_lue: false,
      date_creation: new Date().toISOString(),
      data: content.data,
    };
  }

  private determineNotificationType(data?: any): NotificationType {
    if (!data?.type) return 'ALERTE';
    
    switch (data.type) {
      case 'payment_reminder':
        return 'RAPPEL_PAIEMENT';
      case 'payment_confirmation':
        return 'CONFIRMATION_PAIEMENT';
      case 'expiration':
        return 'EXPIRATION';
      case 'alert':
        return 'ALERTE';
      default:
        return 'ALERTE';
    }
  }

  // Get saved notifications from backend
  async getNotifications(): Promise<Notification[]> {
    try {
      const response = await apiClient.get('/api/notifications/');
      return response.data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return [];
    }
  }

  // Mark notification as read
  async markAsRead(notificationId: number): Promise<void> {
    try {
      await apiClient.patch(`/api/notifications/${notificationId}/mark-read/`);
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  }

  // Mark all notifications as read
  async markAllAsRead(): Promise<void> {
    try {
      await apiClient.patch('/api/notifications/mark-all-read/');
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  }

  // Get notification preferences
  async getNotificationPreferences(): Promise<NotificationPreferences> {
    try {
      const response = await apiClient.get('/api/notifications/preferences/');
      return response.data;
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
      // Return default preferences
      return {
        paymentReminders: true,
        paymentConfirmations: true,
        expirationAlerts: true,
        generalAlerts: true,
      };
    }
  }

  // Update notification preferences
  async updateNotificationPreferences(preferences: NotificationPreferences): Promise<void> {
    try {
      await apiClient.patch('/api/notifications/preferences/', preferences);
      
      // Update local storage
      await storageService.set('notificationPreferences', preferences);
    } catch (error) {
      console.error('Error updating notification preferences:', error);
      throw error;
    }
  }

  // Get local notification preferences
  async getLocalNotificationPreferences(): Promise<NotificationPreferences> {
    try {
      const preferences = await storageService.get<NotificationPreferences>('notificationPreferences');
      if (preferences) {
        return preferences;
      }
    } catch (error) {
      console.error('Error reading local notification preferences:', error);
    }
    
    // Return default preferences
    return {
      paymentReminders: true,
      paymentConfirmations: true,
      expirationAlerts: true,
      generalAlerts: true,
    };
  }

  // Get unread notification count
  async getUnreadCount(): Promise<number> {
    try {
      const response = await apiClient.get('/api/notifications/unread-count/');
      return response.data.count;
    } catch (error) {
      console.error('Error fetching unread count:', error);
      return 0;
    }
  }

  // Cleanup listeners
  cleanup(): void {
    if (this.notificationListener) {
      this.notificationListener.remove();
    }
    if (this.responseListener) {
      this.responseListener.remove();
    }
  }
}

export const notificationService = NotificationService.getInstance();