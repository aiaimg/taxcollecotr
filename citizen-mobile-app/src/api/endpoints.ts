// API Endpoints Configuration
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/v1/auth/login/',
    REGISTER: '/api/v1/auth/register/',
    LOGOUT: '/api/v1/auth/logout/',
    REFRESH: '/api/v1/auth/refresh/',
    VERIFY_EMAIL: '/api/v1/auth/verify-email/',
    PASSWORD_RESET: '/api/v1/auth/password-reset/',
    PASSWORD_RESET_CONFIRM: '/api/v1/auth/password-reset-confirm/',
  },

  // Vehicles
  VEHICLES: {
    LIST: '/api/v1/vehicles/',
    CREATE: '/api/v1/vehicles/',
    DETAIL: (plaque: string) => `/api/v1/vehicles/${plaque}/`,
    UPDATE: (plaque: string) => `/api/v1/vehicles/${plaque}/`,
    DELETE: (plaque: string) => `/api/v1/vehicles/${plaque}/`,
    TAX_INFO: (plaque: string) => `/api/v1/vehicles/${plaque}/tax_info/`,
  },

  // Vehicle Types
  VEHICLE_TYPES: {
    LIST: '/api/v1/vehicle-types/',
  },

  // Tax Calculations
  TAX_CALCULATIONS: {
    CALCULATE: '/api/v1/tax-calculations/calculate/',
  },

  // Payments
  PAYMENTS: {
    LIST: '/api/v1/payments/',
    INITIATE: '/api/v1/payments/initiate/',
    DETAIL: (id: number) => `/api/v1/payments/${id}/`,
    RECEIPT: (id: number) => `/api/v1/payments/${id}/receipt/`,
  },

  // QR Codes
  QR_CODES: {
    VERIFY: '/api/v1/qr-codes/verify/',
  },

  // Notifications
  NOTIFICATIONS: {
    LIST: '/api/v1/notifications/',
    REGISTER_DEVICE: '/api/v1/notifications/register-device/',
    MARK_READ: (id: number) => `/api/v1/notifications/${id}/mark_read/`,
    MARK_ALL_READ: '/api/v1/notifications/mark_all_read/',
    UNREAD_COUNT: '/api/v1/notifications/unread_count/',
  },

  // User Profile
  USERS: {
    ME: '/api/v1/users/me/',
    PROFILE: '/api/v1/profiles/me/',
  },
};

export default API_ENDPOINTS;
