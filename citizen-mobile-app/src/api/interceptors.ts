import { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import storageService, { StorageService } from '../services/storageService';

/**
 * Request interceptor to add authentication token and language headers
 */
export const authRequestInterceptor = async (
  config: InternalAxiosRequestConfig
): Promise<InternalAxiosRequestConfig> => {
  try {
    // Add auth token if available
    const token = await storageService.secureGet(StorageService.KEYS.ACCESS_TOKEN);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add language header
    const language = await storageService.secureGet(StorageService.KEYS.PREFERRED_LANGUAGE);
    if (language && config.headers) {
      config.headers['Accept-Language'] = language;
    }

    // Log request in debug mode
    if (__DEV__) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
      if (config.data) {
        console.log('[API Request Data]', config.data);
      }
    }
  } catch (error) {
    console.error('Error in auth request interceptor:', error);
  }

  return config;
};

/**
 * Request error interceptor
 */
export const requestErrorInterceptor = (error: AxiosError): Promise<AxiosError> => {
  console.error('Request interceptor error:', error);
  return Promise.reject(error);
};

/**
 * Response success interceptor
 */
export const responseSuccessInterceptor = (response: AxiosResponse): AxiosResponse => {
  // Log response in debug mode
  if (__DEV__) {
    console.log(
      `[API Response] ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`
    );
    if (response.data) {
      console.log('[API Response Data]', response.data);
    }
  }

  return response;
};

/**
 * Response error interceptor
 */
export const responseErrorInterceptor = (error: AxiosError): Promise<AxiosError> => {
  // Log error in debug mode
  if (__DEV__) {
    console.error(
      `[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status}`
    );
  }

  // Handle different error types
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const data = error.response.data as any;

    switch (status) {
      case 400:
        console.error('Bad Request:', data);
        break;
      case 401:
        console.error('Unauthorized:', data);
        // Token refresh is handled in the main client
        break;
      case 403:
        console.error('Forbidden:', data);
        break;
      case 404:
        console.error('Not Found:', data);
        break;
      case 500:
        console.error('Server Error:', data);
        break;
      default:
        console.error('API Error:', status, data);
    }
  } else if (error.request) {
    // Request made but no response received
    console.error('Network Error: No response received');
  } else {
    // Error setting up request
    console.error('Request Error:', error.message);
  }

  return Promise.reject(error);
};

/**
 * Format API error for display
 */
export const formatAPIError = (error: any): string => {
  if (error.response) {
    const data = error.response.data;
    
    // Handle validation errors
    if (data && typeof data === 'object') {
      if (data.detail) {
        return data.detail;
      }
      
      // Handle field-specific errors
      const fieldErrors = Object.entries(data)
        .filter(([key]) => key !== 'detail')
        .map(([key, value]) => {
          if (Array.isArray(value)) {
            return `${key}: ${value.join(', ')}`;
          }
          return `${key}: ${value}`;
        });
      
      if (fieldErrors.length > 0) {
        return fieldErrors.join('\n');
      }
    }
    
    return `Error: ${error.response.status} - ${error.response.statusText}`;
  } else if (error.request) {
    return 'Network error: Unable to connect to server';
  } else {
    return error.message || 'An unexpected error occurred';
  }
};

/**
 * Check if error is a network error
 */
export const isNetworkError = (error: any): boolean => {
  return !error.response && error.request;
};

/**
 * Check if error is an authentication error
 */
export const isAuthError = (error: any): boolean => {
  return error.response && (error.response.status === 401 || error.response.status === 403);
};

/**
 * Check if error is a validation error
 */
export const isValidationError = (error: any): boolean => {
  return error.response && error.response.status === 400;
};
