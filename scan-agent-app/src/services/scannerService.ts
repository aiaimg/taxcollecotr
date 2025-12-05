import { PermissionService } from '../utils/permissions';
import { ScanType, ScanResult, QRCodeResult, BarcodeResult, LicensePlateResult, ValidationResult, ScanRecord, Location } from '../types/scanner.types';
import { AgentType } from '../types/auth.types';
import { apiService } from './apiService';
import { storageService } from './storageService';
import { SCANNER_CONFIG, SCAN_VALIDATION_MESSAGES } from '../constants/scanner.constants';
import { validateQRCodeData, validateBarcodeData, validateLicensePlate } from '../utils/validators';
import NetInfo from '@react-native-community/netinfo';

class ScannerService {
  private offlineDatabase: Map<string, any> = new Map();

  constructor() {
    this.initializeOfflineDatabase();
  }

  private initializeOfflineDatabase(): void {
    // Initialize with some sample data for offline validation
    // In a real app, this would be synced from the server
    this.offlineDatabase.set('QR123456789', {
      valid: true,
      vehicleInfo: {
        plateNumber: 'XX1234XX',
        ownerName: 'John Doe',
        vehicleType: 'Car',
        brand: 'Toyota',
        model: 'Corolla',
        year: 2020,
        taxStatus: 'paid',
        insuranceStatus: 'valid',
        lastTaxPayment: new Date('2024-01-15'),
      },
    });

    this.offlineDatabase.set('BAR987654321', {
      valid: true,
      vehicleInfo: {
        plateNumber: 'AB5678CD',
        ownerName: 'Jane Smith',
        vehicleType: 'Truck',
        brand: 'Ford',
        model: 'F-150',
        year: 2019,
        taxStatus: 'pending',
        insuranceStatus: 'valid',
        amountDue: 150000,
      },
    });
  }

  async checkPermissions(): Promise<boolean> {
    const permissions = await PermissionService.checkAllPermissions();
    return permissions.camera && permissions.location;
  }

  async requestPermissions(): Promise<boolean> {
    const permissions = await PermissionService.requestAllPermissions();
    return permissions.camera && permissions.location;
  }

  async scanQRCode(data: string): Promise<QRCodeResult> {
    try {
      // Validate QR code data
      if (!validateQRCodeData(data)) {
        return {
          type: 'qr',
          data,
          format: 'qr',
          isValid: false,
          validationMessage: SCAN_VALIDATION_MESSAGES.INVALID_FORMAT,
        };
      }

      return {
        type: 'qr',
        data,
        format: 'qr',
        isValid: true,
      };
    } catch (error) {
      console.error('QR Code scan error:', error);
      return {
        type: 'qr',
        data,
        format: 'qr',
        isValid: false,
        validationMessage: 'Scan failed',
      };
    }
  }

  async scanBarcode(data: string): Promise<BarcodeResult> {
    try {
      // Validate barcode data
      if (!validateBarcodeData(data)) {
        return {
          type: 'barcode',
          data,
          format: 'code128',
          isValid: false,
          validationMessage: SCAN_VALIDATION_MESSAGES.INVALID_FORMAT,
        };
      }

      return {
        type: 'barcode',
        data,
        format: 'code128',
        isValid: true,
      };
    } catch (error) {
      console.error('Barcode scan error:', error);
      return {
        type: 'barcode',
        data,
        format: 'code128',
        isValid: false,
        validationMessage: 'Scan failed',
      };
    }
  }

  async scanLicensePlate(data: string): Promise<LicensePlateResult> {
    try {
      // Validate license plate format
      if (!validateLicensePlate(data)) {
        return {
          type: 'license_plate',
          plateNumber: data,
          confidence: 0,
          isValid: false,
          validationMessage: SCAN_VALIDATION_MESSAGES.INVALID_FORMAT,
        };
      }

      return {
        type: 'license_plate',
        plateNumber: data.toUpperCase(),
        confidence: 0.9,
        isValid: true,
      };
    } catch (error) {
      console.error('License plate scan error:', error);
      return {
        type: 'license_plate',
        plateNumber: data,
        confidence: 0,
        isValid: false,
        validationMessage: 'Scan failed',
      };
    }
  }

  async validateOnline(
    scanResult: ScanResult,
    agentId: string,
    location?: Location
  ): Promise<ValidationResult> {
    try {
      // Check if online
      if (!(await this.isOnline())) {
        return this.validateOffline(scanResult);
      }

      let endpoint: string;
      let requestData: any;

      if (scanResult.type === 'qr') {
        endpoint = '/agent-government/verify_qr_code/';
        requestData = {
          qr_data: scanResult.data,
          agent_id: agentId,
          agent_type: 'agent_government',
          location: location ? { latitude: location.latitude, longitude: location.longitude } : undefined,
        };
      } else if (scanResult.type === 'barcode') {
        endpoint = '/agent-government/verify_barcode/';
        requestData = {
          barcode_data: scanResult.data,
          agent_id: agentId,
          agent_type: 'agent_government',
          location: location ? { latitude: location.latitude, longitude: location.longitude } : undefined,
        };
      } else if (scanResult.type === 'license_plate') {
        endpoint = `/agent-government/vehicle_info/${scanResult.plateNumber}/`;
        requestData = {
          agent_id: agentId,
          location: location ? { latitude: location.latitude, longitude: location.longitude } : undefined,
        };
      } else {
        return {
          valid: false,
          reason: 'Unsupported scan type',
        };
      }

      const response = await apiService.post(endpoint, requestData);

      if (response.success && response.data) {
        return {
          valid: response.data.valid || response.data.vehicle_info !== undefined,
          vehicleInfo: response.data.vehicle_info,
          paymentStatus: response.data.payment_status,
          warnings: response.data.warnings,
          reason: response.data.message,
        };
      }

      return {
        valid: false,
        reason: response.error || SCAN_VALIDATION_MESSAGES.VALIDATION_FAILED,
      };
    } catch (error) {
      console.error('Online validation error:', error);
      // Fallback to offline validation
      return this.validateOffline(scanResult);
    }
  }

  async validateOffline(scanResult: ScanResult): Promise<ValidationResult> {
    try {
      // Use offline database for validation
      const key = scanResult.data || scanResult.plateNumber;
      const cachedData = this.offlineDatabase.get(key);

      if (cachedData) {
        return {
          valid: cachedData.valid,
          vehicleInfo: cachedData.vehicleInfo,
          paymentStatus: cachedData.paymentStatus,
          reason: SCAN_VALIDATION_MESSAGES.OFFLINE_VALIDATION,
        };
      }

      // Basic validation based on format
      if (scanResult.type === 'qr' && scanResult.isValid) {
        return {
          valid: true,
          reason: SCAN_VALIDATION_MESSAGES.OFFLINE_VALIDATION,
        };
      }

      if (scanResult.type === 'barcode' && scanResult.isValid) {
        return {
          valid: true,
          reason: SCAN_VALIDATION_MESSAGES.OFFLINE_VALIDATION,
        };
      }

      if (scanResult.type === 'license_plate' && scanResult.isValid) {
        return {
          valid: true,
          reason: SCAN_VALIDATION_MESSAGES.OFFLINE_VALIDATION,
        };
      }

      return {
        valid: false,
        reason: SCAN_VALIDATION_MESSAGES.NOT_FOUND,
      };
    } catch (error) {
      console.error('Offline validation error:', error);
      return {
        valid: false,
        reason: 'Validation failed',
      };
    }
  }

  async getCurrentLocation(): Promise<Location | null> {
    return await PermissionService.getCurrentLocation();
  }

  async isOnline(): Promise<boolean> {
    try {
      const state = await NetInfo.fetch();
      return state.isConnected && state.isInternetReachable !== false;
    } catch (error) {
      console.error('Error checking network status:', error);
      return false;
    }
  }

  async saveScanToLocal(scanRecord: ScanRecord): Promise<void> {
    try {
      await storageService.addScanToHistory(scanRecord);
    } catch (error) {
      console.error('Error saving scan to local storage:', error);
      throw error;
    }
  }

  async getLocalScanHistory(): Promise<ScanRecord[]> {
    try {
      return await storageService.getScanHistory();
    } catch (error) {
      console.error('Error getting local scan history:', error);
      return [];
    }
  }

  async syncOfflineScans(): Promise<void> {
    try {
      if (!(await this.isOnline())) {
        return;
      }

      const history = await this.getLocalScanHistory();
      const unsyncedScans = history.filter(scan => !scan.synced);

      for (const scan of unsyncedScans) {
        try {
          // Sync each scan to the server
          await this.syncScanToServer(scan);
          
          // Mark as synced
          scan.synced = true;
          await this.saveScanToLocal(scan);
        } catch (error) {
          console.error(`Error syncing scan ${scan.id}:`, error);
          scan.syncError = error instanceof Error ? error.message : 'Sync failed';
          await this.saveScanToLocal(scan);
        }
      }
    } catch (error) {
      console.error('Error syncing offline scans:', error);
    }
  }

  private async syncScanToServer(scan: ScanRecord): Promise<void> {
    // This would send the scan data to the server
    // Implementation depends on the server API
    console.log(`Syncing scan ${scan.id} to server`);
  }
}

export const scannerService = new ScannerService();