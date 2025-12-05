import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useNavigation } from '@react-navigation/native';
import { RootStackParamList } from '../../types/navigation';
import { selectCurrentUser } from '../../store';
import { useGetVehiclesQuery } from '../../store/api/vehicleApi';
import { useGetPaymentHistoryQuery } from '../../store/api/taxApi';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';

type DashboardNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Main'>;

const DashboardScreen: React.FC = () => {
  const { t } = useTranslation();
  const navigation = useNavigation<DashboardNavigationProp>();
  const user = useSelector(selectCurrentUser);
  
  // Get data from API
  const { data: vehicles, isLoading: vehiclesLoading } = useGetVehiclesQuery();
  const { data: payments, isLoading: paymentsLoading } = useGetPaymentHistoryQuery({ page: 1, pageSize: 10 });

  const vehicleCount = vehicles?.length || 0;
  const taxableVehicles = vehicles?.filter((v: any) => v.tax_status === 'pending')?.length || 0;
  const recentPayments = payments?.slice(0, 3) || [];
  const upcomingPayments = vehicles?.filter((v: any) => v.tax_due_date && new Date(v.tax_due_date) > new Date()).slice(0, 3) || [];

  const handleAddVehicle = () => {
    navigation.navigate('VehicleStack', { screen: 'AddVehicle' });
  };

  const handlePayTax = () => {
    if (vehicles && vehicles.length > 0) {
      const firstVehicle = vehicles[0];
      navigation.navigate('PaymentStack', { 
        screen: 'PaymentMethod', 
        params: { 
          vehiclePlaque: firstVehicle.plaque_immatriculation,
          amount: firstVehicle.tax_amount || 0,
          fiscalYear: new Date().getFullYear()
        }
      });
    }
  };

  const handleViewAllVehicles = () => {
    navigation.navigate('Main', { screen: 'Vehicles' });
  };

  const handleViewAllPayments = () => {
    navigation.navigate('PaymentStack', { screen: 'PaymentHistory' });
  };

  if (vehiclesLoading || paymentsLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.welcomeText}>
          {t('dashboard.welcome', { name: user?.first_name || 'Utilisateur' })}
        </Text>
        <Text style={styles.subtitleText}>
          {t('dashboard.subtitle')}
        </Text>
      </View>

      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{vehicleCount}</Text>
          <Text style={styles.statLabel}>{t('dashboard.vehicles_total')}</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{taxableVehicles}</Text>
          <Text style={styles.statLabel}>{t('dashboard.taxes_pending')}</Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <Text style={styles.sectionTitle}>{t('dashboard.quick_actions')}</Text>
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton} onPress={handleAddVehicle}>
            <Text style={styles.actionButtonText}>{t('dashboard.add_vehicle')}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton} onPress={handlePayTax}>
            <Text style={styles.actionButtonText}>{t('dashboard.pay_tax')}</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Recent Payments */}
      <View style={styles.sectionContainer}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>{t('dashboard.recent_payments')}</Text>
          <TouchableOpacity onPress={handleViewAllPayments}>
            <Text style={styles.seeAllText}>{t('common.see_all')}</Text>
          </TouchableOpacity>
        </View>
        {recentPayments.length > 0 ? (
          recentPayments.map((payment: any, index: number) => (
            <View key={payment.id || index} style={styles.paymentItem}>
              <View style={styles.paymentInfo}>
                <Text style={styles.paymentVehicle}>{payment.vehicle_plaque}</Text>
                <Text style={styles.paymentDate}>{new Date(payment.created_at).toLocaleDateString()}</Text>
              </View>
              <Text style={styles.paymentAmount}>{payment.amount.toLocaleString()} Ar</Text>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>{t('dashboard.no_recent_payments')}</Text>
        )}
      </View>

      {/* Upcoming Payments */}
      <View style={styles.sectionContainer}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>{t('dashboard.upcoming_payments')}</Text>
          <TouchableOpacity onPress={handleViewAllVehicles}>
            <Text style={styles.seeAllText}>{t('common.see_all')}</Text>
          </TouchableOpacity>
        </View>
        {upcomingPayments.length > 0 ? (
          upcomingPayments.map((vehicle: any, index: number) => (
            <View key={vehicle.id || index} style={styles.paymentItem}>
              <View style={styles.paymentInfo}>
                <Text style={styles.paymentVehicle}>{vehicle.plaque}</Text>
                <Text style={styles.paymentDate}>
                  {t('dashboard.due_date')}: {new Date(vehicle.tax_due_date).toLocaleDateString()}
                </Text>
              </View>
              <Text style={styles.paymentAmount}>{vehicle.tax_amount?.toLocaleString() || '0'} Ar</Text>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>{t('dashboard.no_upcoming_payments')}</Text>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  welcomeText: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.text.primary,
    marginBottom: spacing.xs,
  },
  subtitleText: {
    fontSize: typography.fontSize.base,
    color: colors.text.secondary,
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    gap: spacing.md,
  },
  statCard: {
    flex: 1,
    backgroundColor: colors.white,
    padding: spacing.lg,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  statLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
    textAlign: 'center',
  },
  actionsContainer: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: spacing.md,
    marginTop: spacing.md,
  },
  actionButton: {
    flex: 1,
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
  },
  sectionContainer: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold,
    color: colors.text.primary,
  },
  seeAllText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
  },
  paymentItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: colors.white,
    padding: spacing.md,
    borderRadius: 8,
    marginBottom: spacing.sm,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  paymentInfo: {
    flex: 1,
  },
  paymentVehicle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
    color: colors.text.primary,
    marginBottom: spacing.xs,
  },
  paymentDate: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
  },
  paymentAmount: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
  },
  emptyText: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
    textAlign: 'center',
    paddingVertical: spacing.lg,
  },
});

export default DashboardScreen;