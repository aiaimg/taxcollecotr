import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useGetVehiclesQuery } from '../../store/api/vehicleApi';
import { VehicleCard } from '../../components/vehicle/VehicleCard';
import { Vehicle } from '../../types/models';
import { colors } from '../../theme/colors';
import { useTranslation } from 'react-i18next';
import useNetworkStatus from '../../hooks/useNetworkStatus';
import OfflineIndicator from '../../components/common/OfflineIndicator';
import { setVehicles } from '../../store/slices/vehicleSlice';
import { useAppDispatch } from '../../store/hooks';

type NavigationProp = NativeStackNavigationProp<any>;

/**
 * Vehicle List Screen
 * Displays list of user's vehicles with pull-to-refresh
 */
export const VehicleListScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const { t } = useTranslation();
  const { data: vehicles, isLoading, isFetching, refetch, error } = useGetVehiclesQuery();
  const { isOnline, isSyncing, formattedLastSync, getCachedVehicles } = useNetworkStatus();
  const dispatch = useAppDispatch();
  const [displayVehicles, setDisplayVehicles] = useState<Vehicle[]>([]);

  const handleVehiclePress = useCallback(
    (vehicle: Vehicle) => {
      navigation.navigate('VehicleDetail', { plaque: vehicle.plaque_immatriculation });
    },
    [navigation]
  );

  const handleAddVehicle = useCallback(() => {
    navigation.navigate('AddVehicle');
  }, [navigation]);

  const renderVehicleItem = useCallback(
    ({ item }: { item: Vehicle }) => (
      <VehicleCard
        vehicle={item}
        onPress={() => handleVehiclePress(item)}
      />
    ),
    [handleVehiclePress]
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>🚗</Text>
      <Text style={styles.emptyTitle}>
        {!isOnline 
          ? t('vehicles.noVehiclesOffline', 'Mode hors ligne - Aucun véhicule enregistré')
          : t('vehicles.noVehicles', 'Aucun véhicule enregistré')}
      </Text>
      <Text style={styles.emptySubtitle}>
        {!isOnline 
          ? t('vehicles.connectToView', 'Connectez-vous à internet pour voir vos véhicules')
          : t('vehicles.addFirstVehicle', 'Ajoutez votre premier véhicule pour commencer')}
      </Text>
      {isOnline && (
        <TouchableOpacity
          style={styles.addButton}
          onPress={handleAddVehicle}
          activeOpacity={0.8}
        >
          <Text style={styles.addButtonText}>
            {t('vehicles.addVehicle', 'Ajouter un véhicule')}
          </Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderLoadingState = () => (
    <View style={styles.loadingContainer}>
      <ActivityIndicator size="large" color={colors.primary} />
      <Text style={styles.loadingText}>
        {t('common.loading', 'Chargement...')}
      </Text>
    </View>
  );

  const keyExtractor = useCallback(
    (item: Vehicle) => item.id.toString(),
    []
  );

  // Handle offline data loading
  useEffect(() => {
    const loadVehicles = async () => {
      if (isOnline && vehicles) {
        // When online, use API data and cache it
        setDisplayVehicles(vehicles);
        dispatch(setVehicles(vehicles));
      } else if (!isOnline) {
        // When offline, use cached data
        const cachedVehicles = await getCachedVehicles();
        setDisplayVehicles(cachedVehicles);
        dispatch(setVehicles(cachedVehicles));
      }
    };

    loadVehicles();
  }, [isOnline, vehicles, getCachedVehicles, dispatch]);

  if (isLoading) {
    return renderLoadingState();
  }

  return (
    <View style={styles.container}>
      {/* Offline Indicator */}
      <OfflineIndicator compact={true} showSyncInfo={true} />
      
      <FlatList
        data={displayVehicles}
        renderItem={renderVehicleItem}
        keyExtractor={keyExtractor}
        contentContainerStyle={
          displayVehicles && displayVehicles.length > 0
            ? styles.listContent
            : styles.emptyListContent
        }
        ListEmptyComponent={renderEmptyState}
        refreshControl={
          <RefreshControl
            refreshing={isFetching || isSyncing}
            onRefresh={refetch}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
        showsVerticalScrollIndicator={false}
      />

      {/* Floating Add Button - only show when online */}
      {isOnline && displayVehicles && displayVehicles.length > 0 && (
        <TouchableOpacity
          style={styles.floatingButton}
          onPress={handleAddVehicle}
          activeOpacity={0.8}
        >
          <Text style={styles.floatingButtonText}>+</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundSecondary,
  },
  listContent: {
    paddingVertical: 8,
  },
  emptyListContent: {
    flexGrow: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.backgroundSecondary,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: colors.textSecondary,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 8,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: 24,
  },
  addButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 8,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  addButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  floatingButton: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  floatingButtonText: {
    fontSize: 32,
    fontWeight: '300',
    color: colors.white,
    lineHeight: 32,
  },
});
