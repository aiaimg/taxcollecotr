import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import { STORAGE_KEYS } from '../constants/app.constants';
import { Agent } from '../types/auth.types';
import { ScanRecord } from '../types/scanner.types';

class StorageService {
  // Secure storage for sensitive data
  async setAuthToken(token: string): Promise<void> {
    try {
      if (Platform.OS === 'web') {
        await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
      } else {
        await SecureStore.setItemAsync(STORAGE_KEYS.AUTH_TOKEN, token);
      }
    } catch (error) {
      console.error('Error storing auth token:', error);
      throw error;
    }
  }

  async getAuthToken(): Promise<string | null> {
    try {
      if (Platform.OS === 'web') {
        return await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      }
      return await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKEN);
    } catch (error) {
      console.error('Error retrieving auth token:', error);
      return null;
    }
  }

  async setRefreshToken(token: string): Promise<void> {
    try {
      if (Platform.OS === 'web') {
        await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, token);
      } else {
        await SecureStore.setItemAsync(STORAGE_KEYS.REFRESH_TOKEN, token);
      }
    } catch (error) {
      console.error('Error storing refresh token:', error);
      throw error;
    }
  }

  async getRefreshToken(): Promise<string | null> {
    try {
      if (Platform.OS === 'web') {
        return await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
      }
      return await SecureStore.getItemAsync(STORAGE_KEYS.REFRESH_TOKEN);
    } catch (error) {
      console.error('Error retrieving refresh token:', error);
      return null;
    }
  }

  // Regular storage for non-sensitive data
  async setAgentProfile(agent: Agent): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.AGENT_PROFILE, JSON.stringify(agent));
    } catch (error) {
      console.error('Error storing agent profile:', error);
      throw error;
    }
  }

  async getAgentProfile(): Promise<Agent | null> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.AGENT_PROFILE);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error retrieving agent profile:', error);
      return null;
    }
  }

  async setScanHistory(scans: ScanRecord[]): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.SCAN_HISTORY, JSON.stringify(scans));
    } catch (error) {
      console.error('Error storing scan history:', error);
      throw error;
    }
  }

  async getScanHistory(): Promise<ScanRecord[]> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.SCAN_HISTORY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error retrieving scan history:', error);
      return [];
    }
  }

  async addScanToHistory(scan: ScanRecord): Promise<void> {
    try {
      const history = await this.getScanHistory();
      const updatedHistory = [scan, ...history].slice(0, 100); // Keep last 100 scans
      await this.setScanHistory(updatedHistory);
    } catch (error) {
      console.error('Error adding scan to history:', error);
      throw error;
    }
  }

  async setPaymentHistory(payments: any[]): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.PAYMENT_HISTORY, JSON.stringify(payments));
    } catch (error) {
      console.error('Error storing payment history:', error);
      throw error;
    }
  }

  async getPaymentHistory(): Promise<any[]> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.PAYMENT_HISTORY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error retrieving payment history:', error);
      return [];
    }
  }

  async setOfflineQueue(queue: any[]): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.OFFLINE_QUEUE, JSON.stringify(queue));
    } catch (error) {
      console.error('Error storing offline queue:', error);
      throw error;
    }
  }

  async getOfflineQueue(): Promise<any[]> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_QUEUE);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error retrieving offline queue:', error);
      return [];
    }
  }

  async addToOfflineQueue(item: any): Promise<void> {
    try {
      const queue = await this.getOfflineQueue();
      queue.push(item);
      await this.setOfflineQueue(queue);
    } catch (error) {
      console.error('Error adding to offline queue:', error);
      throw error;
    }
  }

  async removeFromOfflineQueue(itemId: string): Promise<void> {
    try {
      const queue = await this.getOfflineQueue();
      const updatedQueue = queue.filter(item => item.id !== itemId);
      await this.setOfflineQueue(updatedQueue);
    } catch (error) {
      console.error('Error removing from offline queue:', error);
      throw error;
    }
  }

  async setAppSettings(settings: any): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.APP_SETTINGS, JSON.stringify(settings));
    } catch (error) {
      console.error('Error storing app settings:', error);
      throw error;
    }
  }

  async getAppSettings(): Promise<any> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.APP_SETTINGS);
      return data ? JSON.parse(data) : {};
    } catch (error) {
      console.error('Error retrieving app settings:', error);
      return {};
    }
  }

  async setLastSync(timestamp: Date): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.LAST_SYNC, timestamp.toISOString());
    } catch (error) {
      console.error('Error storing last sync timestamp:', error);
      throw error;
    }
  }

  async getLastSync(): Promise<Date | null> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.LAST_SYNC);
      return data ? new Date(data) : null;
    } catch (error) {
      console.error('Error retrieving last sync timestamp:', error);
      return null;
    }
  }

  // Clear all data
  async clearAllData(): Promise<void> {
    try {
      // Clear secure storage
      await SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKEN);
      await SecureStore.deleteItemAsync(STORAGE_KEYS.REFRESH_TOKEN);
      
      // Clear regular storage
      const keys = Object.values(STORAGE_KEYS).filter(
        key => key !== STORAGE_KEYS.AUTH_TOKEN && key !== STORAGE_KEYS.REFRESH_TOKEN
      );
      
      await AsyncStorage.multiRemove(keys);
    } catch (error) {
      console.error('Error clearing all data:', error);
      throw error;
    }
  }

  // Clear auth data only
  async clearAuthData(): Promise<void> {
    try {
      if (Platform.OS === 'web') {
        await AsyncStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        await AsyncStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      } else {
        await SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKEN);
        await SecureStore.deleteItemAsync(STORAGE_KEYS.REFRESH_TOKEN);
      }
      await AsyncStorage.removeItem(STORAGE_KEYS.AGENT_PROFILE);
    } catch (error) {
      console.error('Error clearing auth data:', error);
      throw error;
    }
  }
}

export const storageService = new StorageService();