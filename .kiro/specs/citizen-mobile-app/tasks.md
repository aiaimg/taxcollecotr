# Implementation Plan - Tax Collector Citizen Mobile App

- [x] 1. Set up project structure and core configuration
  - Create new React Native project with Expo (SDK 50+) in folder `citizen-mobile-app/` (NOT scan-agent-app/)
  - Configure TypeScript with strict mode
  - Set up folder structure (src/api, src/components, src/screens, src/store, etc.)
  - Install and configure core dependencies (React Navigation, Redux Toolkit, RTK Query, Axios, i18next)
  - Configure environment variables for API endpoints (connect to existing Django backend)
  - Set up ESLint and Prettier for code quality
  - _Requirements: 1.1, 1.2, 2.1, 12.1_

- [x] 2. Implement authentication system
- [x] 2.1 Create authentication API client and services
  - Implement Axios client with base configuration
  - Create auth interceptors for JWT token management
  - Implement AuthService with login, register, logout, and token refresh methods
  - Configure Expo SecureStore for secure token storage
  - _Requirements: 1.3, 1.4, 2.2, 2.3, 2.4_

- [x] 2.2 Build authentication screens and navigation
  - Create AuthNavigator with Login and Register screens
  - Implement Login screen with email/password form and validation
  - Implement Register screen with multi-step form (user type, personal info, credentials)
  - Add form validation for email format, phone format (+261XXXXXXXXX), and password strength
  - Implement error handling and display for authentication failures
  - _Requirements: 1.1, 1.2, 1.7, 2.1, 2.7_

- [x] 2.3 Implement Redux auth slice and RTK Query auth API
  - Create authSlice with user state, tokens, and authentication status
  - Implement authApi with RTK Query for login, register, logout, and refresh endpoints
  - Configure Redux Persist to persist auth state
  - Implement automatic token refresh logic when access token expires
  - _Requirements: 1.4, 2.3, 2.4, 2.5, 2.6_

- [x] 2.4 Add biometric authentication support
  - Implement BiometricService using Expo Local Authentication
  - Add biometric availability check and enrollment prompt
  - Implement biometric login flow after initial password login
  - Store biometric preference in settings
  - _Requirements: 2.4_

- [x] 2.5 Write authentication tests
  - Unit tests for AuthService methods
  - Integration tests for login and register flows
  - Tests for token refresh logic
  - _Requirements: 1.1-2.7_

- [x] 3. Implement vehicle management
- [x] 3.1 Create vehicle API client and services
  - Implement VehicleService with CRUD operations
  - Create vehicle API endpoints using RTK Query (list, create, update, delete, tax_info)
  - Implement vehicle types API endpoint
  - _Requirements: 3.1, 3.2, 4.1_

- [x] 3.2 Build vehicle list screen
  - Create VehicleListScreen with FlatList for vehicle display
  - Implement vehicle card component showing plaque, marque/modèle, photo, and tax status
  - Add status badges (Payé/Impayé/Expiré/Exonéré) with appropriate colors
  - Implement pull-to-refresh functionality
  - Add empty state with "Ajouter un véhicule" button
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 3.3 Build vehicle detail screen
  - Create VehicleDetailScreen showing all vehicle information
  - Display tax calculation with amount and due date
  - Show QR code and receipt if tax is paid
  - Add "Payer maintenant" button if tax is unpaid
  - Display exemption reason if vehicle is exempt
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [x] 3.4 Build add vehicle screen with multi-step form
  - Create AddVehicleScreen with tab navigation for multi-step form
  - Implement Step 1: Basic information (plaque, marque, modèle, couleur, VIN, sans plaque checkbox)
  - Implement Step 2: Technical specifications (type, puissance fiscale, cylindrée, source d'énergie, date circulation)
  - Implement Step 3: Category selection (Personnel/Commercial based on user type)
  - Implement Step 4: Document upload (carte grise recto/verso, assurance, contrôle technique)
  - Add automatic plaque generation for vehicles without plates
  - Implement cylindrée to puissance fiscale suggestion
  - Add form validation for all required fields
  - Implement image compression before upload
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

- [x] 3.5 Implement vehicle Redux slice
  - Create vehicleSlice with vehicles list, selected vehicle, and vehicle types
  - Implement actions for adding, updating, and deleting vehicles
  - Add loading and error states
  - _Requirements: 3.1-4.10_

- [ ]* 3.6 Write vehicle management tests
  - Unit tests for VehicleService
  - Integration tests for vehicle CRUD operations
  - Tests for form validation
  - _Requirements: 3.1-4.10_

- [x] 4. Implement tax calculation and payment system
- [x] 4.1 Create tax calculation service
  - Implement TaxCalculationService with calculate method
  - Create tax calculation API endpoint using RTK Query
  - Implement tax calculation display component with breakdown
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 4.2 Build payment method selection screen
  - Create PaymentMethodScreen with MVola, Stripe, and Cash options
  - Display payment method cards with icons and descriptions
  - Navigate to appropriate payment flow based on selection
  - _Requirements: 6.1_

- [x] 4.3 Implement MVola payment flow
  - Create MVolaPaymentService with initiate and checkStatus methods
  - Build MVola payment screen with phone number input (+261XXXXXXXXX format)
  - Display total amount with platform fees (3%) breakdown
  - Implement payment initiation and waiting screen
  - Add payment status polling (every 3 seconds)
  - Show success screen with receipt and QR code on confirmation
  - Handle payment failures with clear error messages and retry option
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [x] 4.4 Implement Stripe payment flow
  - Install and configure Stripe React Native SDK
  - Create StripePaymentService with initiate and confirmPayment methods
  - Build Stripe payment screen with card input form
  - Implement real-time card validation
  - Handle 3D Secure authentication in WebView
  - Show success screen with receipt and QR code on confirmation
  - Handle payment failures with clear error messages
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 4.5 Build payment history screen
  - Create PaymentHistoryScreen with FlatList of payments
  - Display payment cards with vehicle, amount, date, method icon, and status
  - Implement payment detail modal with full transaction information
  - Add receipt download functionality (PDF)
  - Implement filters by year and vehicle
  - Add empty state for no payments
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 4.6 Implement payment Redux slice
  - Create paymentSlice with payments list and current payment
  - Implement actions for initiating, confirming, and fetching payments
  - Add processing and error states
  - _Requirements: 6.1-9.6_

- [ ]* 4.7 Write payment system tests
  - Unit tests for payment services
  - Integration tests for MVola and Stripe payment flows
  - Tests for payment status polling
  - _Requirements: 6.1-9.6_

- [x] 5. Implement push notifications
- [x] 5.1 Create notification service
  - Install and configure Expo Notifications
  - Implement NotificationService with device registration
  - Request notification permissions on app start
  - Register device token with backend
  - _Requirements: 10.1, 10.2_

- [x] 5.2 Implement notification handling
  - Handle foreground notifications with in-app display
  - Handle background notifications
  - Implement notification tap handling with navigation to appropriate screen
  - Support notification types (payment reminder, confirmation, expiration, alerts)
  - _Requirements: 10.3, 10.4, 10.5_

- [x] 5.3 Build notifications list screen
  - Create NotificationsScreen with FlatList of notifications
  - Display notification cards with title, content, type icon, and timestamp
  - Implement mark as read functionality
  - Add mark all as read button
  - Show unread count badge in navigation
  - _Requirements: 10.5_

- [x] 5.4 Add notification preferences in settings
  - Create notification settings section
  - Add toggles for notification types
  - Persist preferences locally and sync with backend
  - _Requirements: 10.6_

- [ ]* 5.5 Write notification tests
  - Unit tests for NotificationService
  - Integration tests for notification handling
  - Tests for navigation from notifications
  - _Requirements: 10.1-10.6_

- [x] 6. Implement offline mode and data synchronization
- [x] 6.1 Create offline service and network detection
  - Create OfflineService with sync and cache methods
  - Implement network status detection using @react-native-community/netinfo
  - Add network status listener to Redux store
  - Display "Mode hors ligne" indicator in status bar when offline
  - _Requirements: 11.1, 11.2_

- [x] 6.2 Implement offline data caching
  - Configure Redux Persist to cache vehicles and payments
  - Allow viewing cached vehicles list when offline
  - Allow viewing cached payment history when offline
  - Show cached data timestamp in UI
  - _Requirements: 11.2, 11.3_

- [x] 6.3 Implement online actions blocking and sync
  - Block payment actions when offline with clear message
  - Block vehicle creation when offline with clear message
  - Implement automatic data sync when connection is restored
  - Show sync indicator during synchronization
  - _Requirements: 11.4, 11.5, 11.6_

- [ ]* 6.4 Write offline mode tests
  - Unit tests for OfflineService
  - Integration tests for offline data access
  - Tests for sync logic
  - _Requirements: 11.1-11.6_

- [x] 7. Implement internationalization (i18n)
- [x] 7.1 Set up i18n infrastructure
  - Install and configure i18next and react-i18next
  - Create translation files for French (fr.json) and Malagasy (mg.json)
  - Implement language detection from system settings
  - Configure language persistence
  - _Requirements: 12.1, 12.4_

- [ ] 7.2 Complete translations for all screens
  - Translate vehicle management screens
  - Translate payment screens
  - Translate notifications and error messages
  - Translate settings and profile screens
  - _Requirements: 12.2, 12.5_

- [ ] 7.3 Build language settings
  - Create language selection in settings screen
  - Implement real-time language switching
  - Sync language preference with backend
  - _Requirements: 12.1, 12.2, 12.3_

- [ ]* 7.4 Write i18n tests
  - Tests for language switching
  - Tests for translation completeness
  - _Requirements: 12.1-12.5_

- [x] 8. Implement user profile and settings
- [x] 8.1 Create profile service and screen
  - Implement UserProfileService with get and update methods
  - Create ProfileScreen displaying user information
  - Show profile picture, name, email, phone, user type, and language
  - Add edit button to navigate to edit screen
  - _Requirements: 13.1_

- [x] 8.2 Build profile edit screen
  - Create ProfileEditScreen with pre-filled form
  - Allow editing of name, phone, and profile picture
  - Implement image picker for profile picture using expo-image-picker (camera or gallery)
  - Add form validation (email format, phone format)
  - Implement save functionality with API call
  - Show success message on update
  - _Requirements: 13.2, 13.3, 13.4, 13.5, 13.6_

- [x] 8.3 Build settings screen
  - Create SettingsScreen with sections for language, notifications, biometric, and account
  - Add language selection option
  - Add notification preferences toggles
  - Add biometric authentication toggle
  - Add logout button with confirmation dialog
  - _Requirements: 12.1, 14.1_

- [x] 8.4 Implement logout functionality
  - Show confirmation dialog on logout
  - Call logout API endpoint to invalidate token
  - Clear all tokens from SecureStore
  - Clear cached data from AsyncStorage
  - Disable biometric authentication
  - Navigate to login screen
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

- [ ]* 8.5 Write profile and settings tests
  - Unit tests for UserProfileService
  - Integration tests for profile update
  - Tests for logout flow
  - _Requirements: 13.1-14.6_

- [x] 9. Implement navigation and main app structure
- [x] 9.1 Create main navigation structure
  - Implement AppNavigator with authentication check and conditional routing
  - Create MainNavigator with bottom tabs (Dashboard, Vehicles, Payments, Notifications, Profile)
  - Configure stack navigators for each tab
  - Configure deep linking for notifications
  - Wire up App.tsx to use AppNavigator instead of placeholder
  - _Requirements: 1.1, 2.1, 3.1_

- [x] 9.2 Build dashboard screen
  - Create DashboardScreen with overview widgets
  - Display vehicle count and tax status summary
  - Show recent payments list
  - Display upcoming payment reminders
  - Add quick action buttons (Add Vehicle, Pay Tax)
  - _Requirements: 3.1, 5.1, 9.1_

- [x] 9.3 Implement loading states and error boundaries
  - Create reusable loading spinner component
  - Create skeleton loaders for vehicle and payment lists
  - Implement error boundary component for crash handling
  - Add retry mechanisms for failed API requests
  - _Requirements: 15.7_

- [ ]* 9.4 Write navigation tests
  - Integration tests for navigation flows
  - Tests for deep linking
  - _Requirements: 1.1-15.8_

- [x] 10. Implement performance optimizations
- [x] 10.1 Optimize images and media
  - Implement image compression before upload using expo-image-manipulator (max 1MB)
  - Use expo-image for optimized image rendering
  - Implement lazy loading for images in FlatLists
  - Cache downloaded images locally
  - _Requirements: 15.5_

- [x] 10.2 Optimize API calls and rendering
  - Configure RTK Query cache with appropriate TTL (5 minutes for vehicles, 10 minutes for payments)
  - Implement debouncing for search inputs
  - Use React.memo for expensive components (VehicleCard, PaymentCard)
  - Optimize FlatList with windowSize and getItemLayout
  - Implement prefetching for likely next screens
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.6_

- [ ]* 10.3 Performance testing and monitoring
  - Measure app startup time
  - Measure screen transition times
  - Measure API response times
  - Test on low-end devices
  - _Requirements: 15.1-15.8_

- [ ] 11. Implement QR code display functionality
- [ ] 11.1 Add QR code display to vehicle detail screen
  - Display QR code image when vehicle has paid tax
  - Show QR code generation and expiration dates
  - Add tap-to-enlarge functionality for full-screen QR code view
  - Show "No QR code available" message for unpaid vehicles
  - _Requirements: 8.1, 8.2, 8.3, 8.8_

- [ ] 11.2 Enhance QR code in payment history
  - Ensure QR code is displayed in payment detail modal
  - Add share QR code functionality using React Native Share API
  - Add save to gallery functionality using expo-media-library
  - _Requirements: 8.4, 8.5, 8.6, 8.7_

- [ ] 11.3 Create full-screen QR code viewer
  - Create QRCodeViewerScreen for enlarged QR code display
  - Add brightness boost for better scanning by agents
  - Display vehicle and payment information alongside QR code
  - Add close button to return to previous screen
  - _Requirements: 8.3_

- [ ]* 11.4 Write QR display tests
  - Unit tests for QR code display logic
  - Integration tests for share and save functionality
  - Tests for full-screen viewer
  - _Requirements: 8.1-8.8_

- [ ] 12. Implement security measures : dev/ prod
- [ ] 12.1 Configure security settings
  - Ensure HTTPS-only communication in API client on production
  - Implement certificate pinning for production builds
  - Add code obfuscation for production builds
  - Ensure no sensitive data in console logs
  - Validate all user inputs on client side
  - Implement rate limiting on client side for API calls
  - _Requirements: 1.4, 2.3, 6.3, 7.2_

- [ ] 13. Build and deployment setup
- [ ] 13.1 Configure Expo EAS Build
  - Set up EAS Build configuration (eas.json)
  - Configure build profiles (development, staging, production)
  - Set up environment variables for each profile
  - Configure app signing for iOS and Android
  - _Requirements: All_

- [ ] 13.2 Set up CI/CD pipeline
  - Configure GitHub Actions for automated testing
  - Set up automated builds on PR merge
  - Configure automated deployment to TestFlight and Internal Testing
  - Set up crash reporting with Sentry
  - Configure analytics with Firebase
  - _Requirements: All_

- [ ]* 13.3 Create deployment documentation
  - Document build process
  - Document release process
  - Document environment configuration
  - _Requirements: All_

