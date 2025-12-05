import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, FlatList, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { contraventionService } from '../services/contraventionService';
import { Contravention, ContraventionListParams, ContraventionStatus } from '../types/contravention.types';
import { t } from '../utils/translations';

export default function ContraventionListScreen({ navigation }: { navigation: any }) {
  const { agent, canAccessFeature } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<ContraventionStatus | undefined>(undefined);
  const [items, setItems] = useState<Contravention[]>([]);

  const load = async () => {
    if (!canAccessFeature('contraventions')) return;
    setIsLoading(true);
    try {
      const params: ContraventionListParams = { search, status, page: 1, pageSize: 20, department: agent?.department };
      const res = await contraventionService.listContraventions(params);
      if (res.success && res.data) {
        setItems(res.data.results || []);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  const onSearch = () => load();

  const renderItem = ({ item }: { item: Contravention }) => (
    <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('ContraventionDetail', { id: item.id })}>
      <View style={styles.itemHeader}>
        <Text style={styles.itemTitle}>{item.offenseDetails}</Text>
        <View style={[styles.statusBadge, { backgroundColor: statusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
        </View>
      </View>
      <Text style={styles.itemSub}>{item.offenderId}</Text>
      <Text style={styles.itemSub}>{new Date(item.timestamp).toLocaleString()}</Text>
    </TouchableOpacity>
  );

  if (!canAccessFeature('contraventions')) {
    return (
      <View style={styles.center}>
        <Ionicons name="shield-outline" size={56} color="#ccc" />
        <Text style={styles.centerText}>{t('dashboard.accessDeniedMessage')}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.searchRow}>
        <TextInput
          style={styles.input}
          placeholder={t('contraventions.searchPlaceholder')}
          value={search}
          onChangeText={setSearch}
        />
        <TouchableOpacity style={styles.searchBtn} onPress={onSearch}>
          <Ionicons name="search" size={20} color="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.filterRow}>
        {([undefined, ContraventionStatus.ISSUED, ContraventionStatus.PAID, ContraventionStatus.DISPUTED] as const).map(s => (
          <TouchableOpacity
            key={s || 'all'}
            style={[styles.filterChip, s === status && styles.filterChipActive]}
            onPress={() => setStatus(s)}
          >
            <Text style={[styles.filterText, s === status && styles.filterTextActive]}>
              {s ? s.toUpperCase() : t('contraventions.filterAll')}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {isLoading ? (
        <View style={styles.center}> 
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      ) : items.length === 0 ? (
        <View style={styles.center}>
          <Ionicons name="document-text-outline" size={48} color="#ccc" />
          <Text style={styles.centerText}>{t('contraventions.emptyText')}</Text>
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(i) => i.id}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 20 }}
        />
      )}

      <TouchableOpacity style={styles.fab} onPress={() => navigation.navigate('ContraventionForm')}>
        <Ionicons name="add" size={28} color="white" />
      </TouchableOpacity>
    </View>
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
  searchRow: { flexDirection: 'row', padding: 15, backgroundColor: 'white', borderBottomWidth: 1, borderBottomColor: '#e0e0e0' },
  input: { flex: 1, borderWidth: 1, borderColor: '#e0e0e0', borderRadius: 8, paddingHorizontal: 12, height: 40 },
  searchBtn: { marginLeft: 10, backgroundColor: '#007AFF', borderRadius: 8, width: 40, height: 40, alignItems: 'center', justifyContent: 'center' },
  filterRow: { flexDirection: 'row', paddingHorizontal: 15, paddingVertical: 10, backgroundColor: 'white' },
  filterChip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, borderWidth: 1, borderColor: '#e0e0e0', marginRight: 10 },
  filterChipActive: { backgroundColor: '#007AFF22', borderColor: '#007AFF' },
  filterText: { color: '#666', fontWeight: '600' },
  filterTextActive: { color: '#007AFF' },
  item: { backgroundColor: 'white', marginHorizontal: 15, marginTop: 10, borderRadius: 10, padding: 15, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 3.84, elevation: 5 },
  itemHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  itemTitle: { fontSize: 16, fontWeight: 'bold', color: '#333' },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12 },
  statusText: { color: 'white', fontSize: 12, fontWeight: '600' },
  itemSub: { fontSize: 12, color: '#666', marginTop: 4 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  centerText: { color: '#999', marginTop: 10 },
  fab: { position: 'absolute', right: 20, bottom: 20, backgroundColor: '#007AFF', width: 56, height: 56, borderRadius: 28, alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.2, shadowRadius: 3.84, elevation: 6 },
});

