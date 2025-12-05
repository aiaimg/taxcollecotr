/**
 * Offline Slice - Manages offline mode state and network status
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { PendingAction } from '../../services/offlineService';

interface OfflineState {
  isOnline: boolean;
  isSyncing: boolean;
  lastSync: string | null;
  pendingActions: PendingAction[];
  networkType: string | null;
  networkDetails: any | null;
}

const initialState: OfflineState = {
  isOnline: true, // Assume online by default
  isSyncing: false,
  lastSync: null,
  pendingActions: [],
  networkType: null,
  networkDetails: null,
};

const offlineSlice = createSlice({
  name: 'offline',
  initialState,
  reducers: {
    // Network status actions
    setNetworkStatus: (state, action: PayloadAction<{ 
      isOnline: boolean; 
      networkType?: string | null;
      networkDetails?: any | null;
    }>) => {
      state.isOnline = action.payload.isOnline;
      state.networkType = action.payload.networkType || null;
      state.networkDetails = action.payload.networkDetails || null;
    },

    // Sync status actions
    setSyncing: (state, action: PayloadAction<boolean>) => {
      state.isSyncing = action.payload;
    },

    setLastSync: (state, action: PayloadAction<string | null>) => {
      state.lastSync = action.payload;
    },

    // Pending actions
    setPendingActions: (state, action: PayloadAction<PendingAction[]>) => {
      state.pendingActions = action.payload;
    },

    addPendingAction: (state, action: PayloadAction<PendingAction>) => {
      state.pendingActions.push(action.payload);
    },

    removePendingAction: (state, action: PayloadAction<string>) => {
      state.pendingActions = state.pendingActions.filter(
        pendingAction => pendingAction.id !== action.payload
      );
    },

    clearPendingActions: (state) => {
      state.pendingActions = [];
    },

    // Reset state
    resetOfflineState: (state) => {
      state.isOnline = true;
      state.isSyncing = false;
      state.lastSync = null;
      state.pendingActions = [];
      state.networkType = null;
      state.networkDetails = null;
    },
  },
});

// Export actions
export const {
  setNetworkStatus,
  setSyncing,
  setLastSync,
  setPendingActions,
  addPendingAction,
  removePendingAction,
  clearPendingActions,
  resetOfflineState,
} = offlineSlice.actions;

// Export reducer
export default offlineSlice.reducer;

// Selectors
export const selectIsOnline = (state: { offline: OfflineState }) => state.offline.isOnline;
export const selectIsOffline = (state: { offline: OfflineState }) => !state.offline.isOnline;
export const selectIsSyncing = (state: { offline: OfflineState }) => state.offline.isSyncing;
export const selectLastSync = (state: { offline: OfflineState }) => state.offline.lastSync;
export const selectPendingActions = (state: { offline: OfflineState }) => state.offline.pendingActions;
export const selectPendingActionsCount = (state: { offline: OfflineState }) => state.offline.pendingActions.length;
export const selectNetworkType = (state: { offline: OfflineState }) => state.offline.networkType;
export const selectNetworkDetails = (state: { offline: OfflineState }) => state.offline.networkDetails;

// Helper selector to format last sync time
export const selectFormattedLastSync = (state: { offline: OfflineState }) => {
  const lastSync = state.offline.lastSync;
  if (!lastSync) return null;
  
  try {
    const date = new Date(lastSync);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return "À l'instant";
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays}j`;
    
    return date.toLocaleDateString('fr-FR');
  } catch {
    return null;
  }
};