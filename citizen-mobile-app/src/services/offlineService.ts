/**
 * OfflineService - Handles offline mode functionality and data synchronization
 * Provides network status detection, data caching, and sync capabilities
 */

import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import storageService, { StorageService } from './storageService';
import type { Vehicle } from '../types/models';
import type { PaymentReceipt } from '../types/tax';

export interface OfflineState {
  isOnline: boolean;
  lastSync: string | null;
  isSyncing: boolean;
  pendingActions: PendingAction[];
}

export interface PendingAction {
  id: string;
  type: 'CREATE_VEHICLE' | 'UPDATE_VEHICLE' | 'DELETE_VEHICLE' | 'INITIATE_PAYMENT';
  data: any;
  timestamp: string;
  retryCount: number;
}

export interface CachedData {
  vehicles: Vehicle[];
  payments: PaymentReceipt[];
  lastUpdated: string | null;
}

class OfflineService {
  private networkState: NetInfoState | null = null;
  private syncInProgress = false;
  private syncListeners: Array<(isOnline: boolean) => void> = [];
  private networkStatusListeners: Array<(isOnline: boolean) => void> = [];

  /**
   * Initialize the offline service
   * Sets up network status monitoring and sync listeners
   */
  async initialize(): Promise<void> {
    // Get initial network state
    this.networkState = await NetInfo.fetch();
    
    // Subscribe to network state changes
    NetInfo.addEventListener(this.handleNetworkStateChange.bind(this));
    
    // Load cached data
    await this.loadCachedData();
  }

  /**
   * Check if device is currently online
   */
  isOnline(): boolean {
    return this.networkState?.isConnected === true && this.networkState?.isInternetReachable === true;
  }

  /**
   * Check if device is offline
   */
  isOffline(): boolean {
    return !this.isOnline();
  }

  /**
   * Get current network state
   */
  getNetworkState(): NetInfoState | null {
    return this.networkState;
  }

  /**
   * Handle network state changes
   */
  private async handleNetworkStateChange(state: NetInfoState): Promise<void> {
    const wasOnline = this.isOnline();
    this.networkState = state;
    const isNowOnline = this.isOnline();

    // Notify network status listeners
    this.networkStatusListeners.forEach(listener => {
      try {
        listener(isNowOnline);
      } catch (error) {
        console.error('Error in network status listener:', error);
      }
    });

    // If we just came back online, trigger sync
    if (!wasOnline && isNowOnline) {
      console.log('Network connection restored - triggering sync');
      this.triggerSync();
    }
  }

  /**
   * Subscribe to network status changes
   */
  subscribeToNetworkStatus(listener: (isOnline: boolean) => void): () => void {
    this.networkStatusListeners.push(listener);
    
    // Return unsubscribe function
    return () => {
      const index = this.networkStatusListeners.indexOf(listener);
      if (index > -1) {
        this.networkStatusListeners.splice(index, 1);
      }
    };
  }

  /**
   * Add a pending action to be synced when online
   */
  async addPendingAction(action: Omit<PendingAction, 'id' | 'timestamp' | 'retryCount'>): Promise<void> {
    const pendingAction: PendingAction = {
      ...action,
      id: this.generateActionId(),
      timestamp: new Date().toISOString(),
      retryCount: 0,
    };

    try {
      const existingActions = await this.getPendingActions();
      existingActions.push(pendingAction);
      await storageService.set('pending_actions', existingActions);
      console.log('Added pending action:', pendingAction.type);
    } catch (error) {
      console.error('Error adding pending action:', error);
      throw error;
    }
  }

  /**
   * Get all pending actions
   */
  async getPendingActions(): Promise<PendingAction[]> {
    try {
      return await storageService.get<PendingAction[]>('pending_actions') || [];
    } catch (error) {
      console.error('Error getting pending actions:', error);
      return [];
    }
  }

  /**
   * Remove a pending action by ID
   */
  async removePendingAction(actionId: string): Promise<void> {
    try {
      const existingActions = await this.getPendingActions();
      const filteredActions = existingActions.filter(action => action.id !== actionId);
      await storageService.set('pending_actions', filteredActions);
      console.log('Removed pending action:', actionId);
    } catch (error) {
      console.error('Error removing pending action:', error);
      throw error;
    }
  }

  /**
   * Clear all pending actions
   */
  async clearPendingActions(): Promise<void> {
    try {
      await storageService.delete('pending_actions');
      console.log('Cleared all pending actions');
    } catch (error) {
      console.error('Error clearing pending actions:', error);
      throw error;
    }
  }

  /**
   * Cache vehicles data
   */
  async cacheVehicles(vehicles: Vehicle[]): Promise<void> {
    try {
      const cachedData = await this.getCachedData();
      cachedData.vehicles = vehicles;
      cachedData.lastUpdated = new Date().toISOString();
      
      await storageService.set('cached_data', cachedData);
      console.log('Cached vehicles:', vehicles.length);
    } catch (error) {
      console.error('Error caching vehicles:', error);
      throw error;
    }
  }

  /**
   * Cache payments data
   */
  async cachePayments(payments: PaymentReceipt[]): Promise<void> {
    try {
      const cachedData = await this.getCachedData();
      cachedData.payments = payments;
      cachedData.lastUpdated = new Date().toISOString();
      
      await storageService.set('cached_data', cachedData);
      console.log('Cached payments:', payments.length);
    } catch (error) {
      console.error('Error caching payments:', error);
      throw error;
    }
  }

  /**
   * Get cached data
   */
  async getCachedData(): Promise<CachedData> {
    try {
      const cachedData = await storageService.get<CachedData>('cached_data');
      return cachedData || {
        vehicles: [],
        payments: [],
        lastUpdated: null,
      };
    } catch (error) {
      console.error('Error getting cached data:', error);
      return {
        vehicles: [],
        payments: [],
        lastUpdated: null,
      };
    }
  }

  /**
   * Get cached vehicles
   */
  async getCachedVehicles(): Promise<Vehicle[]> {
    const cachedData = await this.getCachedData();
    return cachedData.vehicles;
  }

  /**
   * Get cached payments
   */
  async getCachedPayments(): Promise<PaymentReceipt[]> {
    const cachedData = await this.getCachedData();
    return cachedData.payments;
  }

  /**
   * Load cached data from storage
   */
  private async loadCachedData(): Promise<void> {
    try {
      const cachedData = await this.getCachedData();
      console.log('Loaded cached data:', {
        vehicles: cachedData.vehicles.length,
        payments: cachedData.payments.length,
        lastUpdated: cachedData.lastUpdated,
      });
    } catch (error) {
      console.error('Error loading cached data:', error);
    }
  }

  /**
   * Trigger data synchronization
   */
  async triggerSync(): Promise<void> {
    if (this.syncInProgress) {
      console.log('Sync already in progress, skipping...');
      return;
    }

    if (!this.isOnline()) {
      console.log('Cannot sync - device is offline');
      return;
    }

    this.syncInProgress = true;
    console.log('Starting data synchronization...');

    try {
      // Notify sync listeners
      this.syncListeners.forEach(listener => {
        try {
          listener(true);
        } catch (error) {
          console.error('Error in sync listener:', error);
        }
      });

      // Process pending actions
      await this.processPendingActions();

      // Update last sync timestamp
      const now = new Date().toISOString();
      await storageService.set('last_sync', now);

      console.log('Data synchronization completed successfully');
    } catch (error) {
      console.error('Error during data synchronization:', error);
      throw error;
    } finally {
      this.syncInProgress = false;
      
      // Notify sync completion
      this.syncListeners.forEach(listener => {
        try {
          listener(false);
        } catch (error) {
          console.error('Error in sync completion listener:', error);
        }
      });
    }
  }

  /**
   * Process pending actions
   */
  private async processPendingActions(): Promise<void> {
    const pendingActions = await this.getPendingActions();
    
    if (pendingActions.length === 0) {
      console.log('No pending actions to process');
      return;
    }

    console.log(`Processing ${pendingActions.length} pending actions...`);

    for (const action of pendingActions) {
      try {
        await this.processPendingAction(action);
        await this.removePendingAction(action.id);
        console.log(`Successfully processed action: ${action.type} (${action.id})`);
      } catch (error) {
        console.error(`Failed to process action: ${action.type} (${action.id})`, error);
        
        // Increment retry count
        action.retryCount++;
        
        // If max retries reached, log and remove
        if (action.retryCount >= 3) {
          console.error(`Max retries reached for action: ${action.type} (${action.id})`);
          await this.removePendingAction(action.id);
        } else {
          // Update retry count
          const existingActions = await this.getPendingActions();
          const actionIndex = existingActions.findIndex(a => a.id === action.id);
          if (actionIndex !== -1) {
            existingActions[actionIndex] = action;
            await storageService.set('pending_actions', existingActions);
          }
        }
      }
    }
  }

  /**
   * Process a single pending action
   */
  private async processPendingAction(action: PendingAction): Promise<void> {
    console.log('Processing action:', action.type, action.data);
    
    switch (action.type) {
      case 'CREATE_VEHICLE':
        await this.processCreateVehicleAction(action.data);
        break;
      case 'UPDATE_VEHICLE':
        await this.processUpdateVehicleAction(action.data);
        break;
      case 'DELETE_VEHICLE':
        await this.processDeleteVehicleAction(action.data);
        break;
      case 'INITIATE_PAYMENT':
        await this.processInitiatePaymentAction(action.data);
        break;
      default:
        console.warn('Unknown action type:', action.type);
        throw new Error(`Unknown action type: ${action.type}`);
    }
  }

  private async processCreateVehicleAction(data: any): Promise<void> {
    // This would integrate with vehicle service to create vehicle
    console.log('Processing CREATE_VEHICLE action:', data);
    // TODO: Implement actual vehicle creation using vehicle service
    // For now, we'll simulate success
    return Promise.resolve();
  }

  private async processUpdateVehicleAction(data: any): Promise<void> {
    // This would integrate with vehicle service to update vehicle
    console.log('Processing UPDATE_VEHICLE action:', data);
    // TODO: Implement actual vehicle update using vehicle service
    // For now, we'll simulate success
    return Promise.resolve();
  }

  private async processDeleteVehicleAction(data: any): Promise<void> {
    // This would integrate with vehicle service to delete vehicle
    console.log('Processing DELETE_VEHICLE action:', data);
    // TODO: Implement actual vehicle deletion using vehicle service
    // For now, we'll simulate success
    return Promise.resolve();
  }

  private async processInitiatePaymentAction(data: any): Promise<void> {
    // This would integrate with payment service to initiate payment
    console.log('Processing INITIATE_PAYMENT action:', data);
    // TODO: Implement actual payment initiation using payment service
    // For now, we'll simulate success
    return Promise.resolve();
  }

  /**
   * Get last sync timestamp
   */
  async getLastSync(): Promise<string | null> {
    try {
      return await storageService.get<string>('last_sync');
    } catch (error) {
      console.error('Error getting last sync:', error);
      return null;
    }
  }

  /**
   * Subscribe to sync events
   */
  subscribeToSync(listener: (isSyncing: boolean) => void): () => void {
    this.syncListeners.push(listener);
    
    // Return unsubscribe function
    return () => {
      const index = this.syncListeners.indexOf(listener);
      if (index > -1) {
        this.syncListeners.splice(index, 1);
      }
    };
  }

  /**
   * Check if sync is currently in progress
   */
  isSyncing(): boolean {
    return this.syncInProgress;
  }

  /**
   * Clear all cached data
   */
  async clearCache(): Promise<void> {
    try {
      await storageService.delete('cached_data');
      await storageService.delete('last_sync');
      console.log('Cleared all cached data');
    } catch (error) {
      console.error('Error clearing cache:', error);
      throw error;
    }
  }

  /**
   * Generate a unique action ID
   */
  private generateActionId(): string {
    return `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton instance
export default new OfflineService();