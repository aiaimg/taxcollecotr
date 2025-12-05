import { store } from '../store/store';
import { setAccessToken, logout } from '../store/slices/authSlice';
import storageService, { StorageService } from './storageService';
import apiClient from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';

/**
 * Token Refresh Service
 * Handles automatic token refresh when access token expires
 */
class TokenRefreshService {
  private refreshPromise: Promise<string> | null = null;
  private isRefreshing = false;

  /**
   * Refresh the access token using the refresh token
   * Implements a singleton pattern to prevent multiple simultaneous refresh requests
   */
  async refreshAccessToken(): Promise<string> {
    // If already refreshing, return the existing promise
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise;
    }

    // Set refreshing flag and create new promise
    this.isRefreshing = true;
    this.refreshPromise = this.performRefresh();

    try {
      const newAccessToken = await this.refreshPromise;
      return newAccessToken;
    } finally {
      // Reset flags after refresh completes
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }

  /**
   * Perform the actual token refresh
   */
  private async performRefresh(): Promise<string> {
    try {
      // Get refresh token from secure storage
      const refreshToken = await storageService.secureGet(
        StorageService.KEYS.REFRESH_TOKEN
      );

      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      console.log('Refreshing access token...');

      // Call refresh endpoint
      const response = await apiClient.post<{ access: string }>(
        API_ENDPOINTS.AUTH.REFRESH,
        {
          refresh: refreshToken,
        }
      );

      const { access } = response.data;

      // Store new access token
      await storageService.secureSet(StorageService.KEYS.ACCESS_TOKEN, access);

      // Update Redux state
      store.dispatch(setAccessToken(access));

      console.log('Access token refreshed successfully');

      return access;
    } catch (error) {
      console.error('Token refresh failed:', error);

      // Clear tokens and logout on refresh failure
      await this.handleRefreshFailure();

      throw error;
    }
  }

  /**
   * Handle refresh failure by logging out the user
   */
  private async handleRefreshFailure(): Promise<void> {
    console.log('Handling refresh failure - logging out user');

    // Clear all stored tokens
    await storageService.secureDelete(StorageService.KEYS.ACCESS_TOKEN);
    await storageService.secureDelete(StorageService.KEYS.REFRESH_TOKEN);
    await storageService.secureDelete(StorageService.KEYS.USER_DATA);

    // Dispatch logout action
    store.dispatch(logout());
  }

  /**
   * Check if token is expired or about to expire
   * @param token JWT token
   * @param bufferSeconds Number of seconds before expiry to consider token expired (default: 60)
   */
  isTokenExpired(token: string, bufferSeconds: number = 60): boolean {
    try {
      // Decode JWT token (without verification)
      const payload = this.decodeJWT(token);

      if (!payload || !payload.exp) {
        return true;
      }

      // Get current time in seconds
      const currentTime = Math.floor(Date.now() / 1000);

      // Check if token is expired or will expire within buffer time
      return payload.exp - currentTime < bufferSeconds;
    } catch (error) {
      console.error('Error checking token expiration:', error);
      return true;
    }
  }

  /**
   * Decode JWT token payload
   * Note: This does NOT verify the token signature
   */
  private decodeJWT(token: string): { exp?: number } | null {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        return null;
      }

      // Decode base64 payload
      const payload = parts[1];
      const decoded = atob(payload);
      return JSON.parse(decoded);
    } catch (error) {
      console.error('Error decoding JWT:', error);
      return null;
    }
  }

  /**
   * Get valid access token (refresh if needed)
   */
  async getValidAccessToken(): Promise<string | null> {
    try {
      // Get current access token
      const accessToken = await storageService.secureGet(
        StorageService.KEYS.ACCESS_TOKEN
      );

      if (!accessToken) {
        return null;
      }

      // Check if token is expired or about to expire
      if (this.isTokenExpired(accessToken)) {
        console.log('Access token expired, refreshing...');
        return await this.refreshAccessToken();
      }

      return accessToken;
    } catch (error) {
      console.error('Error getting valid access token:', error);
      return null;
    }
  }
}

// Export singleton instance
export default new TokenRefreshService();
