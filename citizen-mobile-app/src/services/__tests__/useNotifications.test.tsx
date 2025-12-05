import React from 'react';
import { renderHook, act, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { store } from '../../store/store';
import { useNotifications } from '../../hooks/useNotifications';
import { notificationService } from '../notificationService';
import { addNotification, setUnreadCount } from '../../store/slices/notificationSlice';

// Mock dependencies
jest.mock('../notificationService');
jest.mock('../../store/slices/notificationSlice');

const mockNavigate = jest.fn();
const mockDispatch = jest.fn();

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: mockNavigate,
  }),
  useDispatch: () => mockDispatch,
}));

// Mock Redux store
jest.mock('../../store/hooks', () => ({
  useAppDispatch: () => mockDispatch,
  useAppSelector: jest.fn(),
}));

const createTestWrapper = () => {
  const Stack = createNativeStackNavigator();
  
  return function TestWrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <NavigationContainer>
          <Stack.Navigator>
            <Stack.Screen name="Test" component={() => <>{children}</>} />
          </Stack.Navigator>
        </NavigationContainer>
      </Provider>
    );
  };
};

describe('useNotifications Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
    mockDispatch.mockClear();
  });

  describe('initialization', () => {
    it('should initialize notification service on mount', async () => {
      const mockInitialize = jest.fn().mockResolvedValue(undefined);
      const mockSetupForeground = jest.fn();
      const mockSetupBackground = jest.fn();
      const mockGetUnreadCount = jest.fn().mockResolvedValue(5);

      (notificationService.initialize as jest.Mock) = mockInitialize;
      (notificationService.setupForegroundNotificationHandler as jest.Mock) = mockSetupForeground;
      (notificationService.setupBackgroundNotificationHandler as jest.Mock) = mockSetupBackground;
      (notificationService.getUnreadCount as jest.Mock) = mockGetUnreadCount;

      const { result } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      await waitFor(() => {
        expect(mockInitialize).toHaveBeenCalled();
        expect(mockSetupForeground).toHaveBeenCalled();
        expect(mockSetupBackground).toHaveBeenCalled();
        expect(mockGetUnreadCount).toHaveBeenCalled();
      });

      expect(mockDispatch).toHaveBeenCalledWith(setUnreadCount(5));
    });

    it('should handle initialization errors gracefully', async () => {
      const mockInitialize = jest.fn().mockRejectedValue(new Error('Initialization failed'));
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

      (notificationService.initialize as jest.Mock) = mockInitialize;

      const { result } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      await waitFor(() => {
        expect(mockInitialize).toHaveBeenCalled();
      });

      expect(consoleErrorSpy).toHaveBeenCalledWith('Error initializing notifications:', expect.any(Error));
      
      consoleErrorSpy.mockRestore();
    });
  });

  describe('foreground notification handling', () => {
    it('should add notification to store and update unread count', async () => {
      const mockNotification = {
        id: 1,
        titre: 'Test Notification',
        contenu: 'Test content',
        type: 'ALERTE' as const,
        est_lue: false,
        date_creation: '2023-01-01T00:00:00Z',
      };

      const mockSetupForeground = jest.fn((handler) => {
        // Simulate notification received
        handler(mockNotification);
      });

      const mockGetUnreadCount = jest.fn().mockResolvedValue(3);

      (notificationService.setupForegroundNotificationHandler as jest.Mock) = mockSetupForeground;
      (notificationService.getUnreadCount as jest.Mock) = mockGetUnreadCount;

      const { result } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      await waitFor(() => {
        expect(mockSetupForeground).toHaveBeenCalled();
      });

      expect(mockDispatch).toHaveBeenCalledWith(addNotification(mockNotification));
      expect(mockGetUnreadCount).toHaveBeenCalled();
      expect(mockDispatch).toHaveBeenCalledWith(setUnreadCount(3));
    });
  });

  describe('background notification handling', () => {
    it('should navigate to vehicle detail for payment notifications', async () => {
      const mockNotification = {
        id: 2,
        titre: 'Payment Reminder',
        contenu: 'Payment due soon',
        type: 'RAPPEL_PAIEMENT' as const,
        est_lue: false,
        date_creation: '2023-01-01T00:00:00Z',
        data: { vehiclePlaque: '1234ABC' },
      };

      const mockSetupBackground = jest.fn((handler) => {
        // Simulate background notification
        handler(mockNotification);
      });

      (notificationService.setupBackgroundNotificationHandler as jest.Mock) = mockSetupBackground;

      const { result } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      await waitFor(() => {
        expect(mockSetupBackground).toHaveBeenCalled();
      });

      expect(mockNavigate).toHaveBeenCalledWith('VehicleStack', {
        screen: 'VehicleDetail',
        params: { plaque: '1234ABC' },
      });
    });

    it('should navigate to vehicles screen when no vehicle plaque in payment notification', async () => {
      const mockNotification = {
        id: 3,
        titre: 'Payment Confirmation',
        contenu: 'Payment successful',
        type: 'CONFIRMATION_PAIEMENT' as const,
        est_lue: false,
        date_creation: '2023-01-01T00:00:00Z',
        data: {},
      };

      const mockSetupBackground = jest.fn((handler) => {
        handler(mockNotification);
      });

      (notificationService.setupBackgroundNotificationHandler as jest.Mock) = mockSetupBackground;

      const { result } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      await waitFor(() => {
        expect(mockSetupBackground).toHaveBeenCalled();
      });

      expect(mockNavigate).toHaveBeenCalledWith('Main', { screen: 'Vehicles' });
    });

    it('should navigate to vehicle detail for expiration notifications', async () => {
      const mockNotification = {
        id: 4,
        titre: 'Document Expiration',
        contenu: 'Document expires soon',
        type: 'EXPIRATION' as const,
        est_lue: false,
        date_creation: '2023-01-01T00:00:00Z',
        data: { vehiclePlaque: '5678DEF' },
      };

      const mockSetupBackground = jest.fn((handler) => {
        handler(mockNotification);
      });

      (notificationService.setupBackgroundNotificationHandler as jest.Mock) = mockSetupBackground;

      const { result } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      await waitFor(() => {
        expect(mockSetupBackground).toHaveBeenCalled();
      });

      expect(mockNavigate).toHaveBeenCalledWith('VehicleStack', {
        screen: 'VehicleDetail',
        params: { plaque: '5678DEF' },
      });
    });

    it('should navigate to notifications screen for general alerts', async () => {
      const mockNotification = {
        id: 5,
        titre: 'General Alert',
        contenu: 'General system alert',
        type: 'ALERTE' as const,
        est_lue: false,
        date_creation: '2023-01-01T00:00:00Z',
        data: {},
      };

      const mockSetupBackground = jest.fn((handler) => {
        handler(mockNotification);
      });

      (notificationService.setupBackgroundNotificationHandler as jest.Mock) = mockSetupBackground;

      const { result } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      await waitFor(() => {
        expect(mockSetupBackground).toHaveBeenCalled();
      });

      expect(mockNavigate).toHaveBeenCalledWith('Main', { screen: 'Notifications' });
    });
  });

  describe('exposed methods', () => {
    it('should expose notification service methods', () => {
      const { result } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      expect(result.current).toHaveProperty('markAsRead');
      expect(result.current).toHaveProperty('markAllAsRead');
      expect(result.current).toHaveProperty('getNotifications');
      expect(result.current).toHaveProperty('getNotificationPreferences');
      expect(result.current).toHaveProperty('updateNotificationPreferences');
      expect(result.current).toHaveProperty('getLocalNotificationPreferences');
      expect(result.current).toHaveProperty('getUnreadCount');

      expect(result.current.markAsRead).toBe(notificationService.markAsRead);
      expect(result.current.markAllAsRead).toBe(notificationService.markAllAsRead);
      expect(result.current.getNotifications).toBe(notificationService.getNotifications);
      expect(result.current.getNotificationPreferences).toBe(notificationService.getNotificationPreferences);
      expect(result.current.updateNotificationPreferences).toBe(notificationService.updateNotificationPreferences);
      expect(result.current.getLocalNotificationPreferences).toBe(notificationService.getLocalNotificationPreferences);
      expect(result.current.getUnreadCount).toBe(notificationService.getUnreadCount);
    });
  });

  describe('cleanup', () => {
    it('should cleanup notification listeners on unmount', () => {
      const mockCleanup = jest.fn();
      (notificationService.cleanup as jest.Mock) = mockCleanup;

      const { unmount } = renderHook(() => useNotifications(), {
        wrapper: createTestWrapper(),
      });

      unmount();

      expect(mockCleanup).toHaveBeenCalled();
    });
  });
});