import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { useScanner } from '../context/ScannerContext';
import { AgentType } from '../types/auth.types';
import { ScanRecord } from '../types/scanner.types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Ionicons } from '@expo/vector-icons';
import { t } from '../utils/translations';

export default function DashboardScreen({ navigation }: { navigation: any }) {
  const { agent, logout } = useAuth();
  const { scanHistory } = useScanner();
  const [isLoading, setIsLoading] = useState(false);
  const [recentScans, setRecentScans] = useState<ScanRecord[]>([]);
  const [stats, setStats] = useState({
    totalScans: 0,
    validScans: 0,
    invalidScans: 0,
    totalAmount: 0,
  });

  useEffect(() => {
    // Filter recent scans (last 7 days)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    const recent = scanHistory
      .filter(scan => new Date(scan.timestamp) >= sevenDaysAgo)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 5);
    
    setRecentScans(recent);

    // Calculate stats
    const totalScans = scanHistory.length;
    const validScans = scanHistory.filter(scan => 
      scan.validationResult?.valid
    ).length;
    const invalidScans = totalScans - validScans;
    const totalAmount = scanHistory.reduce((sum, scan) => {
      return sum + (scan.validationResult?.vehicleInfo?.amountDue || 0);
    }, 0);

    setStats({
      totalScans,
      validScans,
      invalidScans,
      totalAmount,
    });
  }, [scanHistory]);

  const handleLogout = async () => {
    setIsLoading(true);
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
      Alert.alert(t('dashboard.errorTitle'), t('dashboard.logoutFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleScanPress = () => {
    if (agent?.type === AgentType.GOVERNMENT) {
      navigation.navigate('Scanner');
    } else {
      Alert.alert(t('dashboard.accessDeniedTitle'), t('dashboard.accessDeniedMessage'));
    }
  };

  const handleScanHistory = () => {
    navigation.navigate('ScanHistory');
  };

  const handleProfile = () => {
    navigation.navigate('Profile');
  };

  const getStatusColor = (isValid: boolean) => {
    return isValid ? '#34C759' : '#FF3B30';
  };

  if (!agent) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.userInfo}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {agent.name.charAt(0).toUpperCase()}
            </Text>
          </View>
          <View style={styles.userDetails}>
            <Text style={styles.userName}>{agent.name}</Text>
            <Text style={styles.userRole}>
              {agent.type === AgentType.GOVERNMENT ? t('dashboard.governmentAgent') : t('dashboard.partnerAgent')}
            </Text>
            <Text style={styles.userBadge}>{t('dashboard.badge')} {agent.badgeId}</Text>
          </View>
        </View>
        
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout} disabled={isLoading}>
          <Ionicons name="log-out-outline" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        {/* Actions rapides */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('dashboard.quickActions')}</Text>
          <View style={styles.actionGrid}>
            {agent.type === AgentType.GOVERNMENT && (
              <TouchableOpacity
                style={[styles.actionButton, styles.scanButton]}
                onPress={handleScanPress}
              >
                <Ionicons name="qr-code-outline" size={32} color="white" />
                <Text style={styles.actionButtonText}>{t('dashboard.scan')}</Text>
              </TouchableOpacity>
            )}
            
            <TouchableOpacity
              style={[styles.actionButton, styles.historyButton]}
              onPress={handleScanHistory}
            >
              <Ionicons name="time-outline" size={32} color="white" />
              <Text style={styles.actionButtonText}>{t('dashboard.history')}</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[styles.actionButton, styles.profileButton]}
              onPress={handleProfile}
            >
              <Ionicons name="person-outline" size={32} color="white" />
              <Text style={styles.actionButtonText}>{t('dashboard.profile')}</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Statistiques */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('dashboard.statistics')}</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.totalScans}</Text>
              <Text style={styles.statLabel}>{t('dashboard.totalScans')}</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#E8F5E8' }]}>
              <Text style={[styles.statNumber, { color: '#34C759' }]}>
                {stats.validScans}
              </Text>
              <Text style={styles.statLabel}>{t('dashboard.valid')}</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#FFE8E8' }]}>
              <Text style={[styles.statNumber, { color: '#FF3B30' }]}>
                {stats.invalidScans}
              </Text>
              <Text style={styles.statLabel}>{t('dashboard.invalid')}</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#FFF8E8' }]}>
              <Text style={[styles.statNumber, { color: '#FF9500' }]}>
                {formatCurrency(stats.totalAmount)}
              </Text>
              <Text style={styles.statLabel}>{t('dashboard.totalAmount')}</Text>
            </View>
          </View>
        </View>

        {/* Scans récents */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('dashboard.recentScans')}</Text>
          {recentScans.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="document-text-outline" size={48} color="#ccc" />
              <Text style={styles.emptyStateText}>{t('dashboard.noRecentScans')}</Text>
            </View>
          ) : (
            <View style={styles.scanList}>
              {recentScans.map((scan) => (
                <TouchableOpacity
                  key={scan.id}
                  style={styles.scanItem}
                  onPress={() => navigation.navigate('ScanDetail', { scan })}
                >
                  <View style={styles.scanInfo}>
                    <Text style={styles.scanType}>{scan.type.toUpperCase()}</Text>
                    <Text style={styles.scanData}>
                      {scan.data || scan.plateNumber}
                    </Text>
                    <Text style={styles.scanDate}>
                      {formatDate(scan.timestamp)}
                    </Text>
                  </View>
                  <View style={styles.scanStatus}>
                    <View
                      style={[
                        styles.statusIndicator,
                        { backgroundColor: getStatusColor(scan.validationResult?.valid || false) },
                      ]}
                    />
                    <Text style={styles.statusText}>
                      {scan.validationResult?.valid ? t('common.valid') : t('common.invalid')}
                    </Text>
                  </View>
                </TouchableOpacity>
              ))}
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
    backgroundColor: 'white',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  avatarText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  userDetails: {
    flex: 1,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  userRole: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  userBadge: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  logoutButton: {
    padding: 10,
  },
  content: {
    padding: 20,
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  actionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
  },
  actionButton: {
    width: 100,
    height: 100,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
  },
  scanButton: {
    backgroundColor: '#007AFF',
  },
  historyButton: {
    backgroundColor: '#34C759',
  },
  profileButton: {
    backgroundColor: '#FF9500',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 8,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    width: '48%',
    marginBottom: 10,
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
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
  },
  scanList: {
    backgroundColor: 'white',
    borderRadius: 10,
    overflow: 'hidden',
  },
  scanItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  scanInfo: {
    flex: 1,
  },
  scanType: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  scanData: {
    fontSize: 16,
    color: '#666',
    marginBottom: 2,
  },
  scanDate: {
    fontSize: 12,
    color: '#999',
  },
  scanStatus: {
    alignItems: 'center',
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginBottom: 4,
  },
  statusText: {
    fontSize: 12,
    color: '#666',
  },
  emptyState: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 40,
    alignItems: 'center',
  },
  emptyStateText: {
    fontSize: 16,
    color: '#999',
    marginTop: 10,
  },
});