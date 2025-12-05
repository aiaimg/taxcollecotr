import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * StorageService - Handles secure and normal storage operations
 * Uses Expo SecureStore for sensitive data (tokens, credentials)
 * Uses AsyncStorage for non-sensitive data (cache, preferences)
 */
export class StorageService {
  // Storage keys
  static readonly KEYS = {
    // Secure storage (SecureStore)
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    USER_DATA: 'user_data',
    PREFERRED_LANGUAGE: 'preferred_language',
    BIOMETRIC_ENABLED: 'biometric_enabled',
    
    // Normal storage (AsyncStorage)
    VEHICLES_CACHE: 'vehicles_cache',
    PAYMENTS_CACHE: 'payments_cache',
    NOTIFICATIONS_CACHE: 'notifications_cache',
    LAST_SYNC: 'last_sync',
    THEME: 'theme',
  };

  /**
   * Secure Storage Methods (for sensitive data)
   */

  /**
   * Store data securely using SecureStore
   */
  async secureSet(key: string, value: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(key, value);
    } catch (error) {
      console.error(`Error storing secure data for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get data from SecureStore
   */
  async secureGet(key: string): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.error(`Error getting secure data for key ${key}:`, error);
      return null;
    }
  }

  /**
   * Delete data from SecureStore
   */
  async secureDelete(key: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch (error) {
      console.error(`Error deleting secure data for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Normal Storage Methods (for non-sensitive data)
   */

  /**
   * Store data in AsyncStorage
   */
  async set(key: string, value: any): Promise<void> {
    try {
      const jsonValue = JSON.stringify(value);
      await AsyncStorage.setItem(key, jsonValue);
    } catch (error) {
      console.error(`Error storing data for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get data from AsyncStorage
   */
  async get<T = any>(key: string): Promise<T | null> {
    try {
      const jsonValue = await AsyncStorage.getItem(key);
      return jsonValue != null ? JSON.parse(jsonValue) : null;
    } catch (error) {
      console.error(`Error getting data for key ${key}:`, error);
      return null;
    }
  }

  /**
   * Delete data from AsyncStorage
   */
  async delete(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error(`Error deleting data for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Clear all data from AsyncStorage
   */
  async clear(): Promise<void> {
    try {
      await AsyncStorage.clear();
    } catch (error) {
      console.error('Error clearing AsyncStorage:', error);
      throw error;
    }
  }

  /**
   * Clear all secure data
   */
  async clearSecure(): Promise<void> {
    try {
      await this.secureDelete(StorageService.KEYS.ACCESS_TOKEN);
      await this.secureDelete(StorageService.KEYS.REFRESH_TOKEN);
      await this.secureDelete(StorageService.KEYS.USER_DATA);
      await this.secureDelete(StorageService.KEYS.BIOMETRIC_ENABLED);
    } catch (error) {
      console.error('Error clearing secure storage:', error);
      throw error;
    }
  }

  /**
   * Clear all data (both secure and normal)
   */
  async clearAll(): Promise<void> {
    try {
      await this.clearSecure();
      await this.clear();
    } catch (error) {
      console.error('Error clearing all storage:', error);
      throw error;
    }
  }

  /**
   * Get multiple keys from AsyncStorage
   */
  async getMultiple(keys: string[]): Promise<Record<string, any>> {
    try {
      const values = await AsyncStorage.multiGet(keys);
      const result: Record<string, any> = {};
      
      values.forEach(([key, value]) => {
        if (value != null) {
          try {
            result[key] = JSON.parse(value);
          } catch {
            result[key] = value;
          }
        }
      });
      
      return result;
    } catch (error) {
      console.error('Error getting multiple keys:', error);
      return {};
    }
  }

  /**
   * Set multiple keys in AsyncStorage
   */
  async setMultiple(keyValuePairs: Array<[string, any]>): Promise<void> {
    try {
      const pairs: [string, string][] = keyValuePairs.map(([key, value]) => [
        key,
        JSON.stringify(value),
      ]);
      await AsyncStorage.multiSet(pairs);
    } catch (error) {
      console.error('Error setting multiple keys:', error);
      throw error;
    }
  }

  /**
   * Check if a key exists in AsyncStorage
   */
  async has(key: string): Promise<boolean> {
    try {
      const value = await AsyncStorage.getItem(key);
      return value !== null;
    } catch (error) {
      console.error(`Error checking key ${key}:`, error);
      return false;
    }
  }

  /**
   * Get all keys from AsyncStorage
   */
  async getAllKeys(): Promise<readonly string[]> {
    try {
      return await AsyncStorage.getAllKeys();
    } catch (error) {
      console.error('Error getting all keys:', error);
      return [];
    }
  }
}

// Export singleton instance
export default new StorageService();
