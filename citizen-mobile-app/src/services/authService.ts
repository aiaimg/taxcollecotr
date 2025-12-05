import apiClient from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  AuthTokens,
  User,
} from '../types/models';
import storageService, { StorageService } from './storageService';

/**
 * AuthService - Handles authentication operations
 * Manages JWT tokens, login, register, logout, and token refresh
 */
class AuthService {
  // Storage keys from StorageService
  private readonly ACCESS_TOKEN_KEY = StorageService.KEYS.ACCESS_TOKEN;
  private readonly REFRESH_TOKEN_KEY = StorageService.KEYS.REFRESH_TOKEN;
  private readonly USER_KEY = StorageService.KEYS.USER_DATA;

  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>(
        API_ENDPOINTS.AUTH.LOGIN,
        {
          email: credentials.email,
          password: credentials.password,
        }
      );

      const { access, refresh, user } = response.data;

      // Store tokens securely
      await this.storeTokens({ access, refresh });

      // Store user data
      if (user) {
        await storageService.secureSet(this.USER_KEY, JSON.stringify(user));
      }

      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Register new user
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>(
        API_ENDPOINTS.AUTH.REGISTER,
        {
          user_type: data.user_type,
          first_name: data.first_name,
          last_name: data.last_name,
          email: data.email,
          phone: data.phone,
          password: data.password,
          password_confirm: data.password_confirm,
          preferred_language: data.preferred_language,
        }
      );

      const { access, refresh, user } = response.data;

      // Store tokens securely
      await this.storeTokens({ access, refresh });

      // Store user data
      if (user) {
        await storageService.secureSet(this.USER_KEY, JSON.stringify(user));
      }

      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      // Call logout endpoint to invalidate token on server
      const refreshToken = await storageService.secureGet(this.REFRESH_TOKEN_KEY);
      
      if (refreshToken) {
        await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, {
          refresh: refreshToken,
        });
      }
    } catch (error) {
      console.error('Logout API error:', error);
      // Continue with local cleanup even if API call fails
    } finally {
      // Clear all stored data
      await this.clearTokens();
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(): Promise<string> {
    try {
      const refreshToken = await storageService.secureGet(this.REFRESH_TOKEN_KEY);

      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post<{ access: string }>(
        API_ENDPOINTS.AUTH.REFRESH,
        {
          refresh: refreshToken,
        }
      );

      const { access } = response.data;

      // Store new access token
      await storageService.secureSet(this.ACCESS_TOKEN_KEY, access);

      return access;
    } catch (error) {
      console.error('Token refresh error:', error);
      // Clear tokens if refresh fails
      await this.clearTokens();
      throw error;
    }
  }

  /**
   * Get stored tokens
   */
  async getStoredTokens(): Promise<AuthTokens | null> {
    try {
      const access = await storageService.secureGet(this.ACCESS_TOKEN_KEY);
      const refresh = await storageService.secureGet(this.REFRESH_TOKEN_KEY);

      if (access && refresh) {
        return { access, refresh };
      }

      return null;
    } catch (error) {
      console.error('Error getting stored tokens:', error);
      return null;
    }
  }

  /**
   * Store tokens securely
   */
  async storeTokens(tokens: AuthTokens): Promise<void> {
    try {
      await storageService.secureSet(this.ACCESS_TOKEN_KEY, tokens.access);
      await storageService.secureSet(this.REFRESH_TOKEN_KEY, tokens.refresh);
    } catch (error) {
      console.error('Error storing tokens:', error);
      throw error;
    }
  }

  /**
   * Clear all tokens and user data
   */
  async clearTokens(): Promise<void> {
    try {
      await storageService.secureDelete(this.ACCESS_TOKEN_KEY);
      await storageService.secureDelete(this.REFRESH_TOKEN_KEY);
      await storageService.secureDelete(this.USER_KEY);
    } catch (error) {
      console.error('Error clearing tokens:', error);
      throw error;
    }
  }

  /**
   * Get stored user data
   */
  async getStoredUser(): Promise<User | null> {
    try {
      const userData = await storageService.secureGet(this.USER_KEY);
      if (userData) {
        return JSON.parse(userData) as User;
      }
      return null;
    } catch (error) {
      console.error('Error getting stored user:', error);
      return null;
    }
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    const tokens = await this.getStoredTokens();
    return tokens !== null;
  }

  /**
   * Store preferred language
   */
  async storeLanguage(language: 'fr' | 'mg'): Promise<void> {
    try {
      await storageService.secureSet(StorageService.KEYS.PREFERRED_LANGUAGE, language);
    } catch (error) {
      console.error('Error storing language:', error);
      throw error;
    }
  }

  /**
   * Get stored language
   */
  async getStoredLanguage(): Promise<'fr' | 'mg' | null> {
    try {
      const language = await storageService.secureGet(StorageService.KEYS.PREFERRED_LANGUAGE);
      return language as 'fr' | 'mg' | null;
    } catch (error) {
      console.error('Error getting stored language:', error);
      return null;
    }
  }

  /**
   * Store biometric enabled preference
   */
  async storeBiometricEnabled(enabled: boolean): Promise<void> {
    try {
      await storageService.secureSet(
        StorageService.KEYS.BIOMETRIC_ENABLED,
        enabled ? 'true' : 'false'
      );
    } catch (error) {
      console.error('Error storing biometric preference:', error);
      throw error;
    }
  }

  /**
   * Get biometric enabled preference
   */
  async getBiometricEnabled(): Promise<boolean> {
    try {
      const enabled = await storageService.secureGet(StorageService.KEYS.BIOMETRIC_ENABLED);
      return enabled === 'true';
    } catch (error) {
      console.error('Error getting biometric preference:', error);
      return false;
    }
  }
}

// Export singleton instance
export default new AuthService();
