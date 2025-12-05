// Simple test to verify notification slice functionality
import { 
  addNotification, 
  setNotifications, 
  markAsRead, 
  markAllAsRead, 
  setUnreadCount 
} from '../store/slices/notificationSlice';
import { NotificationType } from '../types/models';

describe('Notification Slice - Basic Tests', () => {
  const mockNotification = {
    id: 1,
    titre: 'Test Notification',
    contenu: 'Test content',
    type: 'ALERTE' as NotificationType,
    est_lue: false,
    date_creation: '2023-01-01T00:00:00Z',
  };

  test('addNotification action should be created correctly', () => {
    const action = addNotification(mockNotification);
    expect(action.type).toBe('notifications/addNotification');
    expect(action.payload).toEqual(mockNotification);
  });

  test('setNotifications action should be created correctly', () => {
    const notifications = [mockNotification];
    const action = setNotifications(notifications);
    expect(action.type).toBe('notifications/setNotifications');
    expect(action.payload).toEqual(notifications);
  });

  test('markAsRead action should be created correctly', () => {
    const action = markAsRead(1);
    expect(action.type).toBe('notifications/markAsRead');
    expect(action.payload).toBe(1);
  });

  test('markAllAsRead action should be created correctly', () => {
    const action = markAllAsRead();
    expect(action.type).toBe('notifications/markAllAsRead');
    expect(action.payload).toBeUndefined();
  });

  test('setUnreadCount action should be created correctly', () => {
    const action = setUnreadCount(5);
    expect(action.type).toBe('notifications/setUnreadCount');
    expect(action.payload).toBe(5);
  });
});