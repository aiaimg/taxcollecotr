import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ScanType, ScanRecord, ScanResult, ValidationResult, Location } from '../types/scanner.types';
import { scannerService } from '../services/scannerService';
import { t } from '../utils/translations';
import { useAuth } from './AuthContext';

interface ScannerContextType {
  isScanning: boolean;
  scanResult: ScanResult | null;
  scanHistory: ScanRecord[];
  lastScan: ScanRecord | null;
  startScanning: (type: ScanType) => Promise<void>;
  stopScanning: () => void;
  processScan: (data: string, type: ScanType) => Promise<ValidationResult>;
  saveScan: (result: ScanResult) => Promise<void>;
  clearScanResult: () => void;
  getScanHistory: () => Promise<ScanRecord[]>;
}

const ScannerContext = createContext<ScannerContextType | undefined>(undefined);

export const useScanner = (): ScannerContextType => {
  const context = useContext(ScannerContext);
  if (!context) {
    throw new Error('useScanner must be used within a ScannerProvider');
  }
  return context;
};

interface ScannerProviderProps {
  children: ReactNode;
}

export const ScannerProvider: React.FC<ScannerProviderProps> = ({ children }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanRecord[]>([]);
  const [lastScan, setLastScan] = useState<ScanRecord | null>(null);
  
  const { agent, agentType } = useAuth();

  const startScanning = async (type: ScanType): Promise<void> => {
    if (!agent || !agentType) {
      throw new Error(t('scanner.authRequired'));
    }

    // Check permissions based on agent type
    if (agentType === 'agent_government') {
      if (!['qr', 'barcode', 'license_plate'].includes(type)) {
        throw new Error(t('scanner.invalidScanTypeGovernment'));
      }
    } else {
      throw new Error(t('scanner.partnerCannotScan'));
    }

    setIsScanning(true);
    setScanResult(null);
  };

  const stopScanning = (): void => {
    setIsScanning(false);
  };

  const processScan = async (data: string, type: ScanType): Promise<ValidationResult> => {
    if (!agent || !agentType) {
      throw new Error(t('scanner.authRequired'));
    }

    try {
      // Get current location
      const location = await scannerService.getCurrentLocation();
      
      // Process the scan based on type
      let result: ScanResult;
      
      switch (type) {
        case 'qr':
          result = await scannerService.scanQRCode(data);
          break;
        case 'barcode':
          result = await scannerService.scanBarcode(data);
          break;
        case 'license_plate':
          result = await scannerService.scanLicensePlate(data);
          break;
        default:
          throw new Error(t('scanner.unsupportedScanType'));
      }

      setScanResult(result);

      // Validate against backend if online
      let validation: ValidationResult;
      
      if (await scannerService.isOnline()) {
        validation = await scannerService.validateOnline(result, agent.id, location);
      } else {
        // Use offline validation
        validation = await scannerService.validateOffline(result);
      }

      // Create scan record
      const scanRecord: ScanRecord = {
        id: generateScanId(),
        type,
        data,
        timestamp: new Date(),
        location: location || undefined,
        agentId: agent.id,
        agentType: agent.type,
        validated: validation.valid,
        validationStatus: validation.valid ? 'valid' : 'invalid',
        vehicleInfo: validation.vehicleInfo,
        paymentStatus: validation.paymentStatus,
        synced: false,
        syncError: validation.valid ? undefined : validation.reason,
      };

      // Save scan record
      await saveScanRecord(scanRecord);
      
      return validation;
    } catch (error) {
      console.error('Error processing scan:', error);
      throw error;
    } finally {
      setIsScanning(false);
    }
  };

  const saveScan = async (result: ScanResult): Promise<void> => {
    if (!agent || !agentType) {
      throw new Error('Authentication required');
    }

    // This method is used to save an existing scan result
    // Usually called after manual input or image processing
    const scanRecord: ScanRecord = {
      id: generateScanId(),
      type: result.type,
      data: result.data,
      timestamp: new Date(),
      agentId: agent.id,
      agentType: agent.type,
      validated: result.isValid,
      validationStatus: result.isValid ? 'valid' : 'invalid',
      vehicleInfo: 'vehicleInfo' in result ? result.vehicleInfo : undefined,
      synced: false,
    };

    await saveScanRecord(scanRecord);
  };

  const saveScanRecord = async (scanRecord: ScanRecord): Promise<void> => {
    try {
      // Save to local storage
      await scannerService.saveScanToLocal(scanRecord);
      
      // Update local state
      setLastScan(scanRecord);
      setScanHistory(prev => [scanRecord, ...prev.slice(0, 99)]); // Keep last 100 scans
    } catch (error) {
      console.error('Error saving scan record:', error);
      throw error;
    }
  };

  const clearScanResult = (): void => {
    setScanResult(null);
  };

  const getScanHistory = async (): Promise<ScanRecord[]> => {
    try {
      const history = await scannerService.getLocalScanHistory();
      setScanHistory(history);
      return history;
    } catch (error) {
      console.error('Error getting scan history:', error);
      return [];
    }
  };

  const generateScanId = (): string => {
    return `scan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const value: ScannerContextType = {
    isScanning,
    scanResult,
    scanHistory,
    lastScan,
    startScanning,
    stopScanning,
    processScan,
    saveScan,
    clearScanResult,
    getScanHistory,
  };

  return <ScannerContext.Provider value={value}>{children}</ScannerContext.Provider>;
};