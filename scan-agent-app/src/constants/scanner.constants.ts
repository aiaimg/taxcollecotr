export const SCANNER_CONFIG = {
  QR_CODE: {
    SUPPORTED_FORMATS: ['qr', 'pdf417'],
    GOVERNMENT_FORMATS: ['qr'],
    TIMEOUT: 10000, // 10 seconds
  },
  BARCODE: {
    SUPPORTED_FORMATS: ['code128', 'code39', 'ean13', 'ean8', 'upc_a', 'upc_e'],
    TIMEOUT: 8000, // 8 seconds
  },
  LICENSE_PLATE: {
    PATTERNS: [
      /^[A-Z]{2}\d{4}[A-Z]{2}$/, // Format: XX1234XX
      /^\d{4}[A-Z]{2}\d{2}$/,     // Format: 1234XX12
      /^[A-Z]\d{3}[A-Z]{2}$/,     // Format: X123XX
    ],
    MIN_CONFIDENCE: 0.8,
    TIMEOUT: 15000, // 15 seconds
  },
} as const;

export const SCAN_VALIDATION_MESSAGES = {
  SUCCESS: 'Scan réussi et validé',
  INVALID_FORMAT: 'Format de code invalide',
  EXPIRED: 'Le code a expiré',
  NOT_FOUND: 'Code introuvable dans la base de données',
  NETWORK_ERROR: "Impossible de valider en raison d'une erreur réseau",
  PERMISSION_DENIED: "Vous n'avez pas l'autorisation de scanner ce type de code",
  OFFLINE_VALIDATION: 'Validation effectuée hors ligne - peut ne pas être à jour',
} as const;

export const SCANNER_PERMISSIONS = {
  CAMERA: 'camera',
  LOCATION: 'location',
  STORAGE: 'storage',
} as const;

export const SCANNER_SETTINGS = {
  AUTO_FOCUS: true,
  FLASH_MODE: 'auto' as const,
  ZOOM: 0,
  WHITE_BALANCE: 'auto' as const,
  QUALITY: 1, // Highest quality
  BASE64: false,
};