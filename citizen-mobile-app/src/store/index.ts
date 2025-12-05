// Export store and persistor
export { store, persistor } from './store';
export type { RootState, AppDispatch } from './store';

// Export hooks
export { useAppDispatch, useAppSelector } from './hooks';

// Export auth slice
export {
  setCredentials,
  setAccessToken,
  setUser,
  setLoading,
  setError,
  clearError,
  logout,
  restoreSession,
  selectCurrentUser,
  selectIsAuthenticated,
  selectAuthTokens,
  selectAuthLoading,
  selectAuthError,
} from './slices/authSlice';

// Export auth API
export {
  authApi,
  useLoginMutation,
  useRegisterMutation,
  useLogoutMutation,
  useRefreshTokenMutation,
  useGetCurrentUserQuery,
  useVerifyEmailMutation,
  useRequestPasswordResetMutation,
  useConfirmPasswordResetMutation,
} from './api/authApi';

// Export tax API
export {
  taxApi,
  useCalculateTaxMutation,
  useInitiatePaymentMutation,
  useGetPaymentStatusQuery,
  useGetPaymentReceiptQuery,
  useGetPaymentHistoryQuery,
  useLazyGetPaymentStatusQuery,
  useLazyGetPaymentReceiptQuery,
  useLazyGetPaymentHistoryQuery,
} from './api/taxApi';

// Export payment slice
export {
  setCurrentCalculation,
  setPaymentId,
  setPaymentStatus,
  resetCurrentPayment,
  setPayments,
  addPayment,
  updatePayment,
  setFilters,
  clearFilters,
  setLoading as setPaymentLoading,
  setError as setPaymentError,
  selectCurrentCalculation,
  selectCurrentPayment,
  selectPayments,
  selectFilteredPayments,
  selectPaymentLoading,
  selectPaymentError,
  selectPaymentFilters,
} from './slices/paymentSlice';

// Export notification slice
export {
  addNotification,
  setNotifications,
  markAsRead,
  markAllAsRead,
  setUnreadCount,
  setLoading as setNotificationLoading,
  setError as setNotificationError,
  selectNotifications,
  selectUnreadCount,
  selectNotificationLoading,
  selectNotificationError,
} from './slices/notificationSlice';

// Export offline slice
export {
  setNetworkStatus,
  setSyncing,
  setLastSync,
  setPendingActions,
  addPendingAction,
  removePendingAction,
  clearPendingActions,
  resetOfflineState,
  selectIsOnline,
  selectIsOffline,
  selectIsSyncing,
  selectLastSync,
  selectPendingActions,
  selectPendingActionsCount,
  selectNetworkType,
  selectNetworkDetails,
  selectFormattedLastSync,
} from './slices/offlineSlice';
