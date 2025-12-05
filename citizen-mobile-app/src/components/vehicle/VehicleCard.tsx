import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { Vehicle } from '../../types/models';
import vehicleService from '../../services/vehicleService';
import { colors } from '../../theme/colors';
import { OptimizedImage } from '../common/OptimizedImage';

interface VehicleCardProps {
  vehicle: Vehicle;
  onPress: () => void;
}

/**
 * Vehicle Card Component
 * Displays vehicle information in a card format with tax status badge
 * Optimized with React.memo for performance
 */
export const VehicleCard = React.memo<VehicleCardProps>(({ vehicle, onPress }) => {
  const statusColor = vehicleService.getTaxStatusColor(vehicle.tax_status);
  const statusLabel = vehicleService.getTaxStatusLabel(vehicle.tax_status);
  const displayName = vehicleService.getVehicleDisplayName(vehicle);

  const renderTaxInfo = () => {
    switch (vehicle.tax_status) {
      case 'PAYE':
        return (
          <Text style={styles.taxInfo}>
            Expire le: {vehicle.tax_due_date ? new Date(vehicle.tax_due_date).toLocaleDateString('fr-FR') : 'N/A'}
          </Text>
        );
      case 'IMPAYE':
        return (
          <Text style={styles.taxInfo}>
            Montant: {vehicle.tax_amount?.toLocaleString('fr-FR')} Ar
          </Text>
        );
      case 'EXPIRE':
        const daysLate = vehicle.tax_due_date
          ? Math.floor((Date.now() - new Date(vehicle.tax_due_date).getTime()) / (1000 * 60 * 60 * 24))
          : 0;
        return (
          <Text style={styles.taxInfo}>
            En retard de {daysLate} jour{daysLate > 1 ? 's' : ''}
          </Text>
        );
      case 'EXONERE':
        return <Text style={styles.taxInfo}>Véhicule exonéré</Text>;
      default:
        return null;
    }
  };

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.cardContent}>
        {/* Vehicle Image */}
        <View style={styles.imageContainer}>
          {vehicle.photo_url ? (
            <OptimizedImage
              source={{ uri: vehicle.photo_url }}
              style={styles.image}
              contentFit="cover"
              cachePolicy="memory-disk"
              placeholder="🚗"
            />
          ) : (
            <View style={[styles.image, styles.placeholderImage]}>
              <Text style={styles.placeholderText}>🚗</Text>
            </View>
          )}
        </View>

        {/* Vehicle Info */}
        <View style={styles.infoContainer}>
          <Text style={styles.plaque} numberOfLines={1}>
            {vehicle.plaque_immatriculation}
          </Text>
          <Text style={styles.vehicleName} numberOfLines={1}>
            {displayName}
          </Text>
          {renderTaxInfo()}
        </View>

        {/* Status Badge */}
        <View style={styles.badgeContainer}>
          <View style={[styles.badge, { backgroundColor: statusColor }]}>
            <Text style={styles.badgeText}>{statusLabel}</Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
});

// Display name for debugging
VehicleCard.displayName = 'VehicleCard';

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: 12,
    marginHorizontal: 16,
    marginVertical: 8,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardContent: {
    flexDirection: 'row',
    padding: 12,
    alignItems: 'center',
  },
  imageContainer: {
    marginRight: 12,
  },
  image: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  placeholderImage: {
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderText: {
    fontSize: 32,
  },
  infoContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  plaque: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.gray900,
    marginBottom: 4,
  },
  vehicleName: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.gray700,
    marginBottom: 4,
  },
  taxInfo: {
    fontSize: 12,
    color: colors.gray600,
  },
  badgeContainer: {
    marginLeft: 8,
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    minWidth: 80,
    alignItems: 'center',
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: colors.white,
  },
});
