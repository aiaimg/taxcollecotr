import { AgentType } from '../types/auth.types';
import { SCANNER_CONFIG } from '../constants/scanner.constants';

export const validateBadgeId = (badgeId: string): boolean => {
  // Badge ID should be alphanumeric and between 6-12 characters
  const badgeIdRegex = /^[A-Z0-9]{6,12}$/i;
  return badgeIdRegex.test(badgeId);
};

export const validatePin = (pin: string): boolean => {
  // PIN should be 4-6 digits
  const pinRegex = /^\d{4,6}$/;
  return pinRegex.test(pin);
};

export const validateLicensePlate = (plate: string): boolean => {
  // Check against known license plate patterns
  const patterns = SCANNER_CONFIG.LICENSE_PLATE.PATTERNS;
  return patterns.some(pattern => pattern.test(plate.toUpperCase()));
};

export const validateQRCodeData = (data: string): boolean => {
  // Basic QR code validation - should be non-empty and reasonable length
  if (!data || data.length < 10 || data.length > 1000) {
    return false;
  }
  
  // Check if it's a valid JSON or has expected format
  try {
    JSON.parse(data);
    return true;
  } catch {
    // If not JSON, check for common QR code patterns
    return data.includes('http') || data.includes('taxcollector') || data.includes('government');
  }
};

export const validateBarcodeData = (data: string): boolean => {
  // Barcode should be numeric or alphanumeric
  if (!data || data.length < 5 || data.length > 50) {
    return false;
  }
  
  // Check for valid characters
  const validChars = /^[A-Z0-9\-\s]+$/i;
  return validChars.test(data);
};

export const validateAmount = (amount: number): boolean => {
  // Amount should be positive and reasonable
  return amount > 0 && amount < 1000000 && Number.isFinite(amount);
};

export const validatePaymentMethod = (method: string): boolean => {
  const validMethods = ['cash', 'mvola', 'card'];
  return validMethods.includes(method.toLowerCase());
};

export const validateAgentPermissions = (
  agentType: AgentType | null,
  requiredPermission: string
): boolean => {
  if (!agentType) {
    return false;
  }
  
  const permissions = AgentType.GOVERNMENT === agentType 
    ? ['scan_qr', 'verify_code', 'view_history', 'view_statistics', 'scan_barcode', 'scan_license_plate']
    : ['process_payment', 'generate_receipt', 'manage_cash_session', 'view_commissions', 'view_payment_history'];
  
  return permissions.includes(requiredPermission);
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhoneNumber = (phone: string): boolean => {
  // Malagasy phone number format: +261 XX XX XXX XX or 03X XX XXX XX
  const phoneRegex = /^(\+261|0)[32]\d{8}$/;
  return phoneRegex.test(phone.replace(/\s/g, ''));
};

export const validateCoordinates = (lat: number, lng: number): boolean => {
  // Basic coordinate validation for Madagascar
  const validLat = lat >= -25.6 && lat <= -11.9; // Madagascar latitude range
  const validLng = lng >= 43.2 && lng <= 50.5;   // Madagascar longitude range
  return validLat && validLng;
};

export const validateOffenseDetails = (details: string): boolean => {
  if (!details) return false;
  const normalized = details.trim();
  return normalized.length >= 5 && normalized.length <= 2000;
};

export const validateEvidenceUri = (uri: string): boolean => {
  if (!uri) return true; // optional
  const urlRegex = /^(https?:\/\/|file:\/\/|content:\/\/).+/i;
  return urlRegex.test(uri);
};
