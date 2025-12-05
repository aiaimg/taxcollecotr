/**
 * Network Status Hook - Manages network status and sync state
 * Integrates offline service with Redux store
 */

import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { PendingAction } from '../services/offlineService';
import {
  setNetworkStatus,
  setSyncing,
  setLastSync,
  setPendingActions,
  selectIsOnline,
  selectIsOffline,
  selectIsSyncing,
  selectLastSync,
  selectPendingActions,
  selectPendingActionsCount,
  selectFormattedLastSync,
} from '../store/slices/offlineSlice';
import offlineService from '../services/offlineService';
import { Vehicle } from '../types/models';
import { PaymentReceipt } from '../types/tax';

export const useNetworkStatus = () => {
  const dispatch = useAppDispatch();
  const isOnline = useAppSelector(selectIsOnline);
  const isOffline = useAppSelector(selectIsOffline);
  const isSyncing = useAppSelector(selectIsSyncing);
  const lastSync = useAppSelector(selectLastSync);
  const formattedLastSync = useAppSelector(selectFormattedLastSync);
  const pendingActions = useAppSelector(selectPendingActions);
  const pendingActionsCount = useAppSelector(selectPendingActionsCount);

  useEffect(() => {
    // Initialize offline service and set up listeners
    const initializeOfflineService = async () => {
      try {
        await offlineService.initialize();
        
        // Set initial network status
        const networkState = offlineService.getNetworkState();
        dispatch(setNetworkStatus({
          isOnline: offlineService.isOnline(),
          networkType: networkState?.type || null,
          networkDetails: networkState?.details || null,
        }));

        // Set initial last sync
        const lastSyncTimestamp = await offlineService.getLastSync();
        dispatch(setLastSync(lastSyncTimestamp));

        // Set initial pending actions
        const actions = await offlineService.getPendingActions();
        dispatch(setPendingActions(actions));
      } catch (error) {
        console.error('Error initializing offline service:', error);
      }
    };

    initializeOfflineService();

    // Subscribe to network status changes
    const unsubscribeNetwork = offlineService.subscribeToNetworkStatus((isOnline) => {
      const networkState = offlineService.getNetworkState();
      dispatch(setNetworkStatus({
        isOnline,
        networkType: networkState?.type || null,
        networkDetails: networkState?.details || null,
      }));
    });

    // Subscribe to sync events
    const unsubscribeSync = offlineService.subscribeToSync((isSyncing) => {
      dispatch(setSyncing(isSyncing));
      
      // Update last sync when sync completes
      if (!isSyncing) {
        offlineService.getLastSync().then(lastSyncTimestamp => {
          dispatch(setLastSync(lastSyncTimestamp));
        });
        
        // Update pending actions
        offlineService.getPendingActions().then(actions => {
          dispatch(setPendingActions(actions));
        });
      }
    });

    return () => {
      unsubscribeNetwork();
      unsubscribeSync();
    };
  }, [dispatch]);

  // Network status methods
  const getNetworkStatus = () => ({
    isOnline,
    isOffline,
    isSyncing,
    lastSync,
    formattedLastSync,
    pendingActions,
    pendingActionsCount,
  });

  const triggerSync = async () => {
    try {
      await offlineService.triggerSync();
    } catch (error) {
      console.error('Error triggering sync:', error);
      throw error;
    }
  };

  // Cache methods
  const cacheVehicles = async (vehicles: Vehicle[]) => {
    try {
      await offlineService.cacheVehicles(vehicles);
    } catch (error) {
      console.error('Error caching vehicles:', error);
      throw error;
    }
  };

  const cachePayments = async (payments: PaymentReceipt[]) => {
    try {
      await offlineService.cachePayments(payments);
    } catch (error) {
      console.error('Error caching payments:', error);
      throw error;
    }
  };

  const getCachedVehicles = async () => {
    try {
      return await offlineService.getCachedVehicles();
    } catch (error) {
      console.error('Error getting cached vehicles:', error);
      return [];
    }
  };

  const getCachedPayments = async () => {
    try {
      return await offlineService.getCachedPayments();
    } catch (error) {
      console.error('Error getting cached payments:', error);
      return [];
    }
  };

  // Pending actions methods
  const addPendingAction = async (action: Omit<PendingAction, 'id' | 'timestamp' | 'retryCount'>) => {
    try {
      await offlineService.addPendingAction(action);
      
      // Update pending actions in store
      const actions = await offlineService.getPendingActions();
      dispatch(setPendingActions(actions));
    } catch (error) {
      console.error('Error adding pending action:', error);
      throw error;
    }
  };

  const removePendingAction = async (actionId: string) => {
    try {
      await offlineService.removePendingAction(actionId);
      
      // Update pending actions in store
      const actions = await offlineService.getPendingActions();
      dispatch(setPendingActions(actions));
    } catch (error) {
      console.error('Error removing pending action:', error);
      throw error;
    }
  };

  const clearPendingActions = async () => {
    try {
      await offlineService.clearPendingActions();
      dispatch(setPendingActions([]));
    } catch (error) {
      console.error('Error clearing pending actions:', error);
      throw error;
    }
  };

  return {
    // Network status
    isOnline,
    isOffline,
    isSyncing,
    lastSync,
    formattedLastSync,
    pendingActions,
    pendingActionsCount,
    getNetworkStatus,
    
    // Sync methods
    triggerSync,
    
    // Cache methods
    cacheVehicles,
    cachePayments,
    getCachedVehicles,
    getCachedPayments,
    
    // Pending actions methods
    addPendingAction,
    removePendingAction,
    clearPendingActions,
  };
};

export default useNetworkStatus;