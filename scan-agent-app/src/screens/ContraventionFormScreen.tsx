import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import * as Location from 'expo-location';
import { useAuth } from '../context/AuthContext';
import { contraventionService } from '../services/contraventionService';
import { ContraventionCreatePayload } from '../types/contravention.types';
import { auditService } from '../services/auditService';
import { t } from '../utils/translations';

export default function ContraventionFormScreen({ navigation }: { navigation: any }) {
  const { agent, hasPermission } = useAuth();
  const [offenderId, setOffenderId] = useState('');
  const [offenseDetails, setOffenseDetails] = useState('');
  const [evidenceUri, setEvidenceUri] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loc, setLoc] = useState<{ latitude: number; longitude: number } | null>(null);

  const requestLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(t('scanner.noCameraAccess'), t('scanner.grantPermission'));
        return;
      }
      const pos = await Location.getCurrentPositionAsync({});
      setLoc({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
    } catch (e) {
      Alert.alert(t('errors.serverError'));
    }
  };

  const onSubmit = async () => {
    if (!hasPermission('issue_contravention')) {
      Alert.alert(t('dashboard.accessDeniedTitle'), t('dashboard.accessDeniedMessage'));
      return;
    }
    if (!offenderId || !offenseDetails || !loc) {
      Alert.alert(t('contraventions.formInvalidTitle'), t('contraventions.formInvalidMessage'));
      return;
    }
    setIsSubmitting(true);
    try {
      const payload: ContraventionCreatePayload = {
        offenderId,
        offenseDetails,
        location: { latitude: loc.latitude, longitude: loc.longitude },
        timestamp: new Date().toISOString(),
        department: agent?.department,
        evidence: evidenceUri ? [{ id: 'local', type: 'document', uri: evidenceUri }] : [],
      };
      const res = await contraventionService.createContravention(payload);
      if (res.success && res.data) {
        await auditService.logAction('contravention_issue', agent?.id || 'unknown', res.data.id, { offenderId });
        Alert.alert(t('contraventions.createSuccessTitle'), t('contraventions.createSuccessMessage'));
        navigation.goBack();
      } else {
        Alert.alert(t('errors.serverError'), res.error || '');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>{t('contraventions.newTitle')}</Text>
        <Text style={styles.label}>{t('contraventions.offender')}</Text>
        <TextInput style={styles.input} value={offenderId} onChangeText={setOffenderId} placeholder={t('contraventions.offenderPlaceholder')} />
        <Text style={styles.label}>{t('contraventions.offenseDetails')}</Text>
        <TextInput style={[styles.input, { height: 80 }]} value={offenseDetails} onChangeText={setOffenseDetails} placeholder={t('contraventions.offensePlaceholder')} multiline />
        <Text style={styles.label}>{t('contraventions.evidenceUri')}</Text>
        <TextInput style={styles.input} value={evidenceUri} onChangeText={setEvidenceUri} placeholder={t('contraventions.evidencePlaceholder')} />
        <TouchableOpacity style={styles.locBtn} onPress={requestLocation}>
          <Text style={styles.locText}>{loc ? t('contraventions.locationCaptured') : t('contraventions.captureLocation')}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.submitBtn} onPress={onSubmit} disabled={isSubmitting}>
        {isSubmitting ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.submitText}>{t('contraventions.submit')}</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  card: { backgroundColor: 'white', margin: 15, borderRadius: 10, padding: 15, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 3.84, elevation: 5 },
  title: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 10 },
  label: { fontSize: 12, color: '#666', marginTop: 8 },
  input: { borderWidth: 1, borderColor: '#e0e0e0', borderRadius: 8, paddingHorizontal: 12, height: 40, marginTop: 4 },
  locBtn: { marginTop: 10, backgroundColor: '#007AFF', borderRadius: 8, paddingVertical: 10, alignItems: 'center' },
  locText: { color: 'white', fontWeight: '600' },
  submitBtn: { position: 'absolute', left: 15, right: 15, bottom: 20, backgroundColor: '#34C759', borderRadius: 8, paddingVertical: 12, alignItems: 'center' },
  submitText: { color: 'white', fontWeight: '600' },
});

