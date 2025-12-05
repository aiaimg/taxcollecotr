import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { contraventionService } from '../services/contraventionService';
import { Contravention, ContraventionStatus } from '../types/contravention.types';
import { useAuth } from '../context/AuthContext';
import { auditService } from '../services/auditService';
import { t } from '../utils/translations';

export default function ContraventionDetailScreen({ route, navigation }: { route: any; navigation: any }) {
  const { id } = route.params;
  const { agent, hasPermission } = useAuth();
  const [item, setItem] = useState<Contravention | null>(null);
  const [loading, setLoading] = useState(true);
  const [voiding, setVoiding] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await contraventionService.getContravention(id);
      if (res.success && res.data) setItem(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const onVoid = async () => {
    if (!hasPermission('void_contravention')) {
      Alert.alert(t('dashboard.accessDeniedTitle'), t('dashboard.accessDeniedMessage'));
      return;
    }
    setVoiding(true);
    try {
      const res = await contraventionService.voidContravention(id, 'Violation cleared by supervisor');
      if (res.success) {
        await auditService.logAction('contravention_void', agent?.id || 'unknown', id, { reason: 'Violation cleared by supervisor' });
        await load();
        Alert.alert(t('contraventions.voidSuccessTitle'), t('contraventions.voidSuccessMessage'));
      } else {
        Alert.alert(t('errors.serverError'), res.error || '');
      }
    } finally {
      setVoiding(false);
    }
  };

  if (loading || !item) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>{t('contraventions.detailTitle')}</Text>
        <Text style={styles.label}>{t('contraventions.offender')}</Text>
        <Text style={styles.value}>{item.offenderId}</Text>
        <Text style={styles.label}>{t('contraventions.offenseDetails')}</Text>
        <Text style={styles.value}>{item.offenseDetails}</Text>
        <Text style={styles.label}>{t('contraventions.timestamp')}</Text>
        <Text style={styles.value}>{new Date(item.timestamp).toLocaleString()}</Text>
        <Text style={styles.label}>{t('contraventions.location')}</Text>
        <Text style={styles.value}>{`${item.location.latitude}, ${item.location.longitude}`}</Text>
        <Text style={styles.label}>{t('contraventions.status')}</Text>
        <View style={[styles.statusBadge, { backgroundColor: statusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>{t('contraventions.evidence')}</Text>
        {item.evidence.length === 0 ? (
          <Text style={styles.value}>{t('contraventions.noEvidence')}</Text>
        ) : (
          item.evidence.map(ev => (
            <View key={ev.id} style={styles.evidenceItem}>
              <Ionicons name="image-outline" size={18} color="#666" />
              <Text style={styles.evidenceText}>{ev.type.toUpperCase()} • {ev.uri}</Text>
            </View>
          ))
        )}
      </View>

      {hasPermission('void_contravention') && item.status !== ContraventionStatus.VOIDED && (
        <TouchableOpacity style={styles.voidBtn} onPress={onVoid} disabled={voiding}>
          <Ionicons name="trash-outline" size={20} color="white" />
          <Text style={styles.voidText}>{t('contraventions.void')}</Text>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
}

function statusColor(s: ContraventionStatus) {
  switch (s) {
    case ContraventionStatus.ISSUED:
      return '#FF9500';
    case ContraventionStatus.PAID:
      return '#34C759';
    case ContraventionStatus.DISPUTED:
      return '#FF3B30';
    case ContraventionStatus.VOIDED:
      return '#8E8E93';
    default:
      return '#007AFF';
  }
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  card: { backgroundColor: 'white', margin: 15, borderRadius: 10, padding: 15, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 3.84, elevation: 5 },
  title: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 10 },
  label: { fontSize: 12, color: '#666', marginTop: 8 },
  value: { fontSize: 14, color: '#333', marginTop: 2 },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12, alignSelf: 'flex-start', marginTop: 4 },
  statusText: { color: 'white', fontSize: 12, fontWeight: '600' },
  evidenceItem: { flexDirection: 'row', alignItems: 'center', marginTop: 8 },
  evidenceText: { marginLeft: 8, color: '#666' },
  voidBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#FF3B30', marginHorizontal: 15, marginBottom: 30, paddingVertical: 12, borderRadius: 8 },
  voidText: { color: 'white', fontWeight: '600', marginLeft: 8 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});

