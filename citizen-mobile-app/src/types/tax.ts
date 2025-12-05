// Tax Calculation Types
import { PaymentMethod } from './models';

export interface TaxCalculationRequest {
  vehicle_plaque: string;
  fiscal_year: number;
}

export interface TaxCalculationResponse {
  vehicle_plaque: string;
  fiscal_year: number;
  base_amount_ariary: number;
  platform_fee_ariary: number;
  total_amount_ariary: number;
  platform_fee_percentage: number;
  tax_breakdown: TaxBreakdown;
  applicable_discounts: Discount[];
  final_amount_ariary: number;
  due_date: string;
  is_exempt: boolean;
  exemption_reason?: string;
}

export interface TaxBreakdown {
  vehicle_type: string;
  fiscal_power_cv: number;
  base_rate_ariary: number;
  age_factor: number;
  energy_factor: number;
  category_factor: number;
  calculated_base_ariary: number;
}

export interface Discount {
  type: 'EARLY_PAYMENT' | 'MULTI_VEHICLE' | 'SENIOR' | 'DISABLED';
  name: string;
  amount_ariary: number;
  percentage: number;
  description: string;
}

export interface TaxCalculation {
  id: string;
  vehicle_plaque: string;
  fiscal_year: number;
  base_amount_ariary: number;
  platform_fee_ariary: number;
  total_amount_ariary: number;
  final_amount_ariary: number;
  due_date: string;
  is_exempt: boolean;
  exemption_reason?: string;
  calculated_at: string;
  expires_at: string;
}

export interface PaymentInitiationRequest {
  vehicle_plaque: string;
  fiscal_year: number;
  amount_ariary: number;
  payment_method: PaymentMethod;
  phone_number?: string;
  return_url?: string;
}

export interface PaymentInitiationResponse {
  payment_id: number;
  transaction_id: string;
  amount_ariary: number;
  payment_method: PaymentMethod;
  status: 'PENDING' | 'INITIATED';
  next_action?: {
    type: 'REDIRECT' | 'POLLING' | 'WAITING';
    url?: string;
    polling_interval?: number;
    instructions?: string;
  };
  expires_at: string;
}

export interface PaymentStatusResponse {
  payment_id: number;
  transaction_id: string;
  status: 'PENDING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  amount_ariary: number;
  payment_method: PaymentMethod;
  paid_at?: string;
  failure_reason?: string;
  receipt_url?: string;
  qr_code?: {
    token: string;
    qr_code_url: string;
    expires_at: string;
  };
}

export interface PaymentReceipt {
  payment_id: number;
  transaction_id: string;
  vehicle_plaque: string;
  fiscal_year: number;
  amount_paid_ariary: number;
  payment_method: PaymentMethod;
  paid_at: string;
  qr_code_url: string;
  receipt_url: string;
  vehicle_details: {
    marque: string;
    modele: string;
    puissance_fiscale_cv: number;
  };
  tax_breakdown: TaxBreakdown;
}