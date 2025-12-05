import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { API_BASE_URL, API_TIMEOUT, ERROR_MESSAGES, API_ENDPOINTS } from '../constants/api.constants';
import { t } from '../utils/translations';
import { storageService } from './storageService';

interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

class APIService {
  private client: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value?: any) => void;
    reject: (error?: any) => void;
  }> = [];

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        // Add auth token if available
        const token = await storageService.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add device info
        config.headers['X-Device-Type'] = 'mobile';
        config.headers['X-App-Version'] = '1.0.0';

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // If already refreshing, queue this request
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const newToken = await this.refreshTokenRequest();
            if (newToken) {
              await storageService.setAuthToken(newToken);
              
              // Process failed queue
              this.failedQueue.forEach(({ resolve }) => {
                resolve();
              });
              this.failedQueue = [];

              // Retry original request
              return this.client(originalRequest);
            } else {
              // Refresh failed, logout
              await this.logoutRequest();
              throw new Error('Authentication failed');
            }
          } catch (refreshError) {
            this.failedQueue.forEach(({ reject }) => {
              reject(refreshError);
            });
            this.failedQueue = [];
            throw refreshError;
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: AxiosError): Error {
    if (error.code === 'ECONNABORTED') {
      return new Error(ERROR_MESSAGES.TIMEOUT_ERROR);
    }

    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as any;

      switch (status) {
        case 400:
          return new Error(data.error || 'Bad request');
        case 401:
          return new Error(ERROR_MESSAGES.UNAUTHORIZED);
        case 403:
          return new Error(ERROR_MESSAGES.FORBIDDEN);
        case 404:
          return new Error('Resource not found');
        case 500:
          return new Error(ERROR_MESSAGES.SERVER_ERROR);
        default:
          return new Error(data.error || ERROR_MESSAGES.SERVER_ERROR);
      }
    } else if (error.request) {
      return new Error(ERROR_MESSAGES.NETWORK_ERROR);
    } else {
      return new Error('Request setup error');
    }
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await this.client.get(url, config);
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : t('api.requestFailed'),
        timestamp: new Date().toISOString(),
      };
    }
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await this.client.post(url, data, config);
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : t('api.requestFailed'),
        timestamp: new Date().toISOString(),
      };
    }
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await this.client.put(url, data, config);
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Request failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await this.client.delete(url, config);
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Request failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Utility methods
  async isOnline(): Promise<boolean> {
    try {
      const response = await this.get('/health/');
      return response.success;
    } catch {
      return false;
    }
  }

  setBaseURL(url: string): void {
    this.client.defaults.baseURL = url;
  }

  setTimeout(timeout: number): void {
    this.client.defaults.timeout = timeout;
  }

  addHeader(key: string, value: string): void {
    this.client.defaults.headers.common[key] = value;
  }

  removeHeader(key: string): void {
    delete this.client.defaults.headers.common[key];
  }

  // Internal helpers to avoid circular dependency with authService
  private async refreshTokenRequest(): Promise<string | null> {
    try {
      const response = await this.client.post(API_ENDPOINTS.AUTH.REFRESH, {});
      const token = (response.data as any)?.access;
      return token || null;
    } catch (e) {
      return null;
    }
  }

  private async logoutRequest(): Promise<void> {
    try {
      await this.client.post(API_ENDPOINTS.AUTH.LOGOUT, {});
    } catch (e) {
      // Ignore server logout errors
    }
    await storageService.clearAuthData();
  }
}

export const apiService = new APIService();
