export const APP_CONFIG = {
  NAME: 'TaxCollector Agent',
  VERSION: '1.0.0',
  BUILD_NUMBER: '1',
  ENVIRONMENT: process.env.NODE_ENV || 'development',
  DEBUG: process.env.NODE_ENV === 'development',
} as const;

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'taxcollector.auth_token',
  REFRESH_TOKEN: 'taxcollector.refresh_token',
  AGENT_PROFILE: 'taxcollector.agent_profile',
  SCAN_HISTORY: 'taxcollector.scan_history',
  PAYMENT_HISTORY: 'taxcollector.payment_history',
  OFFLINE_QUEUE: 'taxcollector.offline_queue',
  APP_SETTINGS: 'taxcollector.app_settings',
  LAST_SYNC: 'taxcollector.last_sync',
} as const;

export const OFFLINE_CONFIG = {
  MAX_QUEUE_SIZE: 100,
  SYNC_INTERVAL: 300000, // 5 minutes
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 5000, // 5 seconds
  CACHE_EXPIRY: 86400000, // 24 hours
} as const;

export const NETWORK_CONFIG = {
  TIMEOUT: 30000, // 30 seconds
  RETRY_COUNT: 3,
  BACKOFF_MULTIPLIER: 2,
  MAX_RETRY_DELAY: 30000, // 30 seconds
} as const;

export const DATE_FORMATS = {
  DISPLAY: 'DD/MM/YYYY HH:mm',
  API: 'YYYY-MM-DDTHH:mm:ssZ',
  DATE_ONLY: 'DD/MM/YYYY',
  TIME_ONLY: 'HH:mm',
} as const;