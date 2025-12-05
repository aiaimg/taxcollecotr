import authReducer, {
  setCredentials,
  setAccessToken,
  setUser,
  setLoading,
  setError,
  clearError,
  setBiometricEnabled,
  logout,
  restoreSession,
  AuthState,
} from '../authSlice';
import { User, AuthTokens } from '../../../types/models';

describe('authSlice', () => {
  const initialState: AuthState = {
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    biometricEnabled: false,
  };

  const mockUser: User = {
    id: 1,
    email: 'test@example.com',
    first_name: 'Test',
    last_name: 'User',
    phone: '+261340000000',
    user_type: 'PARTICULIER',
    is_verified: true,
  };

  const mockTokens: AuthTokens = {
    access: 'mock-access-token',
    refresh: 'mock-refresh-token',
  };

  describe('setCredentials', () => {
    it('should set user and tokens and mark as authenticated', () => {
      const state = authReducer(
        initialState,
        setCredentials({ user: mockUser, tokens: mockTokens })
      );

      expect(state.user).toEqual(mockUser);
      expect(state.tokens).toEqual(mockTokens);
      expect(state.isAuthenticated).toBe(true);
      expect(state.error).toBeNull();
    });
  });

  describe('setAccessToken', () => {
    it('should update access token', () => {
      const stateWithTokens: AuthState = {
        ...initialState,
        tokens: mockTokens,
      };

      const newAccessToken = 'new-access-token';
      const state = authReducer(stateWithTokens, setAccessToken(newAccessToken));

      expect(state.tokens?.access).toBe(newAccessToken);
      expect(state.tokens?.refresh).toBe(mockTokens.refresh);
    });

    it('should not update if tokens are null', () => {
      const state = authReducer(initialState, setAccessToken('new-token'));

      expect(state.tokens).toBeNull();
    });
  });

  describe('setUser', () => {
    it('should update user data', () => {
      const updatedUser: User = {
        ...mockUser,
        first_name: 'Updated',
      };

      const state = authReducer(initialState, setUser(updatedUser));

      expect(state.user).toEqual(updatedUser);
    });
  });

  describe('setLoading', () => {
    it('should set loading state to true', () => {
      const state = authReducer(initialState, setLoading(true));

      expect(state.isLoading).toBe(true);
    });

    it('should set loading state to false', () => {
      const loadingState: AuthState = {
        ...initialState,
        isLoading: true,
      };

      const state = authReducer(loadingState, setLoading(false));

      expect(state.isLoading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should set error message and stop loading', () => {
      const loadingState: AuthState = {
        ...initialState,
        isLoading: true,
      };

      const errorMessage = 'Authentication failed';
      const state = authReducer(loadingState, setError(errorMessage));

      expect(state.error).toBe(errorMessage);
      expect(state.isLoading).toBe(false);
    });
  });

  describe('clearError', () => {
    it('should clear error message', () => {
      const errorState: AuthState = {
        ...initialState,
        error: 'Some error',
      };

      const state = authReducer(errorState, clearError());

      expect(state.error).toBeNull();
    });
  });

  describe('setBiometricEnabled', () => {
    it('should enable biometric authentication', () => {
      const state = authReducer(initialState, setBiometricEnabled(true));

      expect(state.biometricEnabled).toBe(true);
    });

    it('should disable biometric authentication', () => {
      const biometricState: AuthState = {
        ...initialState,
        biometricEnabled: true,
      };

      const state = authReducer(biometricState, setBiometricEnabled(false));

      expect(state.biometricEnabled).toBe(false);
    });
  });

  describe('logout', () => {
    it('should reset state to initial values', () => {
      const authenticatedState: AuthState = {
        user: mockUser,
        tokens: mockTokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        biometricEnabled: true,
      };

      const state = authReducer(authenticatedState, logout());

      expect(state).toEqual(initialState);
    });
  });

  describe('restoreSession', () => {
    it('should restore user and tokens from persisted state', () => {
      const state = authReducer(
        initialState,
        restoreSession({ user: mockUser, tokens: mockTokens })
      );

      expect(state.user).toEqual(mockUser);
      expect(state.tokens).toEqual(mockTokens);
      expect(state.isAuthenticated).toBe(true);
    });
  });

  describe('complex scenarios', () => {
    it('should handle login flow', () => {
      let state = initialState;

      // Start loading
      state = authReducer(state, setLoading(true));
      expect(state.isLoading).toBe(true);

      // Set credentials on success
      state = authReducer(state, setCredentials({ user: mockUser, tokens: mockTokens }));
      expect(state.isAuthenticated).toBe(true);
      expect(state.user).toEqual(mockUser);
      expect(state.tokens).toEqual(mockTokens);
      expect(state.error).toBeNull();

      // Stop loading
      state = authReducer(state, setLoading(false));
      expect(state.isLoading).toBe(false);
    });

    it('should handle login error flow', () => {
      let state = initialState;

      // Start loading
      state = authReducer(state, setLoading(true));
      expect(state.isLoading).toBe(true);

      // Set error on failure
      state = authReducer(state, setError('Invalid credentials'));
      expect(state.error).toBe('Invalid credentials');
      expect(state.isLoading).toBe(false);
      expect(state.isAuthenticated).toBe(false);
    });

    it('should handle token refresh flow', () => {
      let state: AuthState = {
        ...initialState,
        user: mockUser,
        tokens: mockTokens,
        isAuthenticated: true,
      };

      // Update access token
      const newAccessToken = 'refreshed-access-token';
      state = authReducer(state, setAccessToken(newAccessToken));

      expect(state.tokens?.access).toBe(newAccessToken);
      expect(state.tokens?.refresh).toBe(mockTokens.refresh);
      expect(state.isAuthenticated).toBe(true);
    });

    it('should handle logout after authentication', () => {
      let state: AuthState = {
        user: mockUser,
        tokens: mockTokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        biometricEnabled: true,
      };

      state = authReducer(state, logout());

      expect(state).toEqual(initialState);
    });
  });
});
