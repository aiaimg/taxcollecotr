export type ScanType = 'qr' | 'barcode' | 'license_plate';

export interface Location {
  latitude: number;
  longitude: number;
  accuracy?: number;
  timestamp?: Date;
}

export interface VehicleInfo {
  plateNumber: string;
  ownerName: string;
  vehicleType: string;
  brand: string;
  model: string;
  year: number;
  taxStatus: 'paid' | 'pending' | 'expired';
  insuranceStatus: 'valid' | 'expired' | 'none';
  lastTaxPayment?: Date;
  amountDue?: number;
}

export interface PaymentStatus {
  status: 'paid' | 'pending' | 'failed' | 'expired';
  amount?: number;
  method?: 'cash' | 'mvola' | 'card';
  transactionId?: string;
  paidAt?: Date;
  expiresAt?: Date;
}

export interface QRCodeResult {
  type: 'qr';
  data: string;
  format: string;
  isValid: boolean;
  validationMessage?: string;
}

export interface BarcodeResult {
  type: 'barcode';
  data: string;
  format: string;
  isValid: boolean;
  validationMessage?: string;
}

export interface LicensePlateResult {
  type: 'license_plate';
  plateNumber: string;
  confidence: number;
  isValid: boolean;
  vehicleInfo?: VehicleInfo;
  validationMessage?: string;
}

export type ScanResult = QRCodeResult | BarcodeResult | LicensePlateResult;

export interface ScanRecord {
  id: string;
  type: ScanType;
  data: string;
  timestamp: Date;
  location?: Location;
  agentId: string;
  agentType: string;
  validated: boolean;
  validationStatus: 'valid' | 'invalid' | 'expired' | 'pending';
  vehicleInfo?: VehicleInfo;
  paymentStatus?: PaymentStatus;
  notes?: string;
  images?: string[];
  synced: boolean;
  syncError?: string;
}

export interface ValidationResult {
  valid: boolean;
  reason?: string;
  vehicleInfo?: VehicleInfo;
  paymentStatus?: PaymentStatus;
  warnings?: string[];
}