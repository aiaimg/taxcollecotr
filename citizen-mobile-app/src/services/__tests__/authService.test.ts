import authService from '../authService';
import storageService from '../storageService';
import apiClient from '../../api/client';
import { API_ENDPOINTS } from '../../api/endpoints';
import { LoginCredentials, RegisterData, AuthResponse } from '../../types/models';

// Mock dependencies
jest.mock('../../api/client');
jest.mock('../storageService');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockedStorageService = storageService as jest.Mocked<typeof storageService>;

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should login successfully and store tokens', async () => {
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

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });
      mockedStorageService.secureSet.mockResolvedValue();

      const result = await authService.login(credentials);

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        API_ENDPOINTS.AUTH.LOGIN,
        credentials
      );
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
      expect(result).toEqual(mockResponse);
    });

    it('should throw error on login failure', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'WrongPassword',
      };

      const mockError = new Error('Invalid credentials');
      mockedApiClient.post.mockRejectedValueOnce(mockError);

      await expect(authService.login(credentials)).rejects.toThrow('Invalid credentials');
    });
  });

  describe('register', () => {
    it('should register successfully and store tokens', async () => {
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

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });
      mockedStorageService.secureSet.mockResolvedValue();

      const result = await authService.register(registerData);

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        API_ENDPOINTS.AUTH.REGISTER,
        registerData
      );
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'access_token',
        mockResponse.access
      );
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'refresh_token',
        mockResponse.refresh
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw error on registration failure', async () => {
      const registerData: RegisterData = {
        user_type: 'PARTICULIER',
        first_name: 'New',
        last_name: 'User',
        email: 'existing@example.com',
        phone: '+261340000001',
        password: 'Password123!',
        password_confirm: 'Password123!',
        preferred_language: 'fr',
      };

      const mockError = new Error('Email already exists');
      mockedApiClient.post.mockRejectedValueOnce(mockError);

      await expect(authService.register(registerData)).rejects.toThrow(
        'Email already exists'
      );
    });
  });

  describe('logout', () => {
    it('should logout successfully and clear tokens', async () => {
      mockedStorageService.secureGet.mockResolvedValueOnce('mock-refresh-token');
      mockedApiClient.post.mockResolvedValueOnce({ data: {} });
      mockedStorageService.secureDelete.mockResolvedValue();

      await authService.logout();

      expect(mockedApiClient.post).toHaveBeenCalledWith(API_ENDPOINTS.AUTH.LOGOUT, {
        refresh: 'mock-refresh-token',
      });
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('access_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('refresh_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('user_data');
    });

    it('should clear tokens even if API call fails', async () => {
      mockedStorageService.secureGet.mockResolvedValueOnce('mock-refresh-token');
      mockedApiClient.post.mockRejectedValueOnce(new Error('Network error'));
      mockedStorageService.secureDelete.mockResolvedValue();

      await authService.logout();

      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('access_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('refresh_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('user_data');
    });
  });

  describe('refreshToken', () => {
    it('should refresh token successfully', async () => {
      const newAccessToken = 'new-access-token';
      mockedStorageService.secureGet.mockResolvedValueOnce('mock-refresh-token');
      mockedApiClient.post.mockResolvedValueOnce({ data: { access: newAccessToken } });
      mockedStorageService.secureSet.mockResolvedValue();

      const result = await authService.refreshToken();

      expect(mockedStorageService.secureGet).toHaveBeenCalledWith('refresh_token');
      expect(mockedApiClient.post).toHaveBeenCalledWith(API_ENDPOINTS.AUTH.REFRESH, {
        refresh: 'mock-refresh-token',
      });
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'access_token',
        newAccessToken
      );
      expect(result).toBe(newAccessToken);
    });

    it('should throw error if no refresh token available', async () => {
      mockedStorageService.secureGet.mockResolvedValueOnce(null);

      await expect(authService.refreshToken()).rejects.toThrow(
        'No refresh token available'
      );
    });

    it('should clear tokens if refresh fails', async () => {
      mockedStorageService.secureGet.mockResolvedValueOnce('mock-refresh-token');
      mockedApiClient.post.mockRejectedValueOnce(new Error('Invalid refresh token'));
      mockedStorageService.secureDelete.mockResolvedValue();

      await expect(authService.refreshToken()).rejects.toThrow('Invalid refresh token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('access_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('refresh_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('user_data');
    });
  });

  describe('getStoredTokens', () => {
    it('should return stored tokens', async () => {
      mockedStorageService.secureGet
        .mockResolvedValueOnce('mock-access-token')
        .mockResolvedValueOnce('mock-refresh-token');

      const result = await authService.getStoredTokens();

      expect(result).toEqual({
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
      });
    });

    it('should return null if tokens not found', async () => {
      mockedStorageService.secureGet.mockResolvedValue(null);

      const result = await authService.getStoredTokens();

      expect(result).toBeNull();
    });
  });

  describe('storeTokens', () => {
    it('should store tokens securely', async () => {
      const tokens = {
        access: 'test-access-token',
        refresh: 'test-refresh-token',
      };

      mockedStorageService.secureSet.mockResolvedValue();

      await authService.storeTokens(tokens);

      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'access_token',
        tokens.access
      );
      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'refresh_token',
        tokens.refresh
      );
    });
  });

  describe('clearTokens', () => {
    it('should clear all tokens and user data', async () => {
      mockedStorageService.secureDelete.mockResolvedValue();

      await authService.clearTokens();

      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('access_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('refresh_token');
      expect(mockedStorageService.secureDelete).toHaveBeenCalledWith('user_data');
    });
  });

  describe('isAuthenticated', () => {
    it('should return true if tokens exist', async () => {
      mockedStorageService.secureGet
        .mockResolvedValueOnce('mock-access-token')
        .mockResolvedValueOnce('mock-refresh-token');

      const result = await authService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('should return false if tokens do not exist', async () => {
      mockedStorageService.secureGet.mockResolvedValue(null);

      const result = await authService.isAuthenticated();

      expect(result).toBe(false);
    });
  });

  describe('biometric preferences', () => {
    it('should store biometric enabled preference', async () => {
      mockedStorageService.secureSet.mockResolvedValue();

      await authService.storeBiometricEnabled(true);

      expect(mockedStorageService.secureSet).toHaveBeenCalledWith(
        'biometric_enabled',
        'true'
      );
    });

    it('should get biometric enabled preference', async () => {
      mockedStorageService.secureGet.mockResolvedValueOnce('true');

      const result = await authService.getBiometricEnabled();

      expect(result).toBe(true);
    });

    it('should return false if biometric preference not set', async () => {
      mockedStorageService.secureGet.mockResolvedValueOnce(null);

      const result = await authService.getBiometricEnabled();

      expect(result).toBe(false);
    });
  });
});
