# Redux Store Usage Examples

This document provides practical examples of using the Redux store and RTK Query in components.

## Table of Contents

1. [Basic Setup](#basic-setup)
2. [Authentication Examples](#authentication-examples)
3. [State Management Examples](#state-management-examples)
4. [Token Refresh Examples](#token-refresh-examples)
5. [Error Handling](#error-handling)

## Basic Setup

### Wrapping App with Redux Provider

```typescript
// App.tsx
import React from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { store, persistor } from './store';
import AppNavigator from './navigation/AppNavigator';

export default function App() {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <AppNavigator />
      </PersistGate>
    </Provider>
  );
}
```

## Authentication Examples

### Login Example

```typescript
// screens/auth/LoginScreen.tsx
import React, { useState } from 'react';
import { View, TextInput, Button, Text, ActivityIndicator } from 'react-native';
import { useLoginMutation } from '@/store';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // RTK Query hook - provides mutation function and state
  const [login, { isLoading, error }] = useLoginMutation();

  const handleLogin = async () => {
    try {
      // Call login mutation
      const result = await login({ email, password }).unwrap();
      
      // Success! User and tokens are automatically stored in Redux and SecureStore
      console.log('Login successful:', result.user);
      
      // Navigation will happen automatically via auth state change
    } catch (err) {
      // Error is automatically set in the hook state
      console.error('Login failed:', err);
    }
  };

  return (
    <View>
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <Button
        title={isLoading ? 'Logging in...' : 'Login'}
        onPress={handleLogin}
        disabled={isLoading}
      />
      
      {isLoading && <ActivityIndicator />}
      
      {error && (
        <Text style={{ color: 'red' }}>
          {error.data?.message || 'Login failed'}
        </Text>
      )}
    </View>
  );
}
```

### Register Example

```typescript
// screens/auth/RegisterScreen.tsx
import React, { useState } from 'react';
import { View, TextInput, Button, Text } from 'react-native';
import { useRegisterMutation } from '@/store';
import type { UserType } from '@/types/models';

export default function RegisterScreen() {
  const [formData, setFormData] = useState({
    user_type: 'PARTICULIER' as UserType,
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    password_confirm: '',
    preferred_language: 'fr' as 'fr' | 'mg',
  });

  const [register, { isLoading, error }] = useRegisterMutation();

  const handleRegister = async () => {
    try {
      const result = await register(formData).unwrap();
      console.log('Registration successful:', result);
      // User is automatically logged in
    } catch (err) {
      console.error('Registration failed:', err);
    }
  };

  return (
    <View>
      {/* Form fields */}
      <TextInput
        placeholder="First Name"
        value={formData.first_name}
        onChangeText={(text) => setFormData({ ...formData, first_name: text })}
      />
      
      {/* More fields... */}
      
      <Button
        title={isLoading ? 'Registering...' : 'Register'}
        onPress={handleRegister}
        disabled={isLoading}
      />
      
      {error && <Text style={{ color: 'red' }}>Registration failed</Text>}
    </View>
  );
}
```

### Logout Example

```typescript
// screens/settings/SettingsScreen.tsx
import React from 'react';
import { View, Button, Alert } from 'react-native';
import { useLogoutMutation } from '@/store';

export default function SettingsScreen() {
  const [logout, { isLoading }] = useLogoutMutation();

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              await logout().unwrap();
              // User is automatically logged out
              // Navigation to login screen happens automatically
            } catch (err) {
              console.error('Logout failed:', err);
              // Even if API call fails, local logout still happens
            }
          },
        },
      ]
    );
  };

  return (
    <View>
      <Button
        title={isLoading ? 'Logging out...' : 'Logout'}
        onPress={handleLogout}
        disabled={isLoading}
      />
    </View>
  );
}
```

## State Management Examples

### Accessing Auth State

```typescript
// components/UserProfile.tsx
import React from 'react';
import { View, Text } from 'react-native';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser, selectIsAuthenticated } from '@/store';

export default function UserProfile() {
  // Use typed selector hook
  const user = useAppSelector(selectCurrentUser);
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  if (!isAuthenticated || !user) {
    return <Text>Not logged in</Text>;
  }

  return (
    <View>
      <Text>Welcome, {user.first_name} {user.last_name}!</Text>
      <Text>Email: {user.email}</Text>
      <Text>Phone: {user.phone}</Text>
      <Text>Type: {user.user_type}</Text>
    </View>
  );
}
```

### Conditional Rendering Based on Auth State

```typescript
// navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { useAppSelector } from '@/store/hooks';
import { selectIsAuthenticated } from '@/store';
import AuthNavigator from './AuthNavigator';
import MainNavigator from './MainNavigator';

export default function AppNavigator() {
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}
```

### Manual State Updates

```typescript
// Rarely needed, but available if necessary
import { useAppDispatch } from '@/store/hooks';
import { setUser, setError } from '@/store';

function SomeComponent() {
  const dispatch = useAppDispatch();

  const updateUser = (updatedUser) => {
    dispatch(setUser(updatedUser));
  };

  const showError = (message) => {
    dispatch(setError(message));
  };

  // ...
}
```

## Token Refresh Examples

### Automatic Token Refresh

Token refresh happens automatically in the background. You don't need to do anything!

```typescript
// Any API call that returns 401 will automatically:
// 1. Attempt to refresh the token
// 2. Retry the original request
// 3. Logout if refresh fails

// Example: This will automatically refresh if token expired
const { data, error } = useGetCurrentUserQuery();
```

### Manual Token Refresh

```typescript
// Rarely needed, but available
import { useRefreshTokenMutation } from '@/store';
import storageService, { StorageService } from '@/services/storageService';

function SomeComponent() {
  const [refreshToken] = useRefreshTokenMutation();

  const manualRefresh = async () => {
    try {
      const refresh = await storageService.secureGet(
        StorageService.KEYS.REFRESH_TOKEN
      );
      
      if (refresh) {
        await refreshToken({ refresh }).unwrap();
        console.log('Token refreshed successfully');
      }
    } catch (err) {
      console.error('Manual refresh failed:', err);
    }
  };

  // ...
}
```

### Using Token Refresh Service

```typescript
import tokenRefreshService from '@/services/tokenRefreshService';

// Check if token is expired
const isExpired = tokenRefreshService.isTokenExpired(accessToken);

// Get valid token (refresh if needed)
const validToken = await tokenRefreshService.getValidAccessToken();

// Manual refresh
const newToken = await tokenRefreshService.refreshAccessToken();
```

## Error Handling

### Handling API Errors

```typescript
import { useLoginMutation } from '@/store';
import { SerializedError } from '@reduxjs/toolkit';
import { FetchBaseQueryError } from '@reduxjs/toolkit/query';

function LoginScreen() {
  const [login, { error }] = useLoginMutation();

  const getErrorMessage = (error: FetchBaseQueryError | SerializedError | undefined) => {
    if (!error) return null;

    // Handle FetchBaseQueryError
    if ('status' in error) {
      if (error.status === 401) {
        return 'Invalid email or password';
      }
      if (error.status === 400) {
        return error.data?.message || 'Invalid input';
      }
      if (error.status === 500) {
        return 'Server error. Please try again later.';
      }
      return 'An error occurred';
    }

    // Handle SerializedError
    return error.message || 'An error occurred';
  };

  return (
    <View>
      {error && (
        <Text style={{ color: 'red' }}>
          {getErrorMessage(error)}
        </Text>
      )}
    </View>
  );
}
```

### Network Error Handling

```typescript
import { useLoginMutation } from '@/store';

function LoginScreen() {
  const [login, { error, isError }] = useLoginMutation();

  const handleLogin = async () => {
    try {
      await login({ email, password }).unwrap();
    } catch (err) {
      // Check for network errors
      if (err.status === 'FETCH_ERROR') {
        Alert.alert(
          'Network Error',
          'Please check your internet connection and try again.'
        );
      } else {
        Alert.alert('Error', 'Login failed. Please try again.');
      }
    }
  };

  // ...
}
```

### Global Error Handling

```typescript
// utils/errorHandler.ts
import { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { SerializedError } from '@reduxjs/toolkit';

export const handleApiError = (
  error: FetchBaseQueryError | SerializedError | undefined
): string => {
  if (!error) return 'An unknown error occurred';

  if ('status' in error) {
    switch (error.status) {
      case 400:
        return error.data?.message || 'Invalid request';
      case 401:
        return 'Authentication failed';
      case 403:
        return 'Access denied';
      case 404:
        return 'Resource not found';
      case 500:
        return 'Server error';
      case 'FETCH_ERROR':
        return 'Network error. Please check your connection.';
      case 'PARSING_ERROR':
        return 'Invalid response from server';
      case 'TIMEOUT_ERROR':
        return 'Request timeout. Please try again.';
      default:
        return 'An error occurred';
    }
  }

  return error.message || 'An error occurred';
};

// Usage in component
import { handleApiError } from '@/utils/errorHandler';

const errorMessage = handleApiError(error);
```

## Advanced Patterns

### Optimistic Updates

```typescript
// Example for future vehicle API
const [updateVehicle] = useUpdateVehicleMutation();

const handleUpdate = async (vehicleId, updates) => {
  try {
    await updateVehicle({
      id: vehicleId,
      ...updates,
    }).unwrap();
  } catch (err) {
    // Optimistic update will be rolled back automatically
    console.error('Update failed:', err);
  }
};
```

### Polling for Updates

```typescript
// Poll for payment status every 3 seconds
const { data: payment } = useGetPaymentQuery(paymentId, {
  pollingInterval: 3000,
  skip: !paymentId || payment?.status === 'PAYE',
});
```

### Conditional Queries

```typescript
// Only fetch if user is authenticated
const isAuthenticated = useAppSelector(selectIsAuthenticated);

const { data: user } = useGetCurrentUserQuery(undefined, {
  skip: !isAuthenticated,
});
```

### Prefetching Data

```typescript
import { useEffect } from 'react';
import { useAppDispatch } from '@/store/hooks';
import { vehicleApi } from '@/store/api/vehicleApi';

function DashboardScreen() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    // Prefetch vehicles when dashboard loads
    dispatch(vehicleApi.util.prefetch('getVehicles', undefined, { force: true }));
  }, [dispatch]);

  // ...
}
```

## Best Practices

1. **Always use typed hooks**: `useAppDispatch` and `useAppSelector`
2. **Use RTK Query hooks**: Prefer `useLoginMutation()` over manual API calls
3. **Handle loading states**: Always show loading indicators
4. **Handle errors gracefully**: Provide clear error messages to users
5. **Use selectors**: Create reusable selectors for complex state
6. **Avoid prop drilling**: Use Redux for global state, not props
7. **Keep components pure**: Avoid side effects in render
8. **Use unwrap()**: For better error handling with try/catch
9. **Invalidate tags**: Use RTK Query tags for cache invalidation
10. **Test with Redux**: Always wrap test components with Provider

## Common Pitfalls

1. **Don't dispatch in render**: Use useEffect or event handlers
2. **Don't mutate state directly**: Redux Toolkit uses Immer, but be careful
3. **Don't store derived state**: Use selectors instead
4. **Don't ignore loading states**: Always handle isLoading
5. **Don't ignore errors**: Always handle error states
6. **Don't over-persist**: Only persist essential state
7. **Don't skip error boundaries**: Wrap app with error boundary
8. **Don't forget to cleanup**: Unsubscribe from queries when needed
