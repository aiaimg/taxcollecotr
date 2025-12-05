import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { useScanner } from '../context/ScannerContext';
import { ScanRecord } from '../types/scanner.types';
import { formatDate, formatCurrency } from '../utils/formatters';
import { Ionicons } from '@expo/vector-icons';
import { t } from '../utils/translations';

export default function ScanHistoryScreen({ navigation }: { navigation: any }) {
  const { scanHistory, isLoading } = useScanner();
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<'all' | 'valid' | 'invalid'>('all');

  const filteredHistory = scanHistory.filter(scan => {
    if (filter === 'valid') return scan.validationResult?.valid === true;
    if (filter === 'invalid') return scan.validationResult?.valid === false;
    return true;
  });

  const onRefresh = async () => {
    setRefreshing(true);
    // In a real app, this would sync with the server
    setTimeout(() => setRefreshing(false), 1000);
  };

  const handleScanPress = (scan: ScanRecord) => {
    navigation.navigate('ScanDetail', { scan });
  };

  const handleDeleteScan = (scanId: string) => {
    Alert.alert(
      t('history.deleteTitle'),
      t('history.deleteMessage'),
      [
        { text: t('history.cancel'), style: 'cancel' },
        {
          text: t('history.delete'),
          style: 'destructive',
          onPress: () => {
            // In a real app, this would delete from storage
            console.log('Delete scan:', scanId);
          },
        },
      ]
    );
  };

  const getStatusColor = (isValid: boolean) => {
    return isValid ? '#34C759' : '#FF3B30';
  };

  const renderScanItem = ({ item }: { item: ScanRecord }) => (
    <TouchableOpacity
      style={styles.scanItem}
      onPress={() => handleScanPress(item)}
      activeOpacity={0.7}
    >
      <View style={styles.scanContent}>
        <View style={styles.scanHeader}>
          <Text style={styles.scanType}>{item.type.toUpperCase()}</Text>
          <Text style={styles.scanDate}>{formatDate(item.timestamp)}</Text>
        </View>
        
        <Text style={styles.scanData}>
          {item.data || item.plateNumber}
        </Text>
        
        {item.location && (
          <Text style={styles.locationText}>
            📍 {item.location.latitude.toFixed(6)}, {item.location.longitude.toFixed(6)}
          </Text>
        )}
        
        <View style={styles.scanFooter}>
          <View style={styles.statusContainer}>
            <View
              style={[
                styles.statusIndicator,
                { backgroundColor: getStatusColor(item.validationResult?.valid || false) },
              ]}
            />
            <Text style={styles.statusText}>
              {item.validationResult?.valid ? t('history.statusValid') : t('history.statusInvalid')}
            </Text>
          </View>
          
          {item.validationResult?.vehicleInfo?.amountDue && (
            <Text style={styles.amountText}>
              {formatCurrency(item.validationResult.vehicleInfo.amountDue)}
            </Text>
          )}
        </View>
        
        {item.syncError && (
          <Text style={styles.syncErrorText}>{t('history.syncFailed')}</Text>
        )}
      </View>
      
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => handleDeleteScan(item.id)}
      >
        <Ionicons name="trash-outline" size={20} color="#FF3B30" />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      <Text style={styles.headerTitle}>{t('history.title')}</Text>
      <Text style={styles.headerSubtitle}>
        {t('history.totalScans', { count: scanHistory.length })}
      </Text>
      
      <View style={styles.filterContainer}>
        {['all', 'valid', 'invalid'].map((filterOption) => (
          <TouchableOpacity
            key={filterOption}
            style={[
              styles.filterButton,
              filter === filterOption && styles.filterButtonActive,
            ]}
            onPress={() => setFilter(filterOption as any)}
          >
            <Text
              style={[
                styles.filterButtonText,
                filter === filterOption && styles.filterButtonTextActive,
              ]}
            >
              {filterOption === 'all' ? t('history.filterAll') : filterOption === 'valid' ? t('history.filterValid') : t('history.filterInvalid')}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Ionicons name="document-text-outline" size={64} color="#ccc" />
      <Text style={styles.emptyStateTitle}>{t('history.emptyTitle')}</Text>
      <Text style={styles.emptyStateText}>
        {filter === 'all' 
          ? t('history.emptyTextAll')
          : t('history.emptyTextFilter', { filter: filter === 'valid' ? t('history.filterValid').toLowerCase() : t('history.filterInvalid').toLowerCase() })
        }
      </Text>
    </View>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>{t('history.loading')}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={filteredHistory}
        renderItem={renderScanItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmptyState}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  header: {
    backgroundColor: 'white',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 15,
  },
  filterContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  filterButton: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: 'white',
  },
  filterButtonActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  filterButtonText: {
    fontSize: 14,
    color: '#666',
  },
  filterButtonTextActive: {
    color: 'white',
    fontWeight: '600',
  },
  listContainer: {
    paddingBottom: 20,
  },
  scanItem: {
    backgroundColor: 'white',
    marginHorizontal: 15,
    marginVertical: 5,
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  scanContent: {
    flex: 1,
    padding: 15,
  },
  scanHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  scanType: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  scanDate: {
    fontSize: 12,
    color: '#666',
  },
  scanData: {
    fontSize: 16,
    color: '#333',
    marginBottom: 5,
  },
  locationText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 10,
  },
  scanFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 14,
    color: '#666',
  },
  amountText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FF3B30',
  },
  syncErrorText: {
    fontSize: 12,
    color: '#FF3B30',
    marginTop: 5,
  },
  deleteButton: {
    padding: 15,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 10,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
});