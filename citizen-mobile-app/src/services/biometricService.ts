import * as LocalAuthentication from 'expo-local-authentication';
import storageService, { StorageService } from './storageService';

/**
 * BiometricService - Handles biometric authentication
 * Supports Touch ID (iOS) and Fingerprint/Face Unlock (Android)
 */
class BiometricService {
  private readonly BIOMETRIC_ENABLED_KEY = StorageService.KEYS.BIOMETRIC_ENABLED;

  /**
   * Check if biometric authentication is available on the device
   * @returns Promise<boolean> - true if biometric hardware is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      if (!hasHardware) {
        return false;
      }

      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      return isEnrolled;
    } catch (error) {
      console.error('Error checking biometric availability:', error);
      return false;
    }
  }

  /**
   * Get the types of biometric authentication available
   * @returns Promise<LocalAuthentication.AuthenticationType[]>
   */
  async getSupportedTypes(): Promise<LocalAuthentication.AuthenticationType[]> {
    try {
      return await LocalAuthentication.supportedAuthenticationTypesAsync();
    } catch (error) {
      console.error('Error getting supported biometric types:', error);
      return [];
    }
  }

  /**
   * Get a human-readable name for the biometric type
   * @returns Promise<string> - e.g., "Touch ID", "Face ID", "Fingerprint"
   */
  async getBiometricTypeName(): Promise<string> {
    try {
      const types = await this.getSupportedTypes();
      
      if (types.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
        return 'Face ID';
      }
      
      if (types.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
        return 'Touch ID / Fingerprint';
      }
      
      if (types.includes(LocalAuthentication.AuthenticationType.IRIS)) {
        return 'Iris Recognition';
      }

      return 'Biometric Authentication';
    } catch (error) {
      console.error('Error getting biometric type name:', error);
      return 'Biometric Authentication';
    }
  }

  /**
   * Authenticate user using biometric authentication
   * @param promptMessage - Custom message to display in the authentication prompt
   * @returns Promise<boolean> - true if authentication successful
   */
  async authenticate(promptMessage?: string): Promise<boolean> {
    try {
      const isAvailable = await this.isAvailable();
      
      if (!isAvailable) {
        console.warn('Biometric authentication not available');
        return false;
      }

      const biometricTypeName = await this.getBiometricTypeName();
      const defaultMessage = `Authenticate with ${biometricTypeName}`;

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: promptMessage || defaultMessage,
        cancelLabel: 'Cancel',
        disableDeviceFallback: false, // Allow fallback to device passcode
        fallbackLabel: 'Use Passcode',
      });

      return result.success;
    } catch (error) {
      console.error('Biometric authentication error:', error);
      return false;
    }
  }

  /**
   * Enable biometric authentication for the user
   * Stores the preference in secure storage
   */
  async enableBiometric(): Promise<void> {
    try {
      const isAvailable = await this.isAvailable();
      
      if (!isAvailable) {
        throw new Error('Biometric authentication is not available on this device');
      }

      // Test authentication before enabling
      const authenticated = await this.authenticate('Enable biometric login');
      
      if (!authenticated) {
        throw new Error('Biometric authentication failed');
      }

      // Store preference
      await storageService.secureSet(this.BIOMETRIC_ENABLED_KEY, 'true');
    } catch (error) {
      console.error('Error enabling biometric:', error);
      throw error;
    }
  }

  /**
   * Disable biometric authentication for the user
   * Removes the preference from secure storage
   */
  async disableBiometric(): Promise<void> {
    try {
      await storageService.secureDelete(this.BIOMETRIC_ENABLED_KEY);
    } catch (error) {
      console.error('Error disabling biometric:', error);
      throw error;
    }
  }

  /**
   * Check if biometric authentication is enabled for the user
   * @returns Promise<boolean> - true if enabled
   */
  async isBiometricEnabled(): Promise<boolean> {
    try {
      const enabled = await storageService.secureGet(this.BIOMETRIC_ENABLED_KEY);
      return enabled === 'true';
    } catch (error) {
      console.error('Error checking if biometric is enabled:', error);
      return false;
    }
  }

  /**
   * Check if biometric authentication should be offered to the user
   * Returns true if biometric is available but not yet enabled
   * @returns Promise<boolean>
   */
  async shouldPromptEnrollment(): Promise<boolean> {
    try {
      const isAvailable = await this.isAvailable();
      const isEnabled = await this.isBiometricEnabled();
      
      return isAvailable && !isEnabled;
    } catch (error) {
      console.error('Error checking enrollment prompt:', error);
      return false;
    }
  }

  /**
   * Perform biometric login
   * Authenticates the user and returns success status
   * @returns Promise<boolean> - true if login successful
   */
  async biometricLogin(): Promise<boolean> {
    try {
      const isEnabled = await this.isBiometricEnabled();
      
      if (!isEnabled) {
        console.warn('Biometric login not enabled');
        return false;
      }

      const authenticated = await this.authenticate('Login with biometric');
      return authenticated;
    } catch (error) {
      console.error('Biometric login error:', error);
      return false;
    }
  }

  /**
   * Get security level of biometric authentication
   * @returns Promise<LocalAuthentication.SecurityLevel>
   */
  async getSecurityLevel(): Promise<LocalAuthentication.SecurityLevel> {
    try {
      return await LocalAuthentication.getEnrolledLevelAsync();
    } catch (error) {
      console.error('Error getting security level:', error);
      return LocalAuthentication.SecurityLevel.NONE;
    }
  }
}

// Export singleton instance
export default new BiometricService();
