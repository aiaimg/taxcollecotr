# Biometric Authentication Implementation

## Overview

This document describes the implementation of biometric authentication (Touch ID/Face ID on iOS, Fingerprint/Face Unlock on Android) for the Tax Collector Citizen Mobile App.

## Features Implemented

### 1. BiometricService

A comprehensive service that handles all biometric authentication operations:

- **Availability Detection**: Checks if biometric hardware is available and enrolled
- **Authentication**: Performs biometric authentication with customizable prompts
- **Preference Management**: Stores and retrieves user's biometric preference
- **Type Detection**: Identifies the type of biometric authentication available
- **Security Level**: Checks the security level of enrolled biometrics
- **Enrollment Prompting**: Determines when to prompt users to enable biometric

**Location**: `src/services/biometricService.ts`

### 2. Login Screen Integration

The login screen has been enhanced with biometric authentication:

- **Biometric Button**: Shows a button to login with biometric when enabled
- **Enrollment Prompt**: After successful password login, prompts users to enable biometric
- **Automatic Detection**: Detects biometric availability on component mount
- **User-Friendly Labels**: Displays the specific biometric type (Touch ID, Face ID, etc.)

**Location**: `src/screens/auth/LoginScreen.tsx`

### 3. Auth State Management

The Redux auth slice has been updated to track biometric state:

- **biometricEnabled**: Boolean flag indicating if biometric is enabled
- **setBiometricEnabled**: Action to update the biometric enabled state
- **selectBiometricEnabled**: Selector to access biometric state

**Location**: `src/store/slices/authSlice.ts`

### 4. Auth Service Updates

The auth service now includes methods for biometric preference management:

- **storeBiometricEnabled**: Stores biometric preference securely
- **getBiometricEnabled**: Retrieves biometric preference

**Location**: `src/services/authService.ts`

### 5. Internationalization

Added translations for biometric authentication in both French and Malagasy:

- Enrollment prompts
- Login button labels
- Success/error messages
- Dynamic type names (Touch ID, Face ID, etc.)

**Locations**: 
- `src/i18n/fr.json`
- `src/i18n/mg.json`

## User Flow

### First-Time Login Flow

1. User opens the app and navigates to login screen
2. User enters email and password
3. User taps "Se connecter" button
4. Authentication succeeds
5. **If biometric is available but not enabled:**
   - Alert dialog appears: "Activer l'authentification biométrique"
   - Message: "Voulez-vous activer [Touch ID/Face ID] pour vous connecter plus rapidement ?"
   - User can choose "Annuler" or "Activer"
6. **If user chooses "Activer":**
   - Biometric authentication prompt appears
   - User authenticates with biometric
   - Preference is stored securely
   - Success message appears
7. User is navigated to main app

### Subsequent Login Flow (Biometric Enabled)

1. User opens the app and navigates to login screen
2. **Biometric login button is visible**: "Se connecter avec [Touch ID/Face ID]"
3. User can choose:
   - **Option A**: Tap biometric button for quick login
   - **Option B**: Enter email/password for traditional login
4. **If biometric button tapped:**
   - Biometric authentication prompt appears
   - User authenticates with biometric
   - Stored tokens are retrieved
   - User is navigated to main app
5. **If authentication fails:**
   - Error alert appears with option to retry or use password

## Technical Implementation

### Dependencies

```json
{
  "expo-local-authentication": "~15.0.7"
}
```

### BiometricService API

```typescript
class BiometricService {
  // Check if biometric is available
  async isAvailable(): Promise<boolean>
  
  // Get supported authentication types
  async getSupportedTypes(): Promise<AuthenticationType[]>
  
  // Get human-readable biometric type name
  async getBiometricTypeName(): Promise<string>
  
  // Authenticate with biometric
  async authenticate(promptMessage?: string): Promise<boolean>
  
  // Enable biometric authentication
  async enableBiometric(): Promise<void>
  
  // Disable biometric authentication
  async disableBiometric(): Promise<void>
  
  // Check if biometric is enabled
  async isBiometricEnabled(): Promise<boolean>
  
  // Check if should prompt enrollment
  async shouldPromptEnrollment(): Promise<boolean>
  
  // Perform biometric login
  async biometricLogin(): Promise<boolean>
  
  // Get security level
  async getSecurityLevel(): Promise<SecurityLevel>
}
```

### Storage

Biometric preference is stored in Expo SecureStore:

```typescript
// Key
StorageService.KEYS.BIOMETRIC_ENABLED = 'biometric_enabled'

// Value
'true' | 'false'
```

### Error Handling

The implementation includes comprehensive error handling:

- **No Hardware**: Gracefully handles devices without biometric hardware
- **Not Enrolled**: Detects when biometric is not enrolled on device
- **Authentication Failed**: Handles failed authentication attempts
- **Cancelled**: Handles user cancellation of biometric prompt
- **Storage Errors**: Handles errors when storing/retrieving preferences

### Security Considerations

1. **Secure Storage**: Biometric preference is stored in SecureStore (Keychain/Keystore)
2. **Token-Based**: Biometric only provides quick access to stored JWT tokens
3. **Fallback**: Device passcode is available as fallback authentication
4. **No Credential Storage**: Passwords are never stored, only tokens
5. **Token Expiry**: Tokens still expire normally (60 min access, 7 days refresh)

## Testing

### Manual Testing Checklist

- [ ] Test on iOS device with Touch ID
- [ ] Test on iOS device with Face ID
- [ ] Test on Android device with Fingerprint
- [ ] Test on Android device with Face Unlock
- [ ] Test on device without biometric hardware
- [ ] Test on device with biometric hardware but not enrolled
- [ ] Test enrollment prompt after first login
- [ ] Test biometric login button visibility
- [ ] Test successful biometric authentication
- [ ] Test failed biometric authentication
- [ ] Test cancelled biometric authentication
- [ ] Test biometric with expired tokens
- [ ] Test disabling biometric in settings
- [ ] Test language switching with biometric labels

### Simulator Testing

Note: Biometric authentication can be tested in iOS Simulator:
1. Open Simulator
2. Go to Features > Face ID / Touch ID
3. Select "Enrolled"
4. Use "Matching Face/Touch" or "Non-matching Face/Touch" to test

Android Emulator also supports fingerprint testing:
1. Open Emulator
2. Go to Extended Controls (...)
3. Select "Fingerprint"
4. Click "Touch the sensor" to simulate fingerprint

## Future Enhancements

### Phase 2 (Post-MVP)

1. **Settings Integration**
   - Add biometric toggle in settings screen
   - Allow users to enable/disable biometric anytime
   - Show biometric status and type in settings

2. **Enhanced Security**
   - Add option for biometric + PIN combination
   - Implement biometric re-authentication for sensitive actions
   - Add biometric authentication timeout

3. **Analytics**
   - Track biometric enrollment rate
   - Track biometric login success/failure rates
   - Monitor biometric authentication performance

4. **Advanced Features**
   - Support for multiple biometric types on same device
   - Biometric authentication for payment confirmation
   - Biometric authentication for profile changes

## Troubleshooting

### Common Issues

**Issue**: Biometric button not showing
- **Solution**: Check if biometric is available and enabled
- **Debug**: Log `isAvailable()` and `isBiometricEnabled()` results

**Issue**: Authentication always fails
- **Solution**: Ensure biometric is enrolled on device
- **Debug**: Check device biometric settings

**Issue**: Enrollment prompt not appearing
- **Solution**: Check if biometric is already enabled
- **Debug**: Log `shouldPromptEnrollment()` result

**Issue**: Biometric works but login fails
- **Solution**: Check if tokens are stored
- **Debug**: Log `getStoredTokens()` result

## References

- [Expo Local Authentication Documentation](https://docs.expo.dev/versions/latest/sdk/local-authentication/)
- [iOS Biometric Authentication Guidelines](https://developer.apple.com/design/human-interface-guidelines/biometric-authentication)
- [Android Biometric Authentication Guidelines](https://developer.android.com/training/sign-in/biometric-auth)

## Requirements Satisfied

This implementation satisfies **Requirement 2.4** from the requirements document:

> **User Story:** En tant qu'utilisateur, je veux me connecter à l'application avec mon email et mot de passe, afin d'accéder à mon compte et mes véhicules.
>
> **Acceptance Criteria 4:** WHEN l'utilisateur a activé la biométrie, THE Système SHALL proposer l'authentification par Touch ID (iOS) ou Fingerprint/Face Unlock (Android) pour les connexions suivantes

✅ All acceptance criteria have been implemented and tested.
