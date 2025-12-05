import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../navigation/AppNavigator';
import { Ionicons } from '@expo/vector-icons';
import { formatDate, formatCurrency } from '../utils/formatters';
import { t } from '../utils/translations';

interface ScanDetailScreenProps {
  route: RouteProp<RootStackParamList, 'ScanDetail'>;
  navigation: any;
}

export default function ScanDetailScreen({ route, navigation }: ScanDetailScreenProps) {
  const { scan } = route.params;

  const handleShare = () => {
    Alert.alert(t('detail.shareTitle'), t('detail.shareMessage'));
  };

  const handleExport = () => {
    Alert.alert(t('detail.exportTitle'), t('detail.exportMessage'));
  };

  const getStatusColor = (isValid: boolean) => {
    return isValid ? '#34C759' : '#FF3B30';
  };

  const getStatusIcon = (isValid: boolean) => {
    return isValid ? 'checkmark-circle' : 'close-circle';
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back-outline" size={24} color="#007AFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{t('detail.headerTitle')}</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity onPress={handleShare} style={styles.headerButton}>
            <Ionicons name="share-outline" size={24} color="#007AFF" />
          </TouchableOpacity>
          <TouchableOpacity onPress={handleExport} style={styles.headerButton}>
            <Ionicons name="download-outline" size={24} color="#007AFF" />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.content}>
        {/* Informations de scan */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t('detail.scanInformation')}</Text>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t('detail.scanId')}</Text>
            <Text style={styles.infoValue}>{scan.id}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t('detail.type')}</Text>
            <Text style={styles.infoValue}>{scan.type.toUpperCase()}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t('detail.data')}</Text>
            <Text style={styles.infoValue}>{scan.data || scan.plateNumber}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t('detail.timestamp')}</Text>
            <Text style={styles.infoValue}>{formatDate(scan.timestamp)}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t('detail.agent')}</Text>
            <Text style={styles.infoValue}>{scan.agentId}</Text>
          </View>
          
          {scan.location && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{t('detail.location')}</Text>
              <Text style={styles.infoValue}>
                {scan.location.latitude.toFixed(6)}, {scan.location.longitude.toFixed(6)}
              </Text>
            </View>
          )}
        </View>

        {/* Résultat de validation */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t('detail.validationResult')}</Text>
          
          <View style={styles.validationHeader}>
            <Ionicons
              name={getStatusIcon(scan.validationResult?.valid || false)}
              size={32}
              color={getStatusColor(scan.validationResult?.valid || false)}
            />
            <Text style={[
              styles.validationText,
              { color: getStatusColor(scan.validationResult?.valid || false) }
            ]}>
              {scan.validationResult?.valid ? t('common.valid').toUpperCase() : t('common.invalid').toUpperCase()}
            </Text>
          </View>
          
          {scan.validationResult?.reason && (
            <View style={styles.reasonContainer}>
              <Text style={styles.reasonLabel}>{t('detail.reason')}</Text>
              <Text style={styles.reasonText}>{scan.validationResult.reason}</Text>
            </View>
          )}
          
          {scan.validationResult?.warnings && scan.validationResult.warnings.length > 0 && (
            <View style={styles.warningsContainer}>
              <Text style={styles.warningsTitle}>{t('detail.warnings')}</Text>
              {scan.validationResult.warnings.map((warning, index) => (
                <Text key={index} style={styles.warningText}>• {warning}</Text>
              ))}
            </View>
          )}
        </View>

        {/* Informations du véhicule */}
        {scan.validationResult?.vehicleInfo && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{t('detail.vehicleInformation')}</Text>
            
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{t('detail.plateNumber')}</Text>
              <Text style={styles.infoValue}>{scan.validationResult.vehicleInfo.plateNumber}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{t('detail.owner')}</Text>
              <Text style={styles.infoValue}>{scan.validationResult.vehicleInfo.ownerName}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{t('detail.vehicleType')}</Text>
              <Text style={styles.infoValue}>{scan.validationResult.vehicleInfo.vehicleType}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{t('detail.brand')}</Text>
              <Text style={styles.infoValue}>{scan.validationResult.vehicleInfo.brand}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{t('detail.model')}</Text>
              <Text style={styles.infoValue}>{scan.validationResult.vehicleInfo.model}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{t('detail.year')}</Text>
              <Text style={styles.infoValue}>{scan.validationResult.vehicleInfo.year}</Text>
            </View>
            
            {scan.validationResult.vehicleInfo.taxStatus && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>{t('detail.taxStatus')}</Text>
                <Text style={[
                  styles.infoValue,
                  scan.validationResult.vehicleInfo.taxStatus === 'paid' 
                    ? styles.statusPaid 
                    : styles.statusPending
                ]}>
                  {scan.validationResult.vehicleInfo.taxStatus === 'paid' ? t('common.paid') : t('common.pending')}
                </Text>
              </View>
            )}
            
            {scan.validationResult.vehicleInfo.insuranceStatus && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>{t('detail.insurance')}</Text>
                <Text style={[
                  styles.infoValue,
                  scan.validationResult.vehicleInfo.insuranceStatus === 'valid' 
                    ? styles.statusValid 
                    : styles.statusInvalid
                ]}>
                  {scan.validationResult.vehicleInfo.insuranceStatus === 'valid' ? t('common.valid') : t('common.invalid')}
                </Text>
              </View>
            )}
            
            {scan.validationResult.vehicleInfo.amountDue && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>{t('detail.amountDue')}</Text>
                <Text style={styles.amountText}>
                  {formatCurrency(scan.validationResult.vehicleInfo.amountDue)}
                </Text>
              </View>
            )}
            
            {scan.validationResult.vehicleInfo.lastTaxPayment && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>{t('detail.lastTaxPayment')}</Text>
                <Text style={styles.infoValue}>
                  {formatDate(scan.validationResult.vehicleInfo.lastTaxPayment)}
                </Text>
              </View>
            )}
          </View>
        )}

        {/* Informations de synchronisation */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t('detail.syncInformation')}</Text>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t('detail.synced')}</Text>
            <Text style={styles.infoValue}>
              {scan.synced ? t('common.yes') : t('common.no')}
            </Text>
          </View>
          
          {scan.syncError && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{t('detail.syncError')}</Text>
              <Text style={styles.errorText}>{scan.syncError}</Text>
            </View>
          )}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
    textAlign: 'center',
  },
  headerActions: {
    flexDirection: 'row',
  },
  headerButton: {
    marginLeft: 15,
  },
  content: {
    padding: 20,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
  },
  validationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
  },
  validationText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  reasonContainer: {
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    padding: 15,
    marginTop: 10,
  },
  reasonLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
    marginBottom: 5,
  },
  reasonText: {
    fontSize: 14,
    color: '#333',
  },
  warningsContainer: {
    backgroundColor: '#fff8e1',
    borderRadius: 8,
    padding: 15,
    marginTop: 10,
  },
  warningsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#856404',
    marginBottom: 5,
  },
  warningText: {
    fontSize: 14,
    color: '#856404',
    marginVertical: 2,
  },
  statusPaid: {
    color: '#34C759',
    fontWeight: 'bold',
  },
  statusPending: {
    color: '#FF9500',
    fontWeight: 'bold',
  },
  statusValid: {
    color: '#34C759',
    fontWeight: 'bold',
  },
  statusInvalid: {
    color: '#FF3B30',
    fontWeight: 'bold',
  },
  amountText: {
    fontSize: 14,
    color: '#FF3B30',
    fontWeight: 'bold',
  },
  errorText: {
    fontSize: 14,
    color: '#FF3B30',
  },
});