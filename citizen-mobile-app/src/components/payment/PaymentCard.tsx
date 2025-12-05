import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { colors } from '../../theme/colors';

interface PaymentCardProps {
  payment: {
    id: number;
    amount: number;
    status: 'pending' | 'completed' | 'failed';
    vehicle_plaque: string;
    created_at: string;
    payment_method: string;
  };
  onPress: () => void;
}

/**
 * Payment Card Component
 * Displays payment information in a card format
 * Optimized with React.memo for performance
 */
export const PaymentCard = React.memo<PaymentCardProps>(({ payment, onPress }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#10b981'; // green
      case 'pending':
        return '#f59e0b'; // orange
      case 'failed':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return '✓ Payé';
      case 'pending':
        return '⏳ En attente';
      case 'failed':
        return '✗ Échoué';
      default:
        return 'Inconnu';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const formatAmount = (amount: number) => {
    return `${amount.toLocaleString('fr-FR')} Ar`;
  };

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.cardContent}>
        <View style={styles.infoContainer}>
          <Text style={styles.plaque} numberOfLines={1}>
            {payment.vehicle_plaque}
          </Text>
          <Text style={styles.amount}>
            {formatAmount(payment.amount)}
          </Text>
          <Text style={styles.date}>
            {formatDate(payment.created_at)}
          </Text>
          <Text style={styles.method}>
            {payment.payment_method}
          </Text>
        </View>

        {/* Status Badge */}
        <View style={styles.badgeContainer}>
          <View style={[styles.badge, { backgroundColor: getStatusColor(payment.status) }]}>
            <Text style={styles.badgeText}>{getStatusLabel(payment.status)}</Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
});

// Display name for debugging
PaymentCard.displayName = 'PaymentCard';

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
    padding: 16,
    alignItems: 'center',
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
  amount: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.gray800,
    marginBottom: 4,
  },
  date: {
    fontSize: 12,
    color: colors.gray600,
    marginBottom: 2,
  },
  method: {
    fontSize: 12,
    color: colors.gray600,
  },
  badgeContainer: {
    marginLeft: 12,
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