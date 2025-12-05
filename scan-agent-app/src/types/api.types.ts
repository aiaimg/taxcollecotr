export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface VerificationRequest {
  qr_data: string;
  agent_type: string;
  agent_id: string;
  location?: {
    latitude: number;
    longitude: number;
  };
}

export interface VerificationResponse {
  valid: boolean;
  vehicle_info?: {
    plate_number: string;
    owner_name: string;
    vehicle_type: string;
    brand: string;
    model: string;
    year: number;
    tax_status: 'paid' | 'pending' | 'expired';
    insurance_status: 'valid' | 'expired' | 'none';
    last_tax_payment?: string;
    amount_due?: number;
  };
  payment_status?: {
    status: 'paid' | 'pending' | 'failed' | 'expired';
    amount?: number;
    method?: string;
    transaction_id?: string;
    paid_at?: string;
    expires_at?: string;
  };
  warnings?: string[];
  message?: string;
}

export interface PaymentRequest {
  amount: number;
  method: 'cash' | 'mvola' | 'card';
  vehicle_plate?: string;
  agent_id: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  notes?: string;
}

export interface PaymentResponse {
  success: boolean;
  transaction_id: string;
  receipt_number: string;
  amount: number;
  method: string;
  processed_at: string;
  commission_earned?: number;
  vehicle_plate?: string;
}

export interface AgentProfileResponse {
  id: string;
  badge_id: string;
  name: string;
  type: string;
  region: string;
  is_active: boolean;
  email?: string;
  phone?: string;
  created_at: string;
  last_login?: string;
  permissions: string[];
  statistics?: {
    total_scans?: number;
    total_payments?: number;
    total_commissions?: number;
    today_scans?: number;
    today_payments?: number;
  };
}

export interface ScanHistoryResponse {
  scans: Array<{
    id: string;
    type: string;
    data: string;
    timestamp: string;
    location?: {
      latitude: number;
      longitude: number;
    };
    validated: boolean;
    validation_status: string;
    vehicle_info?: any;
    payment_status?: any;
    notes?: string;
  }>;
  total: number;
  page: number;
  limit: number;
}

export interface CommissionResponse {
  total_commissions: number;
  today_commissions: number;
  this_month_commissions: number;
  commission_rate: number;
  transactions: Array<{
    id: string;
    amount: number;
    commission: number;
    date: string;
    vehicle_plate?: string;
    payment_method: string;
  }>;
}

export interface CashSessionResponse {
  session_id: string;
  agent_id: string;
  start_time: string;
  end_time?: string;
  opening_balance: number;
  closing_balance?: number;
  total_transactions: number;
  total_amount: number;
  status: 'active' | 'closed';
}