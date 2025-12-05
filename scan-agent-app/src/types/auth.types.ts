export enum AgentType {
  GOVERNMENT = 'agent_government',
  PARTENAIRE = 'agent_partenaire'
}

export interface Agent {
  id: string;
  badgeId: string;
  type: AgentType;
  name: string;
  permissions: string[];
  region: string;
  department?: string;
  isActive: boolean;
  email?: string;
  phone?: string;
  createdAt: Date;
  lastLogin?: Date;
}

export interface LoginCredentials {
  badgeId?: string;
  pin?: string;
  email?: string;
  password?: string;
}

export interface AuthResponse {
  success: boolean;
  agent?: Agent;
  token?: string;
  refreshToken?: string;
  error?: string;
}

export const AgentPermissions = {
  [AgentType.GOVERNMENT]: [
    'scan_qr',
    'verify_code', 
    'view_history',
    'view_statistics',
    'scan_barcode',
    'scan_license_plate',
    'view_contraventions',
    'issue_contravention',
    'process_contraventions',
    'void_contravention'
  ],
  [AgentType.PARTENAIRE]: [
    'process_payment',
    'generate_receipt',
    'manage_cash_session',
    'view_commissions',
    'view_payment_history'
  ]
} as const;

export type Permission = typeof AgentPermissions[AgentType][number];
