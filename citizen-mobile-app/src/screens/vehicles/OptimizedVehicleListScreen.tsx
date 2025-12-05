import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  RefreshControl,
  TextInput,
} from 'react-native';
import { useGetVehiclesQuery } from '../../store/api/vehicleApi';
import { VehicleCard } from '../../components/vehicle/VehicleCard';
import { OptimizedFlatList, LoadingSpinner, OfflineIndicator } from '../../components/common';
import { useDebouncedSearch } from '../../hooks/useDebounce';
import { usePrefetchVehicleList } from '../../hooks/usePrefetch';
import { useRenderTime } from '../../utils/performance';
import { colors } from '../../theme/colors';
import { Vehicle } from '../../types/models';

const ITEM_HEIGHT = 120; // Height of VehicleCard

/**
 * Optimized Vehicle List Screen
 * Demonstrates performance optimizations including:
 * - Debounced search
 * - Optimized FlatList
 * - React.memo components
 * - Data prefetching
 * - Performance monitoring
 */
export const OptimizedVehicleListScreen: React.FC = () => {
  useRenderTime('OptimizedVehicleListScreen');
  
  const [searchQuery, setSearchQuery] = useState('');
  const prefetchVehicleList = usePrefetchVehicleList();

  // Debounced search
  const { debouncedQuery } = useDebouncedSearch({
    onSearch: (query: string) => {
      // Handle search logic here
      console.log('Searching for:', query);
    },
    delay: 300,
  });

  // Prefetch vehicle list when component mounts
  usePrefetchVehicleList();

  // Fetch vehicles with RTK Query
  const {
    data: vehicles,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useGetVehiclesQuery();

  // Filter vehicles based on search query
  const filteredVehicles = vehicles?.filter((vehicle: Vehicle) =>
    vehicle.plaque_immatriculation.toLowerCase().includes(debouncedQuery.toLowerCase()) ||
    vehicle.marque.toLowerCase().includes(debouncedQuery.toLowerCase()) ||
    vehicle.modele.toLowerCase().includes(debouncedQuery.toLowerCase())
  ) || [];

  // Handle vehicle card press
  const handleVehiclePress = useCallback((vehicle: Vehicle) => {
    // Navigate to vehicle detail screen
    // This would typically use navigation.navigate()
    console.log('Vehicle pressed:', vehicle.plaque_immatriculation);
  }, []);

  // Render vehicle card
  const renderVehicleCard = useCallback(({ item }: { item: Vehicle }) => (
    <VehicleCard
      vehicle={item}
      onPress={() => handleVehiclePress(item)}
    />
  ), [handleVehiclePress]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    refetch();
  }, [refetch]);

  if (isLoading) {
    return (
      <View style={styles.container}>
        <LoadingSpinner />
      </View>
    );
  }

  if (isError) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Erreur: {error && 'message' in error ? error.message : 'Une erreur est survenue'}</Text>
        <OfflineIndicator />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Search Input */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Rechercher un véhicule..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor={colors.gray500}
        />
      </View>

      {/* Vehicle List */}
      <OptimizedFlatList
        data={filteredVehicles}
        renderItem={renderVehicleCard}
        keyExtractor={(item: Vehicle) => item.plaque_immatriculation}
        itemHeight={ITEM_HEIGHT}
        windowSize={10}
        maxToRenderPerBatch={10}
        initialNumToRender={10}
        refreshControl={
          <RefreshControl
            refreshing={isFetching}
            onRefresh={handleRefresh}
            colors={[colors.primary]}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>
              {searchQuery ? 'Aucun véhicule trouvé' : 'Aucun véhicule enregistré'}
            </Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray200,
  },
  searchInput: {
    height: 44,
    borderWidth: 1,
    borderColor: colors.gray300,
    borderRadius: 8,
    paddingHorizontal: 12,
    fontSize: 16,
    color: colors.gray900,
  },
  errorText: {
    color: colors.error,
    fontSize: 16,
    textAlign: 'center',
    marginTop: 20,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: colors.gray600,
    textAlign: 'center',
  },
});