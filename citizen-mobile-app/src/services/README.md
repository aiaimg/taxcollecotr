# Services

This directory contains service modules that handle business logic and external integrations.

## AuthService

Handles all authentication-related operations including login, registration, logout, and token management.

### Features

- **Login**: Authenticate users with email and password
- **Register**: Create new user accounts
- **Logout**: Clear user session and tokens
- **Token Management**: Automatic JWT token refresh
- **Secure Storage**: Uses Expo SecureStore for sensitive data

### Usage

```typescript
import { authService } from '../services';

// Login
const response = await authService.login({
  email: 'user@example.com',
  password: 'password123',
});

// Register
const response = await authService.register({
  user_type: 'PARTICULIER',
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com',
  phone: '+261340000000',
  password: 'password123',
  password_confirm: 'password123',
  preferred_language: 'fr',
});

// Logout
await authService.logout();

// Check authentication status
const isAuth = await authService.isAuthenticated();

// Get stored user
const user = await authService.getStoredUser();
```

## StorageService

Provides a unified interface for secure and normal storage operations.

### Features

- **Secure Storage**: Uses Expo SecureStore for sensitive data (tokens, credentials)
- **Normal Storage**: Uses AsyncStorage for non-sensitive data (cache, preferences)
- **Batch Operations**: Support for multiple key operations
- **Type Safety**: TypeScript support with generics

### Usage

```typescript
import { storageService, StorageService } from '../services';

// Secure storage (for sensitive data)
await storageService.secureSet(StorageService.KEYS.ACCESS_TOKEN, token);
const token = await storageService.secureGet(StorageService.KEYS.ACCESS_TOKEN);
await storageService.secureDelete(StorageService.KEYS.ACCESS_TOKEN);

// Normal storage (for non-sensitive data)
await storageService.set('user_preferences', { theme: 'dark' });
const prefs = await storageService.get('user_preferences');
await storageService.delete('user_preferences');

// Batch operations
const data = await storageService.getMultiple(['key1', 'key2']);
await storageService.setMultiple([
  ['key1', 'value1'],
  ['key2', 'value2'],
]);

// Clear all data
await storageService.clearAll();
```

## BiometricService

Handles biometric authentication using Expo Local Authentication. Supports Touch ID (iOS) and Fingerprint/Face Unlock (Android).

### Features

- **Availability Check**: Detect if biometric hardware is available and enrolled
- **Authentication**: Authenticate users with biometric credentials
- **Preference Management**: Store and retrieve biometric authentication preference
- **Enrollment Prompt**: Prompt users to enable biometric authentication
- **Multiple Types**: Support for fingerprint, face recognition, and iris scanning

### Usage

```typescript
import { biometricService } from '../services';

// Check if biometric is available
const isAvailable = await biometricService.isAvailable();

// Get supported biometric types
const types = await biometricService.getSupportedTypes();
const typeName = await biometricService.getBiometricTypeName();

// Authenticate user
const authenticated = await biometricService.authenticate('Login with biometric');

// Enable biometric authentication
await biometricService.enableBiometric();

// Disable biometric authentication
await biometricService.disableBiometric();

// Check if biometric is enabled
const isEnabled = await biometricService.isBiometricEnabled();

// Check if should prompt enrollment
const shouldPrompt = await biometricService.shouldPromptEnrollment();

// Perform biometric login
const success = await biometricService.biometricLogin();

// Get security level
const securityLevel = await biometricService.getSecurityLevel();
```

### Integration with Login Flow

The biometric service is integrated into the login flow:

1. After successful password login, check if biometric is available but not enabled
2. If available, prompt user to enable biometric authentication
3. If user enables it, store the preference securely
4. On subsequent app launches, show biometric login button if enabled
5. User can login with biometric instead of password

### Security Considerations

- Biometric preference is stored in Expo SecureStore
- Biometric authentication requires device passcode as fallback
- Tokens are still required for API authentication
- Biometric only provides quick access to stored credentials

## API Client

The API client is configured with interceptors for authentication and error handling.

### Features

- **Automatic Token Injection**: Adds JWT token to all requests
- **Token Refresh**: Automatically refreshes expired tokens
- **Language Header**: Adds Accept-Language header based on user preference
- **Error Handling**: Centralized error handling and logging
- **Request Queuing**: Queues requests during token refresh

### Configuration

The API client is pre-configured and exported from `src/api/client.ts`. All services use this client for API calls.

```typescript
import apiClient from '../api/client';

// Make API calls
const response = await apiClient.get('/api/v1/vehicles/');
const response = await apiClient.post('/api/v1/vehicles/', data);
```

## Error Handling

All services use consistent error handling:

```typescript
try {
  await authService.login(credentials);
} catch (error) {
  // Error is already logged by the service
  // Handle error in UI
  if (isAuthError(error)) {
    // Handle authentication error
  } else if (isNetworkError(error)) {
    // Handle network error
  } else {
    // Handle other errors
  }
}
```

## Security Considerations

1. **Tokens**: All tokens are stored in Expo SecureStore (Keychain on iOS, Keystore on Android)
2. **Passwords**: Never stored locally, only transmitted over HTTPS
3. **Automatic Cleanup**: Tokens are cleared on logout or refresh failure
4. **Token Expiry**: Access tokens expire after 60 minutes, refresh tokens after 7 days

## Testing

Services can be tested by mocking the API client and storage:

```typescript
jest.mock('../api/client');
jest.mock('expo-secure-store');

// Test authentication
test('login should store tokens', async () => {
  const mockResponse = {
    data: {
      access: 'access_token',
      refresh: 'refresh_token',
      user: { id: 1, email: 'test@example.com' },
    },
  };
  
  (apiClient.post as jest.Mock).mockResolvedValue(mockResponse);
  
  const response = await authService.login({
    email: 'test@example.com',
    password: 'password',
  });
  
  expect(response).toEqual(mockResponse.data);
});
```
