import notificationReducer, {
  addNotification,
  setNotifications,
  markAsRead,
  markAllAsRead,
  setUnreadCount,
  setLoading,
  setError,
  clearNotifications,
} from '../../store/slices/notificationSlice';
import { Notification, NotificationType } from '../../types/models';

describe('notificationSlice', () => {
  const initialState = {
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null,
  };

  const mockNotification: Notification = {
    id: 1,
    titre: 'Test Notification',
    contenu: 'Test content',
    type: 'ALERTE' as NotificationType,
    est_lue: false,
    date_creation: '2023-01-01T00:00:00Z',
  };

  describe('addNotification', () => {
    it('should add a notification to the beginning of the list', () => {
      const action = addNotification(mockNotification);
      const state = notificationReducer(initialState, action);

      expect(state.notifications).toHaveLength(1);
      expect(state.notifications[0]).toEqual(mockNotification);
      expect(state.unreadCount).toBe(1);
    });

    it('should increment unread count when adding unread notification', () => {
      const stateWithNotification = {
        ...initialState,
        notifications: [mockNotification],
        unreadCount: 1,
      };

      const newNotification = { ...mockNotification, id: 2 };
      const action = addNotification(newNotification);
      const state = notificationReducer(stateWithNotification, action);

      expect(state.notifications).toHaveLength(2);
      expect(state.unreadCount).toBe(2);
    });
  });

  describe('setNotifications', () => {
    it('should replace all notifications', () => {
      const notifications = [
        mockNotification,
        { ...mockNotification, id: 2 },
        { ...mockNotification, id: 3 },
      ];

      const action = setNotifications(notifications);
      const state = notificationReducer(initialState, action);

      expect(state.notifications).toEqual(notifications);
    });

    it('should handle empty array', () => {
      const action = setNotifications([]);
      const state = notificationReducer(initialState, action);

      expect(state.notifications).toEqual([]);
    });
  });

  describe('markAsRead', () => {
    it('should mark a notification as read and decrement unread count', () => {
      const stateWithNotification = {
        ...initialState,
        notifications: [mockNotification],
        unreadCount: 1,
      };

      const action = markAsRead(1);
      const state = notificationReducer(stateWithNotification, action);

      expect(state.notifications[0].est_lue).toBe(true);
      expect(state.unreadCount).toBe(0);
    });

    it('should not change unread count if notification is already read', () => {
      const readNotification = { ...mockNotification, est_lue: true };
      const stateWithReadNotification = {
        ...initialState,
        notifications: [readNotification],
        unreadCount: 0,
      };

      const action = markAsRead(1);
      const state = notificationReducer(stateWithReadNotification, action);

      expect(state.notifications[0].est_lue).toBe(true);
      expect(state.unreadCount).toBe(0);
    });

    it('should not affect other notifications', () => {
      const notifications = [
        mockNotification,
        { ...mockNotification, id: 2, est_lue: true },
        { ...mockNotification, id: 3 },
      ];

      const stateWithNotifications = {
        ...initialState,
        notifications,
        unreadCount: 2,
      };

      const action = markAsRead(3);
      const state = notificationReducer(stateWithNotifications, action);

      expect(state.notifications[0].est_lue).toBe(false); // Notification 1
      expect(state.notifications[1].est_lue).toBe(true);  // Notification 2
      expect(state.notifications[2].est_lue).toBe(true);  // Notification 3
      expect(state.unreadCount).toBe(1);
    });

    it('should handle non-existent notification ID', () => {
      const stateWithNotification = {
        ...initialState,
        notifications: [mockNotification],
        unreadCount: 1,
      };

      const action = markAsRead(999);
      const state = notificationReducer(stateWithNotification, action);

      expect(state.notifications[0].est_lue).toBe(false);
      expect(state.unreadCount).toBe(1);
    });
  });

  describe('markAllAsRead', () => {
    it('should mark all notifications as read and set unread count to 0', () => {
      const notifications = [
        mockNotification,
        { ...mockNotification, id: 2 },
        { ...mockNotification, id: 3, est_lue: true },
      ];

      const stateWithNotifications = {
        ...initialState,
        notifications,
        unreadCount: 2,
      };

      const action = markAllAsRead();
      const state = notificationReducer(stateWithNotifications, action);

      expect(state.notifications.every(n => n.est_lue)).toBe(true);
      expect(state.unreadCount).toBe(0);
    });

    it('should handle empty notifications array', () => {
      const action = markAllAsRead();
      const state = notificationReducer(initialState, action);

      expect(state.notifications).toEqual([]);
      expect(state.unreadCount).toBe(0);
    });

    it('should handle notifications that are already all read', () => {
      const readNotifications = [
        { ...mockNotification, est_lue: true },
        { ...mockNotification, id: 2, est_lue: true },
      ];

      const stateWithReadNotifications = {
        ...initialState,
        notifications: readNotifications,
        unreadCount: 0,
      };

      const action = markAllAsRead();
      const state = notificationReducer(stateWithReadNotifications, action);

      expect(state.notifications.every(n => n.est_lue)).toBe(true);
      expect(state.unreadCount).toBe(0);
    });
  });

  describe('setUnreadCount', () => {
    it('should set unread count to specified value', () => {
      const action = setUnreadCount(5);
      const state = notificationReducer(initialState, action);

      expect(state.unreadCount).toBe(5);
    });

    it('should handle zero count', () => {
      const action = setUnreadCount(0);
      const state = notificationReducer(initialState, action);

      expect(state.unreadCount).toBe(0);
    });

    it('should handle negative count (though not recommended)', () => {
      const action = setUnreadCount(-1);
      const state = notificationReducer(initialState, action);

      expect(state.unreadCount).toBe(-1);
    });
  });

  describe('setLoading', () => {
    it('should set loading state', () => {
      const action = setLoading(true);
      const state = notificationReducer(initialState, action);

      expect(state.loading).toBe(true);
    });

    it('should set loading to false', () => {
      const loadingState = { ...initialState, loading: true };
      const action = setLoading(false);
      const state = notificationReducer(loadingState, action);

      expect(state.loading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should set error message', () => {
      const errorMessage = 'Test error';
      const action = setError(errorMessage);
      const state = notificationReducer(initialState, action);

      expect(state.error).toBe(errorMessage);
    });

    it('should clear error when set to null', () => {
      const errorState = { ...initialState, error: 'Previous error' };
      const action = setError(null);
      const state = notificationReducer(errorState, action);

      expect(state.error).toBeNull();
    });
  });

  describe('clearNotifications', () => {
    it('should clear all notifications and reset state', () => {
      const stateWithData = {
        notifications: [mockNotification],
        unreadCount: 1,
        loading: false,
        error: 'Some error',
      };

      const action = clearNotifications();
      const state = notificationReducer(stateWithData, action);

      expect(state.notifications).toEqual([]);
      expect(state.unreadCount).toBe(0);
      expect(state.error).toBeNull();
    });

    it('should not affect loading state', () => {
      const loadingState = {
        ...initialState,
        loading: true,
      };

      const action = clearNotifications();
      const state = notificationReducer(loadingState, action);

      expect(state.loading).toBe(true);
    });
  });

  describe('combined actions', () => {
    it('should handle multiple actions in sequence', () => {
      let state = notificationReducer(initialState, setLoading(true));
      
      const notification1 = { ...mockNotification, id: 1 };
      state = notificationReducer(state, addNotification(notification1));
      
      const notification2 = { ...mockNotification, id: 2 };
      state = notificationReducer(state, addNotification(notification2));
      
      state = notificationReducer(state, markAsRead(1));
      state = notificationReducer(state, setLoading(false));
      state = notificationReducer(state, setError(null));

      expect(state.notifications).toHaveLength(2);
      expect(state.notifications[0].est_lue).toBe(false); // First notification (id: 2) is unread
      expect(state.notifications[1].est_lue).toBe(true); // Second notification (id: 1) is read
      expect(state.unreadCount).toBe(1);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle setting notifications and then marking as read', () => {
      const notifications = [
        mockNotification,
        { ...mockNotification, id: 2 },
        { ...mockNotification, id: 3 },
      ];

      let state = notificationReducer(initialState, setNotifications(notifications));
      expect(state.unreadCount).toBe(0); // setNotifications doesn't update unreadCount

      // Manually set unread count
      state = notificationReducer(state, setUnreadCount(3));
      expect(state.unreadCount).toBe(3);

      // Mark one as read
      state = notificationReducer(state, markAsRead(1));
      expect(state.unreadCount).toBe(2);
      expect(state.notifications[0].est_lue).toBe(true);
    });
  });
});