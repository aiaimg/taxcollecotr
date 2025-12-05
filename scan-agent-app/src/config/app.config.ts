export const APP_CONFIG = {
  name: 'Scan Agent',
  version: '1.0.0',
  environment: process.env.NODE_ENV || 'development',
  apiUrl: process.env.API_URL || 'https://api.taxcollection.gov.mg',
  timeout: 30000,
  retryAttempts: 3,
};

export const SCANNER_CONFIG = {
  qrCode: {
    enabled: true,
    formats: ['qr'],
  },
  barcode: {
    enabled: true,
    formats: ['code128', 'code39', 'ean13', 'ean8'],
  },
  licensePlate: {
    enabled: true,
    pattern: /^[A-Z]{2,3}\d{3,4}[A-Z]{0,2}$/,
  },
};

export const OFFLINE_CONFIG = {
  maxQueueSize: 100,
  syncInterval: 300000, // 5 minutes
  retryInterval: 60000, // 1 minute
};

export const PERMISSIONS = {
  camera: 'camera',
  location: 'location',
  storage: 'storage',
};

export const DATE_FORMATS = {
  display: 'DD/MM/YYYY HH:mm',
  api: 'YYYY-MM-DDTHH:mm:ssZ',
  short: 'DD/MM/YYYY',
};