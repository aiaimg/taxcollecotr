import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { User, AuthTokens } from '../../types/models';

/**
 * Auth State Interface
 */
export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  biometricEnabled: boolean;
}

/**
 * Initial State
 */
const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  biometricEnabled: false,
};

/**
 * Auth Slice
 * Manages authentication state including user, tokens, and auth status
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Set credentials after successful login/register
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; tokens: AuthTokens }>
    ) => {
      state.user = action.payload.user;
      state.tokens = action.payload.tokens;
      state.isAuthenticated = true;
      state.error = null;
    },

    // Update access token after refresh
    setAccessToken: (state, action: PayloadAction<string>) => {
      if (state.tokens) {
        state.tokens.access = action.payload;
      }
    },

    // Update user data
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },

    // Set loading state
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    // Set error
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.isLoading = false;
    },

    // Clear error
    clearError: state => {
      state.error = null;
    },

    // Set biometric enabled state
    setBiometricEnabled: (state, action: PayloadAction<boolean>) => {
      state.biometricEnabled = action.payload;
    },

    // Logout - clear all auth state
    logout: state => {
      state.user = null;
      state.tokens = null;
      state.isAuthenticated = false;
      state.error = null;
      state.isLoading = false;
      state.biometricEnabled = false;
    },

    // Restore session from persisted state
    restoreSession: (
      state,
      action: PayloadAction<{ user: User; tokens: AuthTokens }>
    ) => {
      state.user = action.payload.user;
      state.tokens = action.payload.tokens;
      state.isAuthenticated = true;
    },
  },
});

// Export actions
export const {
  setCredentials,
  setAccessToken,
  setUser,
  setLoading,
  setError,
  clearError,
  setBiometricEnabled,
  logout,
  restoreSession,
} = authSlice.actions;

// Export selectors
export const selectCurrentUser = (state: { auth: AuthState }) => state.auth.user;
export const selectIsAuthenticated = (state: { auth: AuthState }) =>
  state.auth.isAuthenticated;
export const selectAuthTokens = (state: { auth: AuthState }) => state.auth.tokens;
export const selectAuthLoading = (state: { auth: AuthState }) => state.auth.isLoading;
export const selectAuthError = (state: { auth: AuthState }) => state.auth.error;
export const selectBiometricEnabled = (state: { auth: AuthState }) =>
  state.auth.biometricEnabled;

// Export reducer
export default authSlice.reducer;
