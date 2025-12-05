import { Camera } from 'expo-camera';
import * as Location from 'expo-location';
import { Platform, Linking } from 'react-native';

export class PermissionService {
  static async requestCameraPermission(): Promise<boolean> {
    try {
      const { status } = await Camera.requestCameraPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error requesting camera permission:', error);
      return false;
    }
  }

  static async requestLocationPermission(): Promise<boolean> {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error requesting location permission:', error);
      return false;
    }
  }

  static async checkCameraPermission(): Promise<boolean> {
    try {
      const { status } = await Camera.getCameraPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error checking camera permission:', error);
      return false;
    }
  }

  static async checkLocationPermission(): Promise<boolean> {
    try {
      const { status } = await Location.getForegroundPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error checking location permission:', error);
      return false;
    }
  }

  static async getCurrentLocation(): Promise<{
    latitude: number;
    longitude: number;
    accuracy?: number;
  } | null> {
    try {
      const hasPermission = await this.checkLocationPermission();
      if (!hasPermission) {
        const granted = await this.requestLocationPermission();
        if (!granted) {
          return null;
        }
      }

      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      return {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        // Expo Location can return null for accuracy; map null to undefined
        accuracy: location.coords.accuracy ?? undefined,
      };
    } catch (error) {
      console.error('Error getting current location:', error);
      return null;
    }
  }

  static async requestAllPermissions(): Promise<{
    camera: boolean;
    location: boolean;
  }> {
    const [cameraPermission, locationPermission] = await Promise.all([
      this.requestCameraPermission(),
      this.requestLocationPermission(),
    ]);

    return {
      camera: cameraPermission,
      location: locationPermission,
    };
  }

  static async checkAllPermissions(): Promise<{
    camera: boolean;
    location: boolean;
  }> {
    const [cameraPermission, locationPermission] = await Promise.all([
      this.checkCameraPermission(),
      this.checkLocationPermission(),
    ]);

    return {
      camera: cameraPermission,
      location: locationPermission,
    };
  }

  static getPermissionErrorMessage(permission: 'camera' | 'location'): string {
    switch (permission) {
      case 'camera':
        return 'Camera permission is required to scan codes. Please enable it in your device settings.';
      case 'location':
        return 'Location permission is required for accurate scan records. Please enable it in your device settings.';
      default:
        return 'Permission is required for this feature.';
    }
  }

  static async openSettings(): Promise<void> {
    if (Platform.OS === 'ios') {
      // For iOS, we can't directly open settings, but we can guide the user
      throw new Error('Please open Settings app and enable the required permissions.');
    } else {
      // For Android, we can try to open settings
      try {
        await Linking.openSettings();
      } catch (error) {
        throw new Error('Unable to open settings. Please manually enable permissions in your device settings.');
      }
    }
  }
}