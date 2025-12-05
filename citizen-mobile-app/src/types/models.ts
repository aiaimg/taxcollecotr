// User Types
export type UserType = 'PARTICULIER' | 'ENTREPRISE';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  user_type: UserType;
  is_verified: boolean;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

// Authentication Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  user_type: UserType;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  password: string;
  password_confirm: string;
  preferred_language: 'fr' | 'mg';
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
  message?: string;
}

// Vehicle Types
export type SourceEnergie = 'ESSENCE' | 'DIESEL' | 'ELECTRIQUE' | 'HYBRIDE';
export type CategorieVehicule = 'PERSONNEL' | 'COMMERCIAL';
export type TaxStatus = 'PAYE' | 'IMPAYE' | 'EXPIRE' | 'EXONERE';

export interface VehicleType {
  id: number;
  nom: string;
  description: string;
}

export interface Vehicle {
  id: number;
  plaque_immatriculation: string;
  marque: string;
  modele: string;
  couleur: string;
  vin?: string;
  type_vehicule: VehicleType;
  puissance_fiscale_cv: number;
  cylindree_cm3: number;
  source_energie: SourceEnergie;
  date_premiere_circulation: string;
  categorie_vehicule: CategorieVehicule;
  photo_url?: string;
  tax_status: TaxStatus;
  tax_amount?: number;
  tax_due_date?: string;
  sans_plaque?: boolean;
}

export interface VehicleFormData {
  plaque_immatriculation?: string;
  sans_plaque: boolean;
  marque: string;
  modele: string;
  couleur: string;
  vin?: string;
  type_vehicule_id: number;
  puissance_fiscale_cv: number;
  cylindree_cm3: number;
  source_energie: string;
  date_premiere_circulation: string;
  categorie_vehicule: string;
  documents?: VehicleDocument[];
}

export interface VehicleDocument {
  type: 'carte_grise' | 'carte_grise_verso' | 'assurance' | 'controle_technique';
  uri: string;
  name: string;
}

export interface TaxInfo {
  montant_du_ariary: number;
  annee_fiscale: number;
  est_exonere: boolean;
  date_limite?: string;
  grille_tarifaire?: PriceGrid;
  details?: {
    exemption_reason?: string;
    error?: string;
  };
}

export interface PriceGrid {
  id: number;
  annee_fiscale: number;
  puissance_min_cv: number;
  puissance_max_cv: number;
  tarif_ariary: number;
}

// Payment Types
export type PaymentMethod = 'MVOLA' | 'STRIPE' | 'CASH';
export type PaymentStatus = 'EN_ATTENTE' | 'PAYE' | 'ECHOUE' | 'ANNULE';

export interface Payment {
  id: number;
  vehicule_plaque: string;
  montant_paye_ariary: number;
  annee_fiscale: number;
  date_paiement: string;
  methode_paiement: PaymentMethod;
  statut: PaymentStatus;
  transaction_id?: string;
  qr_code?: QRCode;
}

export interface QRCode {
  token: string;
  qr_code_url: string;
  date_generation: string;
  date_expiration: string;
}

// Notification Types
export type NotificationType =
  | 'RAPPEL_PAIEMENT'
  | 'CONFIRMATION_PAIEMENT'
  | 'EXPIRATION'
  | 'ALERTE';

export interface Notification {
  id: number;
  titre: string;
  contenu: string;
  type: NotificationType;
  est_lue: boolean;
  date_creation: string;
  data?: Record<string, unknown>;
}

// Profile Types
export interface UserProfile {
  user: User;
  profile_picture?: string;
  preferred_language: 'fr' | 'mg';
  notifications_enabled: boolean;
  biometric_enabled: boolean;
}
