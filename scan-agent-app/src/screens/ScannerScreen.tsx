import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Modal,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { CameraView } from 'expo-camera';
import { BarcodeScanningResult } from 'expo-camera';
import { useAuth } from '../context/AuthContext';
import { useScanner } from '../context/ScannerContext';
import { scannerService } from '../services/scannerService';
import { ScanResult, ScanType, ValidationResult } from '../types/scanner.types';
import { AgentType } from '../types/auth.types';
import { t } from '../utils/translations';

export default function ScannerScreen() {
  const { agent } = useAuth();
  const { startScanning, stopScanning, processScan, isScanning, scanResult } = useScanner();
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    (async () => {
      const granted = await scannerService.requestPermissions();
      setHasPermission(granted);
    })();
  }, []);

  const handleBarCodeScanned = async (result: BarcodeScanningResult) => {
    if (isProcessing || !agent) return;

    setIsProcessing(true);
    const derivedType: ScanType = result.type === 'qr' ? 'qr' : 'barcode';
    await startScanning(derivedType);

    try {
      const validation = await processScan(result.data, derivedType);
      setValidationResult(validation);
      setShowResult(true);
    } catch (error) {
      console.error('Scan processing error:', error);
      Alert.alert(t('scanner.scanErrorTitle'), t('scanner.scanErrorMessage'));
    } finally {
      setIsProcessing(false);
      stopScanning();
    }
  };

  const handleManualLicensePlate = async () => {
    if (!agent) return;

    Alert.prompt(
      t('scanner.enterPlateTitle'),
      t('scanner.enterPlateMessage'),
      [
        {
          text: t('scanner.cancel'),
          style: 'cancel',
        },
        {
          text: t('scanner.scan'),
          onPress: async (plateNumber?: string) => {
            const value = plateNumber?.trim();
            if (value) {
              setIsProcessing(true);
              await startScanning('license_plate');

              try {
                const validation = await processScan(value, 'license_plate');
                setValidationResult(validation);
                setShowResult(true);
              } catch (error) {
                console.error('Manual scan error:', error);
                Alert.alert(t('scanner.scanErrorTitle'), t('scanner.scanErrorMessage'));
              } finally {
                setIsProcessing(false);
                stopScanning();
              }
            }
          },
        },
      ],
      'plain-text'
    );
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>{t('scanner.requestingPermission')}</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>{t('scanner.noCameraAccess')}</Text>
        <TouchableOpacity
          style={styles.permissionButton}
          onPress={async () => {
            const granted = await scannerService.requestPermissions();
            setHasPermission(granted);
          }}
        >
          <Text style={styles.buttonText}>{t('scanner.grantPermission')}</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (agent?.type !== AgentType.GOVERNMENT) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>{t('scanner.govOnly')}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView
        style={styles.camera}
        onBarcodeScanned={isProcessing ? undefined : handleBarCodeScanned}
        barcodeScannerSettings={{
          barcodeTypes: ['qr', 'code128', 'code39', 'ean13', 'ean8', 'upc_a', 'upc_e'],
        }}
      >
        <View style={styles.overlay}>
          <View style={styles.header}>
            <Text style={styles.headerText}>{t('scanner.headerText')}</Text>
          </View>

          <View style={styles.scanArea}>
            <View style={styles.scanFrame}>
              <View style={styles.scanLine} />
            </View>
          </View>

          <View style={styles.footer}>
            <TouchableOpacity
              style={styles.manualButton}
              onPress={handleManualLicensePlate}
              disabled={isProcessing}
            >
              <Text style={styles.buttonText}>{t('scanner.manualPlate')}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </CameraView>

      {isProcessing && (
        <View style={styles.processingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.processingText}>{t('scanner.processing')}</Text>
        </View>
      )}

      <Modal
        visible={showResult}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowResult(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <ScrollView>
              <Text style={styles.modalTitle}>{t('scanner.resultTitle')}</Text>
              
              {scanResult && (
                <View>
                  <Text style={styles.resultText}>
                    {t('scanner.type')} {scanResult.type.toUpperCase()}
                  </Text>
                  <Text style={styles.resultText}>
                    {t('scanner.data')} {scanResult.type === 'license_plate' ? scanResult.plateNumber : scanResult.data}
                  </Text>
                  
                  {validationResult && (
                    <View>
                      <Text style={[
                        styles.validationText,
                        validationResult.valid ? styles.validText : styles.invalidText
                      ]}>
                        {validationResult.valid ? `✓ ${t('common.valid')}` : `✗ ${t('common.invalid')}`}
                      </Text>
                      
                      {validationResult.vehicleInfo && (
                        <View style={styles.vehicleInfo}>
                          <Text style={styles.vehicleTitle}>Vehicle Information:</Text>
                          <Text>Plate: {validationResult.vehicleInfo.plateNumber}</Text>
                          <Text>Owner: {validationResult.vehicleInfo.ownerName}</Text>
                          <Text>Type: {validationResult.vehicleInfo.vehicleType}</Text>
                          <Text>Brand: {validationResult.vehicleInfo.brand}</Text>
                          <Text>Model: {validationResult.vehicleInfo.model}</Text>
                          <Text>Year: {validationResult.vehicleInfo.year}</Text>
                          
                          {validationResult.vehicleInfo.taxStatus && (
                            <Text style={[
                              styles.statusText,
                              validationResult.vehicleInfo.taxStatus === 'paid' ? styles.paidStatus : styles.pendingStatus
                            ]}>
                              Tax Status: {validationResult.vehicleInfo.taxStatus.toUpperCase()}
                            </Text>
                          )}
                          
                          {validationResult.vehicleInfo.insuranceStatus && (
                            <Text style={[
                              styles.statusText,
                              validationResult.vehicleInfo.insuranceStatus === 'valid' ? styles.validStatus : styles.invalidStatus
                            ]}>
                              {t('scanner.insurance')}: {(validationResult.vehicleInfo.insuranceStatus === 'valid' ? t('common.valid') : t('common.invalid')).toUpperCase()}
                            </Text>
                          )}
                          
                          {validationResult.vehicleInfo.amountDue && (
                            <Text style={styles.amountText}>
                              {t('scanner.amountDue')}: {validationResult.vehicleInfo.amountDue.toLocaleString()} FCFA
                            </Text>
                          )}
                        </View>
                      )}
                      
                      {validationResult.warnings && validationResult.warnings.length > 0 && (
                        <View style={styles.warningsContainer}>
                          <Text style={styles.warningsTitle}>{t('scanner.warnings')}:</Text>
                          {validationResult.warnings.map((warning, index) => (
                            <Text key={index} style={styles.warningText}>⚠ {warning}</Text>
                          ))}
                        </View>
                      )}
                      
                      {validationResult.reason && (
                        <Text style={styles.reasonText}>
                          {validationResult.reason}
                        </Text>
                      )}
                    </View>
                  )}
                </View>
              )}
            </ScrollView>
            
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowResult(false)}
            >
              <Text style={styles.buttonText}>{t('common.close')}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  camera: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  header: {
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  headerText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
  scanArea: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanFrame: {
    width: 250,
    height: 250,
    borderWidth: 2,
    borderColor: '#007AFF',
    borderRadius: 10,
    position: 'relative',
  },
  scanLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 2,
    backgroundColor: '#007AFF',
    top: '50%',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  manualButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  message: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
  },
  permissionButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  processingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  processingText: {
    color: 'white',
    fontSize: 16,
    marginTop: 10,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 20,
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
  },
  resultText: {
    fontSize: 16,
    marginBottom: 10,
  },
  validationText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginVertical: 10,
  },
  validText: {
    color: '#34C759',
  },
  invalidText: {
    color: '#FF3B30',
  },
  vehicleInfo: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 8,
    marginVertical: 10,
  },
  vehicleTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  statusText: {
    fontWeight: 'bold',
    marginTop: 5,
  },
  paidStatus: {
    color: '#34C759',
  },
  pendingStatus: {
    color: '#FF9500',
  },
  validStatus: {
    color: '#34C759',
  },
  invalidStatus: {
    color: '#FF3B30',
  },
  amountText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FF3B30',
    marginTop: 10,
  },
  warningsContainer: {
    backgroundColor: '#fff3cd',
    padding: 15,
    borderRadius: 8,
    marginVertical: 10,
  },
  warningsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  warningText: {
    color: '#856404',
    marginVertical: 2,
  },
  reasonText: {
    fontStyle: 'italic',
    color: '#666',
    marginTop: 10,
  },
  closeButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
    alignItems: 'center',
  },
});