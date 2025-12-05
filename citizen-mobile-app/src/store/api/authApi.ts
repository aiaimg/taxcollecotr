import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { API_ENDPOINTS } from '../../api/endpoints';
import {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  User,
} from '../../types/models';
import { setCredentials, setAccessToken, logout } from '../slices/authSlice';
import storageService from '../../services/storageService';
import { StorageService } from '../../services/storageService';

/**
 * Base query with automatic token refresh
 */
const baseQuery = fetchBaseQuery({
  baseUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
  prepareHeaders: async headers => {
    // Get access token from secure storage
    const token = await storageService.secureGet(StorageService.KEYS.ACCESS_TOKEN);
    
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    
    headers.set('Content-Type', 'application/json');
    
    return headers;
  },
});

/**
 * Base query with automatic token refresh on 401 errors
 */
const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);

  // If we get a 401 error, try to refresh the token
  if (result.error && result.error.status === 401) {
    console.log('Access token expired, attempting refresh...');

    // Get refresh token
    const refreshToken = await storageService.secureGet(
      StorageService.KEYS.REFRESH_TOKEN
    );

    if (refreshToken) {
      // Try to refresh the token
      const refreshResult = await baseQuery(
        {
          url: API_ENDPOINTS.AUTH.REFRESH,
          method: 'POST',
          body: { refresh: refreshToken },
        },
        api,
        extraOptions
      );

      if (refreshResult.data) {
        // Store the new access token
        const { access } = refreshResult.data as { access: string };
        await storageService.secureSet(StorageService.KEYS.ACCESS_TOKEN, access);
        
        // Update the token in Redux state
        api.dispatch(setAccessToken(access));

        // Retry the original query with new token
        result = await baseQuery(args, api, extraOptions);
      } else {
        // Refresh failed, logout user
        console.log('Token refresh failed, logging out...');
        api.dispatch(logout());
        
        // Clear all stored data
        await storageService.secureDelete(StorageService.KEYS.ACCESS_TOKEN);
        await storageService.secureDelete(StorageService.KEYS.REFRESH_TOKEN);
        await storageService.secureDelete(StorageService.KEYS.USER_DATA);
      }
    } else {
      // No refresh token available, logout
      api.dispatch(logout());
    }
  }

  return result;
};

/**
 * Auth API
 * RTK Query API for authentication endpoints
 */
export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Auth', 'User'],
  endpoints: builder => ({
    // Login endpoint
    login: builder.mutation<AuthResponse, LoginCredentials>({
      query: credentials => ({
        url: API_ENDPOINTS.AUTH.LOGIN,
        method: 'POST',
        body: credentials,
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          
          // Store tokens and user in Redux
          dispatch(
            setCredentials({
              user: data.user,
              tokens: {
                access: data.access,
                refresh: data.refresh,
              },
            })
          );

          // Store tokens securely
          await storageService.secureSet(
            StorageService.KEYS.ACCESS_TOKEN,
            data.access
          );
          await storageService.secureSet(
            StorageService.KEYS.REFRESH_TOKEN,
            data.refresh
          );
          await storageService.secureSet(
            StorageService.KEYS.USER_DATA,
            JSON.stringify(data.user)
          );
        } catch (error) {
          console.error('Login failed:', error);
        }
      },
      invalidatesTags: ['Auth', 'User'],
    }),

    // Register endpoint
    register: builder.mutation<AuthResponse, RegisterData>({
      query: userData => ({
        url: API_ENDPOINTS.AUTH.REGISTER,
        method: 'POST',
        body: userData,
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          
          // Store tokens and user in Redux
          dispatch(
            setCredentials({
              user: data.user,
              tokens: {
                access: data.access,
                refresh: data.refresh,
              },
            })
          );

          // Store tokens securely
          await storageService.secureSet(
            StorageService.KEYS.ACCESS_TOKEN,
            data.access
          );
          await storageService.secureSet(
            StorageService.KEYS.REFRESH_TOKEN,
            data.refresh
          );
          await storageService.secureSet(
            StorageService.KEYS.USER_DATA,
            JSON.stringify(data.user)
          );
        } catch (error) {
          console.error('Registration failed:', error);
        }
      },
      invalidatesTags: ['Auth', 'User'],
    }),

    // Logout endpoint
    logout: builder.mutation<void, void>({
      query: () => ({
        url: API_ENDPOINTS.AUTH.LOGOUT,
        method: 'POST',
        body: {},
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
        } catch (error) {
          console.error('Logout API call failed:', error);
        } finally {
          // Always clear local state and storage, even if API call fails
          dispatch(logout());
          
          await storageService.secureDelete(StorageService.KEYS.ACCESS_TOKEN);
          await storageService.secureDelete(StorageService.KEYS.REFRESH_TOKEN);
          await storageService.secureDelete(StorageService.KEYS.USER_DATA);
        }
      },
      invalidatesTags: ['Auth', 'User'],
    }),

    // Refresh token endpoint
    refreshToken: builder.mutation<{ access: string }, { refresh: string }>({
      query: ({ refresh }) => ({
        url: API_ENDPOINTS.AUTH.REFRESH,
        method: 'POST',
        body: { refresh },
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          
          // Update access token in Redux
          dispatch(setAccessToken(data.access));

          // Store new access token
          await storageService.secureSet(
            StorageService.KEYS.ACCESS_TOKEN,
            data.access
          );
        } catch (error) {
          console.error('Token refresh failed:', error);
          // Logout on refresh failure
          dispatch(logout());
          await storageService.secureDelete(StorageService.KEYS.ACCESS_TOKEN);
          await storageService.secureDelete(StorageService.KEYS.REFRESH_TOKEN);
          await storageService.secureDelete(StorageService.KEYS.USER_DATA);
        }
      },
    }),

    // Get current user profile
    getCurrentUser: builder.query<User, void>({
      query: () => ({
        url: API_ENDPOINTS.USERS.ME,
        method: 'GET',
      }),
      providesTags: ['User'],
    }),

    // Verify email (if needed)
    verifyEmail: builder.mutation<{ message: string }, { token: string }>({
      query: ({ token }) => ({
        url: API_ENDPOINTS.AUTH.VERIFY_EMAIL,
        method: 'POST',
        body: { token },
      }),
    }),

    // Request password reset
    requestPasswordReset: builder.mutation<{ message: string }, { email: string }>({
      query: ({ email }) => ({
        url: API_ENDPOINTS.AUTH.PASSWORD_RESET,
        method: 'POST',
        body: { email },
      }),
    }),

    // Confirm password reset
    confirmPasswordReset: builder.mutation<
      { message: string },
      { token: string; password: string }
    >({
      query: ({ token, password }) => ({
        url: API_ENDPOINTS.AUTH.PASSWORD_RESET_CONFIRM,
        method: 'POST',
        body: { token, password },
      }),
    }),
  }),
});

// Export hooks for usage in components
export const {
  useLoginMutation,
  useRegisterMutation,
  useLogoutMutation,
  useRefreshTokenMutation,
  useGetCurrentUserQuery,
  useVerifyEmailMutation,
  useRequestPasswordResetMutation,
  useConfirmPasswordResetMutation,
} = authApi;
