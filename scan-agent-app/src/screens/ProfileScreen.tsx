import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Switch,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { AgentType } from '../types/auth.types';
import { Ionicons } from '@expo/vector-icons';
import { t } from '../utils/translations';
import { formatDate } from '../utils/formatters';
import { LanguageSelector } from '../components/LanguageSelector';

export default function ProfileScreen() {
  const { agent, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [autoSync, setAutoSync] = useState(true);
  const [offlineMode, setOfflineMode] = useState(false);

  const handleLogout = async () => {
    setIsLoading(true);
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
      Alert.alert(t('profile.errorTitle'), t('profile.logoutFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangePassword = () => {
    Alert.alert(t('profile.changePasswordTitle'), t('profile.changePasswordMessage'));
  };

  const handleContactSupport = () => {
    Alert.alert(t('profile.contactSupportTitle'), t('profile.contactSupportMessage'));
  };

  const handleAbout = () => {
    Alert.alert(t('profile.aboutTitle'), t('profile.aboutMessage'));
  };

  if (!agent) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{t('profile.agentNotFound')}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {agent.name.charAt(0).toUpperCase()}
            </Text>
          </View>
          <Text style={styles.userName}>{agent.name}</Text>
          <Text style={styles.userRole}>
            {agent.type === AgentType.GOVERNMENT ? t('profile.governmentAgent') : t('profile.partnerAgent')}
          </Text>
        </View>
      </View>

      <View style={styles.content}>
        {/* Informations agent */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('profile.infoSection')}</Text>
          <View style={styles.infoCard}>
            <View style={styles.infoRow}>
              <Ionicons name="person-outline" size={20} color="#666" />
              <View style={styles.infoTextContainer}>
                <Text style={styles.infoLabel}>{t('profile.fullName')}</Text>
                <Text style={styles.infoValue}>{agent.name}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <Ionicons name="id-card-outline" size={20} color="#666" />
              <View style={styles.infoTextContainer}>
                <Text style={styles.infoLabel}>{t('profile.badgeId')}</Text>
                <Text style={styles.infoValue}>{agent.badgeId}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <Ionicons name="mail-outline" size={20} color="#666" />
              <View style={styles.infoTextContainer}>
                <Text style={styles.infoLabel}>{t('profile.email')}</Text>
                <Text style={styles.infoValue}>{agent.email}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <Ionicons name="call-outline" size={20} color="#666" />
              <View style={styles.infoTextContainer}>
                <Text style={styles.infoLabel}>{t('profile.phone')}</Text>
                <Text style={styles.infoValue}>{agent.phone}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <Ionicons name="calendar-outline" size={20} color="#666" />
              <View style={styles.infoTextContainer}>
                <Text style={styles.infoLabel}>{t('profile.accountCreated')}</Text>
                <Text style={styles.infoValue}>{formatDate(agent.createdAt)}</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Permissions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('profile.permissionsSection')}</Text>
          <View style={styles.permissionsCard}>
            <View style={styles.permissionRow}>
              <View style={styles.permissionInfo}>
                <Ionicons name="qr-code-outline" size={24} color="#007AFF" />
                <View style={styles.permissionTextContainer}>
                  <Text style={styles.permissionTitle}>{t('profile.scanning')}</Text>
                  <Text style={styles.permissionDescription}>
                    {agent.type === AgentType.GOVERNMENT 
                      ? t('profile.scanningGov')
                      : t('profile.scanningPartner')
                    }
                  </Text>
                </View>
              </View>
              <View style={[
                styles.permissionStatus,
                { backgroundColor: agent.type === AgentType.GOVERNMENT ? '#34C759' : '#FF9500' }
              ]}>
                <Text style={styles.permissionStatusText}>
                  {agent.type === AgentType.GOVERNMENT ? t('profile.full') : t('profile.limited')}
                </Text>
              </View>
            </View>
            
            <View style={styles.permissionRow}>
              <View style={styles.permissionInfo}>
                <Ionicons name="cash-outline" size={24} color="#007AFF" />
                <View style={styles.permissionTextContainer}>
                  <Text style={styles.permissionTitle}>{t('profile.payments')}</Text>
                  <Text style={styles.permissionDescription}>
                    {agent.type === AgentType.GOVERNMENT 
                      ? t('profile.paymentsGov')
                      : t('profile.paymentsPartner')
                    }
                  </Text>
                </View>
              </View>
              <View style={[
                styles.permissionStatus,
                { backgroundColor: agent.type === AgentType.GOVERNMENT ? '#34C759' : '#FF9500' }
              ]}>
                <Text style={styles.permissionStatusText}>
                  {agent.type === AgentType.GOVERNMENT ? t('profile.full') : t('profile.limited')}
                </Text>
              </View>
            </View>
            
            <View style={styles.permissionRow}>
              <View style={styles.permissionInfo}>
                <Ionicons name="analytics-outline" size={24} color="#007AFF" />
                <View style={styles.permissionTextContainer}>
                  <Text style={styles.permissionTitle}>{t('profile.reports')}</Text>
                  <Text style={styles.permissionDescription}>
                    {agent.type === AgentType.GOVERNMENT 
                      ? t('profile.reportsGov')
                      : t('profile.reportsPartner')
                    }
                  </Text>
                </View>
              </View>
              <View style={[
                styles.permissionStatus,
                { backgroundColor: agent.type === AgentType.GOVERNMENT ? '#34C759' : '#FF9500' }
              ]}>
                <Text style={styles.permissionStatusText}>
                  {agent.type === AgentType.GOVERNMENT ? t('profile.full') : t('profile.limited')}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Paramètres */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('profile.settingsSection')}</Text>
          
          {/* Language Selector */}
          <LanguageSelector />
          
          <View style={styles.settingsCard}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Ionicons name="notifications-outline" size={20} color="#666" />
                <Text style={styles.settingText}>{t('profile.notifications')}</Text>
              </View>
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: '#ccc', true: '#007AFF' }}
                thumbColor={notifications ? '#007AFF' : '#f4f3f4'}
              />
            </View>
            
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Ionicons name="sync-outline" size={20} color="#666" />
                <Text style={styles.settingText}>{t('profile.autoSync')}</Text>
              </View>
              <Switch
                value={autoSync}
                onValueChange={setAutoSync}
                trackColor={{ false: '#ccc', true: '#007AFF' }}
                thumbColor={autoSync ? '#007AFF' : '#f4f3f4'}
              />
            </View>
            
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Ionicons name="cloud-offline-outline" size={20} color="#666" />
                <Text style={styles.settingText}>{t('profile.offlineMode')}</Text>
              </View>
              <Switch
                value={offlineMode}
                onValueChange={setOfflineMode}
                trackColor={{ false: '#ccc', true: '#007AFF' }}
                thumbColor={offlineMode ? '#007AFF' : '#f4f3f4'}
              />
            </View>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('profile.actionsSection')}</Text>
          <View style={styles.actionsCard}>
            <TouchableOpacity style={styles.actionRow} onPress={handleChangePassword}>
              <Ionicons name="key-outline" size={20} color="#007AFF" />
              <Text style={styles.actionText}>{t('profile.changePasswordTitle')}</Text>
              <Ionicons name="chevron-forward-outline" size={20} color="#ccc" />
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionRow} onPress={handleContactSupport}>
              <Ionicons name="help-circle-outline" size={20} color="#007AFF" />
              <Text style={styles.actionText}>{t('profile.contactSupportTitle')}</Text>
              <Ionicons name="chevron-forward-outline" size={20} color="#ccc" />
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionRow} onPress={handleAbout}>
              <Ionicons name="information-circle-outline" size={20} color="#007AFF" />
              <Text style={styles.actionText}>{t('profile.aboutTitle')}</Text>
              <Ionicons name="chevron-forward-outline" size={20} color="#ccc" />
            </TouchableOpacity>
            
            <TouchableOpacity style={[styles.actionRow, styles.logoutRow]} onPress={handleLogout}>
              <Ionicons name="log-out-outline" size={20} color="#FF3B30" />
              <Text style={[styles.actionText, styles.logoutText]}>{t('profile.logout')}</Text>
              <Ionicons name="chevron-forward-outline" size={20} color="#ccc" />
            </TouchableOpacity>
          </View>
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
    paddingVertical: 30,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  avatarContainer: {
    alignItems: 'center',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
  },
  avatarText: {
    color: 'white',
    fontSize: 32,
    fontWeight: 'bold',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  userRole: {
    fontSize: 16,
    color: '#666',
  },
  content: {
    padding: 20,
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  infoCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoTextContainer: {
    flex: 1,
    marginLeft: 15,
  },
  infoLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  permissionsCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  permissionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  permissionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  permissionTextContainer: {
    flex: 1,
    marginLeft: 15,
  },
  permissionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  permissionDescription: {
    fontSize: 14,
    color: '#666',
  },
  permissionStatus: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  permissionStatusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  settingsCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 15,
  },
  actionsCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  actionText: {
    flex: 1,
    fontSize: 16,
    color: '#333',
    marginLeft: 15,
  },
  logoutRow: {
    borderBottomWidth: 0,
  },
  logoutText: {
    color: '#FF3B30',
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
    marginTop: 20,
  },
});