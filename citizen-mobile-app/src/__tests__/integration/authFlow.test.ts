import { configureStore } from '@reduxjs/toolkit';
import authReducer, { setCredentials, logout } from '../../store/slices/authSlice';
import { authApi } from '../../store/api/authApi';
import authService from '../../services/authService';
import storageService from '../../services/storageService';
import apiClient from '../../api/client';
import { LoginCredentials, RegisterData, AuthResponse } from '../../types/models';

// Mock dependencies
jest.mock('../../api/client');
jest.mock('../../services/storageService');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockedStorageService = storageService as jest.Mocked<typeof storageService>;

describe('Authentication Flow Integration Tests', () => {
  let store: ReturnType<typeof configureStore>;

  beforeEach(() => {
    // Create a fresh store for each test
    store = configureStore({
      reducer: {
        auth: authReducer,
        [authApi.reducerPath]: authApi.reducer,
      },
      middleware: getDefaultMiddleware =>
        getDefaultMiddleware().concat(authApi.middleware),
    });

    jest.clearAllMocks();
  });

  describe('Login Flow', () => {
    it('should complete full login flow successfully', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'Password123!',
      };

      const mockResponse: AuthResponse = {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: {
          id: 1,
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User',
          phone: '+261340000000',
          user_type: 'PARTICULIER',
          is_verified: true,
        },
      };

      // Mock API response
      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });
      mockedStorageService.secureSet.mockResolvedValue();

      // Execute login
      const result = await authService.login(credentials);

      // Verify API was called correctly
      expect(mockedApiClient.post).toHaveBeenCalledWith(
        '/api/v1/auth/login/',
        credentials
      );

      // Verify tokens were stored
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'access_token',
        mockResponse.access
      );
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'refresh_token',
        mockResponse.refresh
      );
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'user_data',
        JSON.stringify(mockResponse.user)
      );

      // Verify response
      expect(result).toEqual(mockResponse);

      // Simulate Redux state update
      store.dispatch(
        setCredentials({
          user: mockResponse.user,
          tokens: {
            access: mockResponse.access,
            refresh: mockResponse.refresh,
          },
        })
      );

      // Verify Redux state
      const state = store.getState() as any;
      expect(state.auth.isAuthenticated).toBe(true);
      expect(state.auth.user).toEqual(mockResponse.user);
      expect(state.auth.tokens).toEqual({
        access: mockResponse.access,
        refresh: mockResponse.refresh,
      });
    });

    it('should handle login failure correctly', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'WrongPassword',
      };

      const mockError = {
        response: {
          status: 401,
          data: { detail: 'Invalid credentials' },
        },
      };

      mockedApiClient.post.mockRejectedValueOnce(mockError);

      // Execute login and expect failure
      await expect(authService.login(credentials)).rejects.toEqual(mockError);

      // Verify tokens were not stored
      expect(mockedStorageService.secureSet).not.toHaveBeenCalled();

      // Verify Redux state remains unauthenticated
      const state = store.getState() as any;
      expect(state.auth.isAuthenticated).toBe(false);
      expect(state.auth.user).toBeNull();
    });
  });

  describe('Register Flow', () => {
    it('should complete full registration flow successfully', async () => {
      const registerData: RegisterData = {
        user_type: 'PARTICULIER',
        first_name: 'New',
        last_name: 'User',
        email: 'newuser@example.com',
        phone: '+261340000001',
        password: 'Password123!',
        password_confirm: 'Password123!',
        preferred_language: 'fr',
      };

      const mockResponse: AuthResponse = {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: {
          id: 2,
          email: 'newuser@example.com',
          first_name: 'New',
          last_name: 'User',
          phone: '+261340000001',
          user_type: 'PARTICULIER',
          is_verified: false,
        },
      };

      // Mock API response
      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });
      mockedStorageService.secureSet.mockResolvedValue();

      // Execute registration
      const result = await authService.register(registerData);

      // Verify API was called correctly
      expect(mockedApiClient.post).toHaveBeenCalledWith(
        '/api/v1/auth/register/',
        registerData
      );

      // Verify tokens were stored
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'access_token',
        mockResponse.access
      );
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'refresh_token',
        mockResponse.refresh
      );

      // Verify response
      expect(result).toEqual(mockResponse);

      // Simulate Redux state update
      store.dispatch(
        setCredentials({
          user: mockResponse.user,
          tokens: {
            access: mockResponse.access,
            refresh: mockResponse.refresh,
          },
        })
      );

      // Verify Redux state
      const state = store.getState() as any;
      expect(state.auth.isAuthenticated).toBe(true);
      expect(state.auth.user).toEqual(mockResponse.user);
    });

    it('should handle registration validation errors', async () => {
      const registerData: RegisterData = {
        user_type: 'PARTICULIER',
        first_name: 'New',
        last_name: 'User',
        email: 'invalid-email',
        phone: 'invalid-phone',
        password: 'weak',
        password_confirm: 'weak',
        preferred_language: 'fr',
      };

      const mockError = {
        response: {
          status: 400,
          data: {
            email: ['Enter a valid email address.'],
            phone: ['Invalid phone number format.'],
            password: ['Password is too weak.'],
          },
        },
      };

      mockedApiClient.post.mockRejectedValueOnce(mockError);

      // Execute registration and expect failure
      await expect(authService.register(registerData)).rejects.toEqual(mockError);

      // Verify tokens were not stored
      expect(mockedStorageService.secureSet).not.toHaveBeenCalled();
    });
  });

  describe('Logout Flow', () => {
    it('should complete full logout flow successfully', async () => {
      // Setup authenticated state
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        phone: '+261340000000',
        user_type: 'PARTICULIER' as const,
        is_verified: true,
      };

      store.dispatch(
        setCredentials({
          user: mockUser,
          tokens: {
            access: 'mock-access-token',
            refresh: 'mock-refresh-token',
          },
        })
      );

      // Verify authenticated
      let state = store.getState() as any;
      expect(state.auth.isAuthenticated).toBe(true);

      // Mock logout
      mockedStorageService.secureGet.mockResolvedValueOnce('mock-refresh-token');
      mockedApiClient.post.mockResolvedValueOnce({ data: {} });
      mockedStorageService.secureDelete.mockResolvedValue();

      // Execute logout
      await authService.logout();

      // Verify API was called
      expect(mockedApiClient.post).toHaveBeenCalledWith('/api/v1/auth/logout/', {
        refresh: 'mock-refresh-token',
      });

      // Verify tokens were cleared
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('access_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('refresh_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('user_data');

      // Simulate Redux state update
      store.dispatch(logout());

      // Verify Redux state
      state = store.getState() as any;
      expect(state.auth.isAuthenticated).toBe(false);
      expect(state.auth.user).toBeNull();
      expect(state.auth.tokens).toBeNull();
    });
  });

  describe('Token Refresh Flow', () => {
    it('should refresh access token successfully', async () => {
      // Setup authenticated state with expired access token
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        phone: '+261340000000',
        user_type: 'PARTICULIER' as const,
        is_verified: true,
      };

      store.dispatch(
        setCredentials({
          user: mockUser,
          tokens: {
            access: 'expired-access-token',
            refresh: 'valid-refresh-token',
          },
        })
      );

      // Mock token refresh
      const newAccessToken = 'new-access-token';
      mockedStorageService.secureGet.mockResolvedValueOnce('valid-refresh-token');
      mockedApiClient.post.mockResolvedValueOnce({ data: { access: newAccessToken } });
      mockedStorageService.secureSet.mockResolvedValue();

      // Execute token refresh
      const result = await authService.refreshToken();

      // Verify API was called
      expect(mockedApiClient.post).toHaveBeenCalledWith('/api/v1/auth/refresh/', {
        refresh: 'valid-refresh-token',
      });

      // Verify new token was stored
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'access_token',
        newAccessToken
      );

      // Verify result
      expect(result).toBe(newAccessToken);
    });

    it('should logout if token refresh fails', async () => {
      // Mock failed refresh
      mockedStorageService.secureGet.mockResolvedValueOnce('invalid-refresh-token');
      mockedApiClient.post.mockRejectedValueOnce(new Error('Invalid refresh token'));
      mockedStorageService.secureDelete.mockResolvedValue();

      // Execute token refresh and expect failure
      await expect(authService.refreshToken()).rejects.toThrow('Invalid refresh token');

      // Verify tokens were cleared
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('access_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('refresh_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('user_data');
    });
  });

  describe('Session Persistence', () => {
    it('should restore session from stored tokens', async () => {
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        phone: '+261340000000',
        user_type: 'PARTICULIER' as const,
        is_verified: true,
      };

      // Mock stored tokens
      mockedStorageService.secureGet
        .mockResolvedValueOnce('stored-access-token')
        .mockResolvedValueOnce('stored-refresh-token');

      // Get stored tokens
      const tokens = await authService.getStoredTokens();

      expect(tokens).toEqual({
        access: 'stored-access-token',
        refresh: 'stored-refresh-token',
      });

      // Verify authentication status
      const isAuthenticated = await authService.isAuthenticated();
      expect(isAuthenticated).toBe(true);
    });

    it('should not restore session if no tokens stored', async () => {
      mockedStorageService.secureGet.mockResolvedValue(null);

      const tokens = await authService.getStoredTokens();
      expect(tokens).toBeNull();

      const isAuthenticated = await authService.isAuthenticated();
      expect(isAuthenticated).toBe(false);
    });
  });
});
