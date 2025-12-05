# Redux Store Documentation

This directory contains the Redux store configuration, slices, and RTK Query API definitions for the Tax Collector Citizen Mobile App.

## Structure

```
store/
├── api/              # RTK Query API definitions
│   └── authApi.ts    # Authentication API endpoints
├── slices/           # Redux slices
│   └── authSlice.ts  # Authentication state slice
├── hooks.ts          # Typed Redux hooks
├── store.ts          # Store configuration with Redux Persist
├── index.ts          # Public exports
└── README.md         # This file
```

## Features

### 1. Redux Toolkit

We use Redux Toolkit for state management, which provides:
- Simplified store configuration
- Immutable state updates with Immer
- Built-in thunk middleware
- DevTools integration

### 2. RTK Query

RTK Query is used for API calls and caching:
- Automatic request deduplication
- Cache management
- Optimistic updates
- Automatic refetching

### 3. Redux Persist

Redux Persist is configured to:
- Persist auth state to AsyncStorage
- Restore session on app restart
- Exclude RTK Query cache from persistence

### 4. Automatic Token Refresh

The auth API includes automatic token refresh:
- Intercepts 401 errors
- Automatically refreshes access token
- Retries failed requests with new token
- Logs out user if refresh fails

## Usage

### Typed Hooks

Always use the typed hooks instead of plain Redux hooks:

```typescript
import { useAppDispatch, useAppSelector } from '@/store/hooks';

// In component
const dispatch = useAppDispatch();
const user = useAppSelector(selectCurrentUser);
```

### Auth Slice

The auth slice manages authentication state:

```typescript
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { setCredentials, logout, selectIsAuthenticated } from '@/store';

// In component
const dispatch = useAppDispatch();
const isAuthenticated = useAppSelector(selectIsAuthenticated);

// Login
dispatch(setCredentials({ user, tokens }));

// Logout
dispatch(logout());
```

### Auth API

Use RTK Query hooks for authentication:

```typescript
import { useLoginMutation, useRegisterMutation } from '@/store';

// In component
const [login, { isLoading, error }] = useLoginMutation();

const handleLogin = async () => {
  try {
    const result = await login({ email, password }).unwrap();
    // Success - tokens and user are automatically stored
  } catch (error) {
    // Handle error
  }
};
```

### Available Auth Hooks

- `useLoginMutation()` - Login user
- `useRegisterMutation()` - Register new user
- `useLogoutMutation()` - Logout user
- `useRefreshTokenMutation()` - Manually refresh token
- `useGetCurrentUserQuery()` - Get current user profile
- `useVerifyEmailMutation()` - Verify email address
- `useRequestPasswordResetMutation()` - Request password reset
- `useConfirmPasswordResetMutation()` - Confirm password reset

## State Structure

### Auth State

```typescript
interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

### Root State

```typescript
interface RootState {
  auth: AuthState;
  authApi: RTKQueryState;
  // More slices will be added as features are implemented
}
```

## Token Refresh Flow

1. API request returns 401 (Unauthorized)
2. Auth API intercepts the error
3. Attempts to refresh access token using refresh token
4. If successful:
   - Stores new access token
   - Updates Redux state
   - Retries original request
5. If failed:
   - Clears all tokens
   - Dispatches logout action
   - Redirects to login screen

## Persistence

The auth state is persisted to AsyncStorage and restored on app restart:

```typescript
// Persisted data
{
  auth: {
    user: User,
    tokens: AuthTokens,
    isAuthenticated: true
  }
}
```

RTK Query cache is NOT persisted to avoid stale data.

## Security Considerations

1. **Secure Storage**: Tokens are stored in Expo SecureStore (Keychain/Keystore)
2. **Token Expiry**: Access tokens expire after 60 minutes
3. **Refresh Tokens**: Refresh tokens expire after 7 days
4. **Automatic Logout**: User is logged out if refresh fails
5. **HTTPS Only**: All API calls use HTTPS in production

## Adding New API Endpoints

To add new RTK Query APIs:

1. Create new API file in `api/` directory
2. Define endpoints using `createApi`
3. Add reducer to store configuration
4. Add middleware to store configuration
5. Export hooks from `index.ts`

Example:

```typescript
// api/vehicleApi.ts
export const vehicleApi = createApi({
  reducerPath: 'vehicleApi',
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    getVehicles: builder.query<Vehicle[], void>({
      query: () => '/api/v1/vehicles/',
    }),
  }),
});

// store.ts
import { vehicleApi } from './api/vehicleApi';

const rootReducer = combineReducers({
  // ...
  [vehicleApi.reducerPath]: vehicleApi.reducer,
});

// middleware
.concat(vehicleApi.middleware)
```

## Testing

When testing components that use Redux:

```typescript
import { Provider } from 'react-redux';
import { store } from '@/store';

// Wrap component with Provider
<Provider store={store}>
  <YourComponent />
</Provider>
```

## Debugging

Redux DevTools are automatically enabled in development mode. You can inspect:
- Current state
- Dispatched actions
- State changes over time
- API requests and responses

## Best Practices

1. **Use typed hooks**: Always use `useAppDispatch` and `useAppSelector`
2. **Use RTK Query**: Prefer RTK Query over manual API calls
3. **Avoid direct state mutation**: Redux Toolkit uses Immer, but still write immutable code
4. **Use selectors**: Create reusable selectors for complex state derivations
5. **Handle loading states**: Always handle loading and error states in components
6. **Invalidate tags**: Use RTK Query tags for automatic cache invalidation

## Future Enhancements

- Add vehicle slice and API
- Add payment slice and API
- Add notification slice and API
- Add settings slice
- Add offline queue for failed requests
- Add optimistic updates for better UX
