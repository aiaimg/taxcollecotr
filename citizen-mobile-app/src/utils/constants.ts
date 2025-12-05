// Storage Keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  PREFERRED_LANGUAGE: 'preferred_language',
  BIOMETRIC_ENABLED: 'biometric_enabled',
  CACHED_VEHICLES: 'cached_vehicles',
  CACHED_PAYMENTS: 'cached_payments',
};

// API Configuration
export const API_CONFIG = {
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

// Validation Patterns
export const VALIDATION_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE_MG: /^\+261\d{9}$/,
  PASSWORD_MIN_LENGTH: 8,
};

// Date Formats
export const DATE_FORMATS = {
  DISPLAY: 'DD/MM/YYYY',
  API: 'YYYY-MM-DD',
  DATETIME: 'DD/MM/YYYY HH:mm',
};

// Payment Configuration
export const PAYMENT_CONFIG = {
  MVOLA_FEE_PERCENTAGE: 0.03, // 3%
  POLLING_INTERVAL: 3000, // 3 seconds
  MAX_POLLING_ATTEMPTS: 60, // 3 minutes max
};

// Image Configuration
export const IMAGE_CONFIG = {
  MAX_SIZE_MB: 1,
  MAX_SIZE_BYTES: 1024 * 1024, // 1MB
  QUALITY: 0.8,
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
};

// API Base URL
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
