import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import {
  persistStore,
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import slices
import authReducer from './slices/authSlice';
import vehicleReducer from './slices/vehicleSlice';
import paymentReducer from './slices/paymentSlice';
import notificationReducer from './slices/notificationSlice';
import offlineReducer from './slices/offlineSlice';
// import settingsReducer from './slices/settingsSlice';

// Import API slices
import { authApi } from './api/authApi';
import { vehicleApi } from './api/vehicleApi';
import { taxApi } from './api/taxApi';
// import { paymentApi } from './api/paymentApi';
// import { notificationApi } from './api/notificationApi';

/**
 * Redux Persist Configuration
 * Persists auth, vehicle, payment, and offline state to AsyncStorage for offline access
 */
const persistConfig = {
  key: 'root',
  version: 1,
  storage: AsyncStorage,
  whitelist: ['auth', 'vehicles', 'payment', 'offline'], // Persist auth, vehicles, payments, and offline state
  blacklist: [authApi.reducerPath, vehicleApi.reducerPath, taxApi.reducerPath], // Don't persist RTK Query cache
};

/**
 * Root Reducer
 * Combines all reducers including RTK Query API reducers
 */
const rootReducer = combineReducers({
  auth: authReducer,
  vehicles: vehicleReducer,
  payment: paymentReducer,
  notifications: notificationReducer,
  offline: offlineReducer,
  // settings: settingsReducer,
  [authApi.reducerPath]: authApi.reducer,
  [vehicleApi.reducerPath]: vehicleApi.reducer,
  [taxApi.reducerPath]: taxApi.reducer,
  // [paymentApi.reducerPath]: paymentApi.reducer,
  // [notificationApi.reducerPath]: notificationApi.reducer,
});

/**
 * Persisted Reducer
 * Wraps root reducer with persistence capabilities
 */
const persistedReducer = persistReducer(persistConfig, rootReducer);

/**
 * Redux Store Configuration
 * Configures store with persisted reducer and RTK Query middleware
 */
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }).concat([
      authApi.middleware,
      vehicleApi.middleware,
      taxApi.middleware,
    ] as const),
  // Add more API middleware as they are created
  // .concat(paymentApi.middleware)
  // .concat(notificationApi.middleware),
});

/**
 * Persistor
 * Manages persistence of the Redux store
 */
export const persistor = persistStore(store);

// Setup listeners for RTK Query (refetchOnFocus, refetchOnReconnect)
setupListeners(store.dispatch);

// Export types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
