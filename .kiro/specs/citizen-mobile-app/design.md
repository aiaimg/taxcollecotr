# Design Document - Tax Collector Citizen Mobile App

## Overview

L'application mobile Tax Collector Citizen App est une application native cross-platform développée avec React Native (Expo) pour iOS et Android. Elle permet aux citoyens et entreprises de Madagascar de gérer leurs véhicules, calculer et payer leurs taxes annuelles, et consulter leur historique de paiements via une interface mobile intuitive et performante.

### Objectifs Principaux

- Fournir une expérience mobile native fluide et performante
- Permettre l'enregistrement et la gestion de véhicules
- Faciliter le calcul et le paiement des taxes annuelles
- Offrir un accès hors ligne aux données essentielles
- Supporter le multilingue (Français/Malagasy)
- Intégrer les paiements mobiles (MVola) et cartes bancaires (Stripe)
- Fournir un système de notifications push pour les rappels

### Technologies Utilisées

- **Framework**: React Native avec Expo (SDK 50+)
- **Langage**: TypeScript
- **Navigation**: React Navigation 6.x
- **State Management**: Redux Toolkit + RTK Query
- **API Client**: Axios avec intercepteurs
- **Authentification**: JWT avec stockage sécurisé (Expo SecureStore)
- **Paiements**: Stripe React Native SDK + MVola API
- **Notifications**: Expo Notifications
- **QR Code Display**: React Native QR Code SVG
- **Stockage Local**: AsyncStorage + Expo SecureStore
- **Images**: Expo Image Picker + Image Manipulator
- **Internationalisation**: i18next + react-i18next
- **Biométrie**: Expo Local Authentication
- **Offline**: Redux Persist + Network Info

## Architecture

### Architecture Globale


```
┌─────────────────────────────────────────────────────────────┐
│                    Mobile Application                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Presentation Layer                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Screens   │  │ Components │  │ Navigation │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Business Logic Layer                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │   Redux    │  │  RTK Query │  │  Services  │     │   │
│  │  │   Store    │  │    API     │  │  (Utils)   │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Data Layer                               │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │ SecureStore│  │AsyncStorage│  │   Cache    │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTPS/REST API
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (Django)                      │
│  /api/v1/auth, /api/v1/vehicles, /api/v1/payments, etc.    │
└─────────────────────────────────────────────────────────────┘
```

### Structure des Dossiers

**Note**: L'application citoyenne Tax Collector n'existe pas encore dans le projet. Elle sera créée dans un nouveau dossier `citizen-mobile-app/` (à ne pas confondre avec `scan-agent-app/` qui est l'application des agents de contrôle pour les contraventions).

```
citizen-mobile-app/          # NOUVEAU PROJET À CRÉER
├── src/
│   ├── api/                    # API client et configuration
│   │   ├── client.ts          # Axios instance configurée
│   │   ├── endpoints.ts       # Définition des endpoints
│   │   └── interceptors.ts    # Auth et error interceptors
│   ├── components/            # Composants réutilisables
│   │   ├── common/           # Boutons, inputs, cards, etc.
│   │   ├── vehicle/          # Composants liés aux véhicules
│   │   ├── payment/          # Composants de paiement
│   │   └── navigation/       # Navigation components
│   ├── screens/              # Écrans de l'application
│   │   ├── auth/            # Login, Register, ForgotPassword
│   │   ├── dashboard/       # Dashboard principal
│   │   ├── vehicles/        # Liste, détails, ajout véhicules
│   │   ├── payments/        # Paiement, historique
│   │   ├── profile/         # Profil utilisateur
│   │   └── settings/        # Paramètres
│   ├── navigation/           # Configuration navigation
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   └── MainNavigator.tsx
│   ├── store/               # Redux store
│   │   ├── slices/         # Redux slices
│   │   │   ├── authSlice.ts
│   │   │   ├── vehicleSlice.ts
│   │   │   ├── paymentSlice.ts
│   │   │   └── settingsSlice.ts
│   │   ├── api/            # RTK Query API
│   │   │   ├── authApi.ts
│   │   │   ├── vehicleApi.ts
│   │   │   ├── paymentApi.ts
│   │   │   └── notificationApi.ts
│   │   └── store.ts        # Store configuration
│   ├── services/            # Services métier
│   │   ├── authService.ts
│   │   ├── storageService.ts
│   │   ├── notificationService.ts
│   │   ├── biometricService.ts
│   │   └── offlineService.ts
│   ├── utils/              # Utilitaires
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   ├── constants.ts
│   │   └── helpers.ts
│   ├── i18n/               # Internationalisation
│   │   ├── index.ts
│   │   ├── fr.json
│   │   └── mg.json
│   ├── types/              # Types TypeScript
│   │   ├── api.ts
│   │   ├── models.ts
│   │   └── navigation.ts
│   └── theme/              # Thème et styles
│       ├── colors.ts
│       ├── typography.ts
│       └── spacing.ts
├── assets/                 # Assets statiques
│   ├── images/
│   ├── icons/
│   └── fonts/
├── App.tsx                # Point d'entrée
├── app.json              # Configuration Expo
└── package.json
```

## Components and Interfaces

### 1. Authentification

#### AuthService

Service gérant l'authentification et la gestion des tokens JWT.


**Interfaces:**

```typescript
interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  user_type: 'PARTICULIER' | 'ENTREPRISE';
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  password: string;
  password_confirm: string;
  preferred_language: 'fr' | 'mg';
}

interface AuthTokens {
  access: string;
  refresh: string;
}

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  user_type: string;
  is_verified: boolean;
}
```

**Méthodes:**

- `login(credentials: LoginCredentials): Promise<AuthResponse>`
- `register(data: RegisterData): Promise<AuthResponse>`
- `logout(): Promise<void>`
- `refreshToken(): Promise<string>`
- `getStoredTokens(): Promise<AuthTokens | null>`
- `storeTokens(tokens: AuthTokens): Promise<void>`
- `clearTokens(): Promise<void>`

#### BiometricService

Service pour l'authentification biométrique (Touch ID/Face ID).

**Méthodes:**

- `isAvailable(): Promise<boolean>`
- `authenticate(): Promise<boolean>`
- `enableBiometric(): Promise<void>`
- `disableBiometric(): Promise<void>`
- `isBiometricEnabled(): Promise<boolean>`

### 2. Gestion des Véhicules

#### VehicleService

Service pour la gestion des véhicules.

**Interfaces:**

```typescript
interface Vehicle {
  id: number;
  plaque_immatriculation: string;
  marque: string;
  modele: string;
  couleur: string;
  vin?: string;
  type_vehicule: VehicleType;
  puissance_fiscale_cv: number;
  cylindree_cm3: number;
  source_energie: 'ESSENCE' | 'DIESEL' | 'ELECTRIQUE' | 'HYBRIDE';
  date_premiere_circulation: string;
  categorie_vehicule: 'PERSONNEL' | 'COMMERCIAL';
  photo_url?: string;
  tax_status: 'PAYE' | 'IMPAYE' | 'EXPIRE' | 'EXONERE';
  tax_amount?: number;
  tax_due_date?: string;
}

interface VehicleType {
  id: number;
  nom: string;
  description: string;
}

interface VehicleFormData {
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

interface VehicleDocument {
  type: 'carte_grise' | 'assurance' | 'controle_technique';
  uri: string;
  name: string;
}
```

**API Endpoints:**

- `GET /api/v1/vehicles/` - Liste des véhicules
- `POST /api/v1/vehicles/` - Créer un véhicule
- `GET /api/v1/vehicles/{plaque}/` - Détails d'un véhicule
- `PUT /api/v1/vehicles/{plaque}/` - Modifier un véhicule
- `DELETE /api/v1/vehicles/{plaque}/` - Supprimer un véhicule
- `GET /api/v1/vehicles/{plaque}/tax_info/` - Info taxe
- `GET /api/v1/vehicle-types/` - Types de véhicules

### 3. Calcul et Paiement des Taxes

#### TaxCalculationService

Service pour le calcul des taxes.

**Interfaces:**

```typescript
interface TaxCalculationRequest {
  plaque_immatriculation?: string;
  puissance_fiscale_cv: number;
  cylindree_cm3: number;
  source_energie: string;
  date_premiere_circulation: string;
  categorie_vehicule: string;
  annee_fiscale?: number;
}

interface TaxCalculationResponse {
  montant_du_ariary: number;
  annee_fiscale: number;
  est_exonere: boolean;
  grille_tarifaire?: PriceGrid;
  details: {
    exemption_reason?: string;
    error?: string;
  };
}

interface PriceGrid {
  id: number;
  annee_fiscale: number;
  puissance_min_cv: number;
  puissance_max_cv: number;
  tarif_ariary: number;
}
```

**API Endpoints:**

- `POST /api/v1/tax-calculations/calculate/` - Calculer la taxe

#### PaymentService

Service pour la gestion des paiements.

**Interfaces:**

```typescript
interface Payment {
  id: number;
  vehicule_plaque: string;
  montant_paye_ariary: number;
  annee_fiscale: number;
  date_paiement: string;
  methode_paiement: 'MVOLA' | 'STRIPE' | 'CASH';
  statut: 'EN_ATTENTE' | 'PAYE' | 'ECHOUE' | 'ANNULE';
  transaction_id?: string;
  qr_code?: QRCode;
}

interface PaymentInitiateRequest {
  vehicule_plaque: string;
  annee_fiscale: number;
  methode_paiement: 'MVOLA' | 'STRIPE';
  customer_msisdn?: string; // Pour MVola
  payment_method_id?: string; // Pour Stripe
}

interface PaymentInitiateResponse {
  id: number;
  statut: string;
  montant_total: number;
  frais_plateforme: number;
  instructions?: string;
}

interface QRCode {
  token: string;
  qr_code_url: string;
  date_generation: string;
  date_expiration: string;
}
```

**API Endpoints:**

- `POST /api/v1/payments/initiate/` - Initier un paiement
- `GET /api/v1/payments/{id}/` - Statut du paiement
- `GET /api/v1/payments/` - Historique des paiements
- `GET /api/v1/payments/{id}/receipt/` - Télécharger le reçu PDF

#### MVolaPaymentService

Service spécifique pour les paiements MVola.

**Méthodes:**

- `initiate(vehiclePlaque: string, amount: number, msisdn: string): Promise<PaymentInitiateResponse>`
- `checkStatus(paymentId: number): Promise<Payment>`
- `pollStatus(paymentId: number, maxAttempts: number): Promise<Payment>`

#### StripePaymentService

Service spécifique pour les paiements Stripe.

**Méthodes:**

- `initiate(vehiclePlaque: string, amount: number): Promise<PaymentInitiateResponse>`
- `confirmPayment(paymentIntentId: string, paymentMethodId: string): Promise<Payment>`
- `handle3DSecure(paymentIntent: any): Promise<void>`

### 4. QR Code Display

#### QRCodeDisplayService

Service pour afficher et partager les QR codes de paiement.

**Interfaces:**

```typescript
interface QRCodeData {
  token: string;
  qr_code_url: string;
  date_generation: string;
  date_expiration: string;
  vehicle_plaque: string;
  payment_id: number;
}

interface QRCodeShareOptions {
  format: 'image' | 'text';
  includeDetails: boolean;
}
```

**Méthodes:**

- `displayQRCode(qrData: QRCodeData): void` - Afficher le QR code
- `enlargeQRCode(qrData: QRCodeData): void` - Afficher en plein écran
- `shareQRCode(qrData: QRCodeData, options: QRCodeShareOptions): Promise<void>` - Partager le QR code
- `saveToGallery(qrData: QRCodeData): Promise<void>` - Sauvegarder dans la galerie
- `boostBrightness(): void` - Augmenter la luminosité pour faciliter le scan

**Note:** Les citoyens n'ont pas besoin de scanner les QR codes - ils les affichent uniquement pour que les agents gouvernementaux puissent les scanner.

### 5. Notifications

#### NotificationService

Service pour la gestion des notifications push.

**Interfaces:**

```typescript
interface Notification {
  id: number;
  titre: string;
  contenu: string;
  type: 'RAPPEL_PAIEMENT' | 'CONFIRMATION_PAIEMENT' | 'EXPIRATION' | 'ALERTE';
  est_lue: boolean;
  date_creation: string;
  data?: any;
}

interface DeviceToken {
  token: string;
  platform: 'ios' | 'android';
}
```

**Méthodes:**

- `registerDevice(token: DeviceToken): Promise<void>`
- `getNotifications(): Promise<Notification[]>`
- `markAsRead(notificationId: number): Promise<void>`
- `markAllAsRead(): Promise<void>`
- `getUnreadCount(): Promise<number>`
- `handleNotificationReceived(notification: any): void`
- `handleNotificationTapped(notification: any): void`

**API Endpoints:**

- `POST /api/v1/notifications/register-device/` - Enregistrer le device
- `GET /api/v1/notifications/` - Liste des notifications
- `POST /api/v1/notifications/{id}/mark_read/` - Marquer comme lue
- `POST /api/v1/notifications/mark_all_read/` - Tout marquer comme lu
- `GET /api/v1/notifications/unread_count/` - Nombre non lues

### 6. Profil Utilisateur

#### UserProfileService

Service pour la gestion du profil utilisateur.

**Interfaces:**

```typescript
interface UserProfile {
  user: User;
  profile_picture?: string;
  preferred_language: 'fr' | 'mg';
  notifications_enabled: boolean;
  biometric_enabled: boolean;
}

interface UpdateProfileRequest {
  first_name?: string;
  last_name?: string;
  phone?: string;
  preferred_language?: 'fr' | 'mg';
  profile_picture?: string;
}
```

**API Endpoints:**

- `GET /api/v1/users/me/` - Profil actuel
- `PUT /api/v1/users/me/` - Modifier le profil
- `GET /api/v1/profiles/me/` - Détails du profil
- `PUT /api/v1/profiles/me/` - Modifier les détails

### 7. Stockage et Cache

#### StorageService

Service pour le stockage local sécurisé et le cache.

**Méthodes:**

- `secureSet(key: string, value: string): Promise<void>` - Stockage sécurisé (tokens)
- `secureGet(key: string): Promise<string | null>` - Récupération sécurisée
- `secureDelete(key: string): Promise<void>` - Suppression sécurisée
- `set(key: string, value: any): Promise<void>` - Stockage normal (cache)
- `get(key: string): Promise<any>` - Récupération normale
- `delete(key: string): Promise<void>` - Suppression normale
- `clear(): Promise<void>` - Tout effacer

#### OfflineService

Service pour la gestion du mode hors ligne.

**Méthodes:**

- `isOnline(): Promise<boolean>`
- `syncData(): Promise<void>`
- `cacheVehicles(vehicles: Vehicle[]): Promise<void>`
- `getCachedVehicles(): Promise<Vehicle[]>`
- `cachePayments(payments: Payment[]): Promise<void>`
- `getCachedPayments(): Promise<Payment[]>`

## Data Models

### Redux Store Structure

```typescript
interface RootState {
  auth: AuthState;
  vehicles: VehicleState;
  payments: PaymentState;
  notifications: NotificationState;
  settings: SettingsState;
  offline: OfflineState;
}

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface VehicleState {
  vehicles: Vehicle[];
  selectedVehicle: Vehicle | null;
  vehicleTypes: VehicleType[];
  isLoading: boolean;
  error: string | null;
}

interface PaymentState {
  payments: Payment[];
  currentPayment: Payment | null;
  isProcessing: boolean;
  error: string | null;
}

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
}

interface SettingsState {
  language: 'fr' | 'mg';
  biometricEnabled: boolean;
  notificationsEnabled: boolean;
  theme: 'light' | 'dark';
}

interface OfflineState {
  isOnline: boolean;
  lastSync: string | null;
  pendingActions: any[];
}
```

## Error Handling

### Error Types

```typescript
enum ErrorCode {
  NETWORK_ERROR = 'network_error',
  AUTH_ERROR = 'auth_error',
  VALIDATION_ERROR = 'validation_error',
  NOT_FOUND = 'not_found',
  SERVER_ERROR = 'server_error',
  PAYMENT_ERROR = 'payment_error',
  TIMEOUT = 'timeout',
}

interface APIError {
  code: ErrorCode;
  message: string;
  details?: any;
}
```

### Error Handling Strategy

1. **Network Errors**: Afficher un message "Pas de connexion internet" et basculer en mode hors ligne
2. **Auth Errors**: Déconnecter l'utilisateur et rediriger vers l'écran de login
3. **Validation Errors**: Afficher les erreurs sous les champs concernés
4. **Server Errors**: Afficher un message générique et logger l'erreur
5. **Payment Errors**: Afficher un message spécifique avec option de réessayer

### Axios Interceptors

**Request Interceptor:**
- Ajouter le token JWT dans le header Authorization
- Ajouter le header Accept-Language selon la langue sélectionnée
- Logger les requêtes en mode debug

**Response Interceptor:**
- Gérer les erreurs 401 (token expiré) → refresh token automatique
- Gérer les erreurs 403 (permission denied) → redirection
- Gérer les erreurs 500 → afficher message d'erreur
- Transformer les réponses au format standard

## Testing Strategy

### Types de Tests

1. **Unit Tests** (Jest)
   - Services (AuthService, PaymentService, etc.)
   - Utilitaires (validation, formatting)
   - Redux slices et reducers

2. **Integration Tests** (Jest + React Native Testing Library)
   - Flux d'authentification complet
   - Ajout et paiement de véhicule
   - Affichage et partage de QR code

3. **E2E Tests** (Detox)
   - Parcours utilisateur complet
   - Paiement MVola end-to-end
   - Mode hors ligne

4. **Manual Testing**
   - Tests sur devices réels (iOS/Android)
   - Tests de performance
   - Tests d'accessibilité

### Coverage Goals

- Unit Tests: 80% minimum
- Integration Tests: 60% minimum
- E2E Tests: Scénarios critiques couverts

## Performance Optimization

### Stratégies d'Optimisation

1. **Images**
   - Compression avant upload (max 1MB)
   - Utilisation de WebP quand possible
   - Lazy loading des images
   - Cache des images téléchargées

2. **API Calls**
   - Debouncing des recherches
   - Pagination des listes
   - Cache des réponses API (RTK Query)
   - Prefetching des données probables

3. **Rendering**
   - Utilisation de React.memo pour les composants
   - FlatList avec windowSize optimisé
   - Éviter les re-renders inutiles

4. **Bundle Size**
   - Code splitting par écran
   - Tree shaking
   - Minification en production

5. **Offline Performance**
   - Cache local des données essentielles
   - Synchronisation en arrière-plan
   - Queue des actions offline

### Performance Targets

- Temps de démarrage: < 2 secondes
- Navigation entre écrans: < 300ms
- Chargement liste véhicules: < 3 secondes
- Recherche/filtrage: < 500ms
- Taille du bundle: < 30MB

## Security Considerations

### Mesures de Sécurité

1. **Authentification**
   - JWT avec expiration courte (60 min)
   - Refresh token avec expiration longue (7 jours)
   - Stockage sécurisé des tokens (SecureStore)
   - Biométrie optionnelle

2. **Communication**
   - HTTPS uniquement
   - Certificate pinning en production
   - Validation des certificats SSL

3. **Données Sensibles**
   - Pas de stockage de mots de passe
   - Chiffrement des données locales sensibles
   - Effacement des données à la déconnexion

4. **Paiements**
   - Utilisation des SDK officiels (Stripe, MVola)
   - Pas de stockage des informations de carte
   - Validation côté serveur

5. **Code**
   - Obfuscation du code en production
   - Pas de secrets dans le code
   - Variables d'environnement pour les clés API

## Deployment Strategy

### Build Process

1. **Development**
   - Expo Go pour le développement rapide
   - Hot reload activé
   - Debug mode

2. **Staging**
   - Build avec Expo EAS
   - TestFlight (iOS) / Internal Testing (Android)
   - Tests QA

3. **Production**
   - Build optimisé avec Expo EAS
   - App Store (iOS) / Play Store (Android)
   - Monitoring activé

### CI/CD Pipeline

1. **Commit** → Tests unitaires
2. **Pull Request** → Tests d'intégration
3. **Merge to develop** → Build staging
4. **Merge to main** → Build production
5. **Release** → Déploiement stores

### Monitoring

- Crash reporting (Sentry)
- Analytics (Firebase Analytics)
- Performance monitoring (Firebase Performance)
- User feedback (In-app feedback form)

## Internationalization (i18n)

### Structure des Traductions

```json
// fr.json
{
  "auth": {
    "login": "Se connecter",
    "register": "S'inscrire",
    "email": "Email",
    "password": "Mot de passe"
  },
  "vehicles": {
    "list": "Mes véhicules",
    "add": "Ajouter un véhicule",
    "plate": "Plaque d'immatriculation"
  },
  "payments": {
    "pay": "Payer",
    "amount": "Montant",
    "history": "Historique"
  }
}

// mg.json
{
  "auth": {
    "login": "Hiditra",
    "register": "Hisoratra anarana",
    "email": "Email",
    "password": "Teny miafina"
  },
  "vehicles": {
    "list": "Ny fiarako",
    "add": "Hanampy fiara",
    "plate": "Takelaka"
  },
  "payments": {
    "pay": "Handoa",
    "amount": "Vola",
    "history": "Tantara"
  }
}
```

### Gestion des Langues

- Détection automatique de la langue du système au premier lancement
- Changement de langue en temps réel
- Persistance de la préférence
- Synchronisation avec le backend

## Accessibility

### Conformité WCAG 2.1 Level AA

1. **Contraste des Couleurs**
   - Ratio minimum 4.5:1 pour le texte normal
   - Ratio minimum 3:1 pour le texte large

2. **Navigation au Clavier**
   - Support complet de la navigation au clavier
   - Focus visible sur tous les éléments interactifs

3. **Screen Readers**
   - Labels accessibles sur tous les éléments
   - Annonces pour les changements d'état
   - Support de VoiceOver (iOS) et TalkBack (Android)

4. **Taille des Cibles Tactiles**
   - Minimum 44x44 points pour tous les boutons
   - Espacement suffisant entre les éléments

5. **Texte Redimensionnable**
   - Support du zoom jusqu'à 200%
   - Pas de perte de contenu ou de fonctionnalité

## Future Enhancements

### Phase 2 (Post-MVP)

1. **Fonctionnalités Avancées**
   - Paiement en plusieurs fois
   - Gestion de flotte pour entreprises
   - Export des données (PDF, Excel)
   - Partage de véhicules entre utilisateurs

2. **Intégrations**
   - Apple Pay / Google Pay
   - Autres opérateurs mobile money
   - Intégration avec assurances

3. **Améliorations UX**
   - Mode sombre
   - Widgets iOS/Android
   - Siri Shortcuts / Google Assistant
   - Animations avancées

4. **Analytics**
   - Dashboard de statistiques personnelles
   - Prédictions de dépenses
   - Rappels intelligents

