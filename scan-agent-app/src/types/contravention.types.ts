export enum ContraventionStatus {
  DRAFT = 'draft',
  ISSUED = 'issued',
  PAID = 'paid',
  DISPUTED = 'disputed',
  VOIDED = 'voided',
}

export type EvidenceType = 'photo' | 'video' | 'document';

export interface Evidence {
  id: string;
  type: EvidenceType;
  uri: string;
  hash?: string;
  size?: number;
  metadata?: Record<string, any>;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  address?: string;
}

export interface Contravention {
  id: string;
  offenderId: string;
  offenseDetails: string;
  location: LocationData;
  timestamp: string;
  status: ContraventionStatus;
  evidence: Evidence[];
  createdBy: string; // agent id
  department?: string;
  notes?: string;
}

export interface ContraventionListParams {
  search?: string;
  status?: ContraventionStatus;
  offenderId?: string;
  department?: string;
  fromDate?: string;
  toDate?: string;
  page?: number;
  pageSize?: number;
}

export interface ContraventionCreatePayload {
  offenderId: string;
  offenseDetails: string;
  location: LocationData;
  timestamp: string;
  evidence?: Evidence[];
  department?: string;
  notes?: string;
}
