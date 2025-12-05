export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/refresh/',
  },
  GOVERNMENT_AGENT: {
    VERIFY_QR: '/agent-government/verify_qr_code/',
    SCAN_HISTORY: '/agent-government/my_verifications/',
    STATISTICS: '/agent-government/statistics/',
    PROFILE: '/agent-government/profile/',
    VEHICLE_INFO: '/agent-government/vehicle_info/',
    CONTRAVENTIONS_LIST: '/agent-government/contraventions/',
    CONTRAVENTIONS_DETAIL: (id: string) => `/agent-government/contraventions/${id}/`,
    CONTRAVENTIONS_CREATE: '/agent-government/contraventions/create/',
    CONTRAVENTIONS_UPDATE: (id: string) => `/agent-government/contraventions/${id}/update/`,
    CONTRAVENTIONS_VOID: (id: string) => `/agent-government/contraventions/${id}/void/`,
    EVIDENCE_UPLOAD: (id: string) => `/agent-government/contraventions/${id}/evidence/`,
    OFFENDER_VERIFY: '/agent-government/offender/verify/',
  },
  PARTNER_AGENT: {
    PROCESS_PAYMENT: '/agent-partenaire/process_payment/',
    MY_SESSIONS: '/agent-partenaire/my_sessions/',
    PROFILE: '/agent-partenaire/profile/',
    GENERATE_RECEIPT: '/agent-partenaire/generate_receipt/',
    COMMISSIONS: '/agent-partenaire/commissions/',
    CLOSE_SESSION: '/agent-partenaire/close_session/',
  },
} as const;

export const API_TIMEOUT = 30000; // 30 seconds

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const;

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network connection error. Please check your internet connection.',
  TIMEOUT_ERROR: 'Request timeout. Please try again.',
  UNAUTHORIZED: 'Authentication required. Please login again.',
  FORBIDDEN: 'Access denied. You do not have permission to perform this action.',
  SERVER_ERROR: 'Server error. Please try again later.',
  INVALID_RESPONSE: 'Invalid response from server.',
  OFFLINE_MODE: 'You are currently offline. Some features may be limited.',
} as const;
