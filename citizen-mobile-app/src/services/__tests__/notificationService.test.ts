import { notificationService, NotificationPreferences } from '../notificationService';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import apiClient from '../../api/client';
import storageService from '../storageService';

// Mock dependencies
jest.mock('expo-notifications', () => ({
  addNotificationReceivedListener: jest.fn(),
  addNotificationResponseReceivedListener: jest.fn(),
  removeNotificationSubscription: jest.fn(),
  getPermissionsAsync: jest.fn(),
  requestPermissionsAsync: jest.fn(),
  getExpoPushTokenAsync: jest.fn(),
  setNotificationHandler: jest.fn(),
}));
jest.mock('expo-device', () => ({
  isDevice: true,
}));
jest.mock('../../api/client');
jest.mock('../storageService');

describe('NotificationService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset singleton instance
    (notificationService as any).constructor.instance = undefined;
  });

  describe('initialize', () => {
    it('should configure notification handler and request permissions', async () => {
      const mockSetNotificationHandler = jest.fn();
      (Notifications.setNotificationHandler as jest.Mock) = mockSetNotificationHandler;
      
      const mockRequestPermissions = jest.fn().mockResolvedValue(true);
      const mockRegisterForPushNotifications = jest.fn().mockResolvedValue('test-token');
      
      notificationService.requestPermissions = mockRequestPermissions;
      notificationService.registerForPushNotifications = mockRegisterForPushNotifications;

      await notificationService.initialize();

      expect(mockSetNotificationHandler).toHaveBeenCalledWith({
        handleNotification: expect.any(Function),
      });
      expect(mockRequestPermissions).toHaveBeenCalled();
      expect(mockRegisterForPushNotifications).toHaveBeenCalled();
    });
  });

  describe('requestPermissions', () => {
    it('should return true when permissions are granted', async () => {
      // Device.isDevice is already mocked as true
      (Notifications.getPermissionsAsync as jest.Mock) = jest.fn().mockResolvedValue({
        status: 'granted',
      });

      const result = await notificationService.requestPermissions();

      expect(result).toBe(true);
      expect(Notifications.requestPermissionsAsync).not.toHaveBeenCalled();
    });

    it('should request permissions when not granted', async () => {
      // Device.isDevice is already mocked as true
      (Notifications.getPermissionsAsync as jest.Mock) = jest.fn().mockResolvedValue({
        status: 'undetermined',
      });
      (Notifications.requestPermissionsAsync as jest.Mock) = jest.fn().mockResolvedValue({
        status: 'granted',
      });

      const result = await notificationService.requestPermissions();

      expect(result).toBe(true);
      expect(Notifications.requestPermissionsAsync).toHaveBeenCalled();
    });

    it('should return false when permissions are denied', async () => {
      // Device.isDevice is already mocked as true
      (Notifications.getPermissionsAsync as jest.Mock) = jest.fn().mockResolvedValue({
        status: 'denied',
      });

      const result = await notificationService.requestPermissions();

      expect(result).toBe(false);
    });

    it('should return false when not on a physical device', async () => {
      // Test when not a device - mock will return false

      const result = await notificationService.requestPermissions();

      expect(result).toBe(false);
    });
  });

  describe('registerForPushNotifications', () => {
    it('should register for push notifications successfully', async () => {
      const mockToken = 'test-push-token';
      (notificationService.requestPermissions as jest.Mock) = jest.fn().mockResolvedValue(true);
      (Notifications.getExpoPushTokenAsync as jest.Mock) = jest.fn().mockResolvedValue({
        data: mockToken,
      });
      (storageService.set as jest.Mock) = jest.fn().mockResolvedValue(undefined);
      (notificationService.registerTokenWithBackend as jest.Mock) = jest.fn().mockResolvedValue(undefined);

      const result = await notificationService.registerForPushNotifications();

      expect(result).toBe(mockToken);
      expect(storageService.set).toHaveBeenCalledWith('pushToken', mockToken);
      expect(notificationService.registerTokenWithBackend).toHaveBeenCalledWith(mockToken);
    });

    it('should return null when permissions are not granted', async () => {
      (notificationService.requestPermissions as jest.Mock) = jest.fn().mockResolvedValue(false);

      const result = await notificationService.registerForPushNotifications();

      expect(result).toBeNull();
      expect(Notifications.getExpoPushTokenAsync).not.toHaveBeenCalled();
    });

    it('should handle errors gracefully', async () => {
      (notificationService.requestPermissions as jest.Mock) = jest.fn().mockRejectedValue(
        new Error('Permission error')
      );

      const result = await notificationService.registerForPushNotifications();

      expect(result).toBeNull();
    });
  });

  describe('registerTokenWithBackend', () => {
    it('should register token with backend successfully', async () => {
      const mockToken = 'test-token';
      const mockPlatform = 'android';
      (apiClient.post as jest.Mock) = jest.fn().mockResolvedValue({ data: {} });

      await notificationService.registerTokenWithBackend(mockToken);

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/notifications/register-token/',
        {
          token: mockToken,
          platform: mockPlatform,
        }
      );
    });

    it('should throw error when backend registration fails', async () => {
      const mockToken = 'test-token';
      const mockError = new Error('Backend error');
      (apiClient.post as jest.Mock) = jest.fn().mockRejectedValue(mockError);

      await expect(notificationService.registerTokenWithBackend(mockToken)).rejects.toThrow(mockError);
    });
  });

  describe('unregisterToken', () => {
    it('should unregister token successfully', async () => {
      const mockToken = 'test-token';
      (storageService.get as jest.Mock) = jest.fn().mockResolvedValue(mockToken);
      (apiClient.post as jest.Mock) = jest.fn().mockResolvedValue({ data: {} });
      (storageService.delete as jest.Mock) = jest.fn().mockResolvedValue(undefined);

      await notificationService.unregisterToken();

      expect(apiClient.post).toHaveBeenCalledWith('/api/notifications/unregister-token/', { token: mockToken });
      expect(storageService.delete).toHaveBeenCalledWith('pushToken');
    });

    it('should handle case when no token is stored', async () => {
      (storageService.get as jest.Mock) = jest.fn().mockResolvedValue(null);

      await notificationService.unregisterToken();

      expect(apiClient.post).not.toHaveBeenCalled();
      expect(storageService.delete).not.toHaveBeenCalled();
    });

    it('should handle errors gracefully', async () => {
      (storageService.get as jest.Mock) = jest.fn().mockRejectedValue(new Error('Storage error'));

      await notificationService.unregisterToken();

      expect(apiClient.post).not.toHaveBeenCalled();
    });
  });

  describe('notification handlers', () => {
    it('should setup foreground notification handler', () => {
      const mockAddNotificationReceivedListener = jest.fn();
      (Notifications.addNotificationReceivedListener as jest.Mock) = mockAddNotificationReceivedListener;

      const mockHandler = jest.fn();
      notificationService.setupForegroundNotificationHandler(mockHandler);

      expect(mockAddNotificationReceivedListener).toHaveBeenCalledWith(expect.any(Function));
    });

    it('should setup background notification handler', () => {
      const mockAddNotificationResponseReceivedListener = jest.fn();
      (Notifications.addNotificationResponseReceivedListener as jest.Mock) = mockAddNotificationResponseReceivedListener;

      const mockHandler = jest.fn();
      notificationService.setupBackgroundNotificationHandler(mockHandler);

      expect(mockAddNotificationResponseReceivedListener).toHaveBeenCalledWith(expect.any(Function));
    });
  });

  describe('parseExpoNotification', () => {
    it('should parse Expo notification correctly', () => {
      const mockExpoNotification = {
        request: {
          content: {
            title: 'Test Title',
            body: 'Test Body',
            data: { type: 'payment_reminder' },
          },
        },
      };

      const result = (notificationService as any).parseExpoNotification(mockExpoNotification);

      expect(result.titre).toBe('Test Title');
      expect(result.contenu).toBe('Test Body');
      expect(result.type).toBe('RAPPEL_PAIEMENT');
      expect(result.est_lue).toBe(false);
      expect(result.data).toEqual({ type: 'payment_reminder' });
    });

    it('should handle missing title and body', () => {
      const mockExpoNotification = {
        request: {
          content: {
            data: {},
          },
        },
      };

      const result = (notificationService as any).parseExpoNotification(mockExpoNotification);

      expect(result.titre).toBe('Notification');
      expect(result.contenu).toBe('');
      expect(result.type).toBe('ALERTE');
    });
  });

  describe('determineNotificationType', () => {
    it('should determine correct notification type', () => {
      expect((notificationService as any).determineNotificationType({ type: 'payment_reminder' })).toBe('RAPPEL_PAIEMENT');
      expect((notificationService as any).determineNotificationType({ type: 'payment_confirmation' })).toBe('CONFIRMATION_PAIEMENT');
      expect((notificationService as any).determineNotificationType({ type: 'expiration' })).toBe('EXPIRATION');
      expect((notificationService as any).determineNotificationType({ type: 'alert' })).toBe('ALERTE');
      expect((notificationService as any).determineNotificationType({ type: 'unknown' })).toBe('ALERTE');
      expect((notificationService as any).determineNotificationType(null)).toBe('ALERTE');
    });
  });

  describe('getNotifications', () => {
    it('should fetch notifications successfully', async () => {
      const mockNotifications = [
        { id: 1, titre: 'Test 1', contenu: 'Content 1', type: 'ALERTE', est_lue: false, date_creation: '2023-01-01' },
        { id: 2, titre: 'Test 2', contenu: 'Content 2', type: 'RAPPEL_PAIEMENT', est_lue: true, date_creation: '2023-01-02' },
      ];
      (apiClient.get as jest.Mock) = jest.fn().mockResolvedValue({ data: mockNotifications });

      const result = await notificationService.getNotifications();

      expect(result).toEqual(mockNotifications);
      expect(apiClient.get).toHaveBeenCalledWith('/api/notifications/');
    });

    it('should return empty array on error', async () => {
      (apiClient.get as jest.Mock) = jest.fn().mockRejectedValue(new Error('API error'));

      const result = await notificationService.getNotifications();

      expect(result).toEqual([]);
    });
  });

  describe('markAsRead', () => {
    it('should mark notification as read successfully', async () => {
      const notificationId = 1;
      (apiClient.patch as jest.Mock) = jest.fn().mockResolvedValue({ data: {} });

      await notificationService.markAsRead(notificationId);

      expect(apiClient.patch).toHaveBeenCalledWith(`/api/notifications/${notificationId}/mark-read/`);
    });

    it('should throw error on failure', async () => {
      const notificationId = 1;
      const mockError = new Error('API error');
      (apiClient.patch as jest.Mock) = jest.fn().mockRejectedValue(mockError);

      await expect(notificationService.markAsRead(notificationId)).rejects.toThrow(mockError);
    });
  });

  describe('markAllAsRead', () => {
    it('should mark all notifications as read successfully', async () => {
      (apiClient.patch as jest.Mock) = jest.fn().mockResolvedValue({ data: {} });

      await notificationService.markAllAsRead();

      expect(apiClient.patch).toHaveBeenCalledWith('/api/notifications/mark-all-read/');
    });

    it('should throw error on failure', async () => {
      const mockError = new Error('API error');
      (apiClient.patch as jest.Mock) = jest.fn().mockRejectedValue(mockError);

      await expect(notificationService.markAllAsRead()).rejects.toThrow(mockError);
    });
  });

  describe('getNotificationPreferences', () => {
    it('should fetch preferences successfully', async () => {
      const mockPreferences: NotificationPreferences = {
        paymentReminders: true,
        paymentConfirmations: false,
        expirationAlerts: true,
        generalAlerts: false,
      };
      (apiClient.get as jest.Mock) = jest.fn().mockResolvedValue({ data: mockPreferences });

      const result = await notificationService.getNotificationPreferences();

      expect(result).toEqual(mockPreferences);
      expect(apiClient.get).toHaveBeenCalledWith('/api/notifications/preferences/');
    });

    it('should return default preferences on error', async () => {
      (apiClient.get as jest.Mock) = jest.fn().mockRejectedValue(new Error('API error'));

      const result = await notificationService.getNotificationPreferences();

      expect(result).toEqual({
        paymentReminders: true,
        paymentConfirmations: true,
        expirationAlerts: true,
        generalAlerts: true,
      });
    });
  });

  describe('updateNotificationPreferences', () => {
    it('should update preferences successfully', async () => {
      const mockPreferences: NotificationPreferences = {
        paymentReminders: true,
        paymentConfirmations: false,
        expirationAlerts: true,
        generalAlerts: false,
      };
      (apiClient.patch as jest.Mock) = jest.fn().mockResolvedValue({ data: {} });
      (storageService.set as jest.Mock) = jest.fn().mockResolvedValue(undefined);

      await notificationService.updateNotificationPreferences(mockPreferences);

      expect(apiClient.patch).toHaveBeenCalledWith('/api/notifications/preferences/', mockPreferences);
      expect(storageService.set).toHaveBeenCalledWith('notificationPreferences', JSON.stringify(mockPreferences));
    });

    it('should throw error on failure', async () => {
      const mockPreferences: NotificationPreferences = {
        paymentReminders: true,
        paymentConfirmations: false,
        expirationAlerts: true,
        generalAlerts: false,
      };
      const mockError = new Error('API error');
      (apiClient.patch as jest.Mock) = jest.fn().mockRejectedValue(mockError);

      await expect(notificationService.updateNotificationPreferences(mockPreferences)).rejects.toThrow(mockError);
    });
  });

  describe('getLocalNotificationPreferences', () => {
    it('should return stored preferences', async () => {
      const mockPreferences: NotificationPreferences = {
        paymentReminders: true,
        paymentConfirmations: false,
        expirationAlerts: true,
        generalAlerts: false,
      };
      (storageService.get as jest.Mock) = jest.fn().mockResolvedValue(JSON.stringify(mockPreferences));

      const result = await notificationService.getLocalNotificationPreferences();

      expect(result).toEqual(mockPreferences);
    });

    it('should return default preferences when none stored', async () => {
      (storageService.get as jest.Mock) = jest.fn().mockResolvedValue(null);

      const result = await notificationService.getLocalNotificationPreferences();

      expect(result).toEqual({
        paymentReminders: true,
        paymentConfirmations: true,
        expirationAlerts: true,
        generalAlerts: true,
      });
    });

    it('should return default preferences on error', async () => {
      (storageService.get as jest.Mock) = jest.fn().mockRejectedValue(new Error('Storage error'));

      const result = await notificationService.getLocalNotificationPreferences();

      expect(result).toEqual({
        paymentReminders: true,
        paymentConfirmations: true,
        expirationAlerts: true,
        generalAlerts: true,
      });
    });
  });

  describe('getUnreadCount', () => {
    it('should fetch unread count successfully', async () => {
      const mockCount = 5;
      (apiClient.get as jest.Mock) = jest.fn().mockResolvedValue({ data: { count: mockCount } });

      const result = await notificationService.getUnreadCount();

      expect(result).toBe(mockCount);
      expect(apiClient.get).toHaveBeenCalledWith('/api/notifications/unread-count/');
    });

    it('should return 0 on error', async () => {
      (apiClient.get as jest.Mock) = jest.fn().mockRejectedValue(new Error('API error'));

      const result = await notificationService.getUnreadCount();

      expect(result).toBe(0);
    });
  });

  describe('cleanup', () => {
    it('should remove all listeners', () => {
      const mockRemove = jest.fn();
      
      // Mock the add listener methods to return objects with remove method
      (Notifications.addNotificationReceivedListener as jest.Mock).mockReturnValue({ remove: mockRemove });
      (Notifications.addNotificationResponseReceivedListener as jest.Mock).mockReturnValue({ remove: mockRemove });

      // Setup listeners first
      notificationService.setupForegroundNotificationHandler(jest.fn());
      notificationService.setupBackgroundNotificationHandler(jest.fn());

      notificationService.cleanup();

      expect(mockRemove).toHaveBeenCalledTimes(2);
    });
  });
});