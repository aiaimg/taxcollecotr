import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  Image,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import {
  useGetVehicleQuery,
  useGetVehicleTaxInfoQuery,
  useDeleteVehicleMutation,
} from '../../store/api/vehicleApi';
import { useGetPaymentHistoryQuery, useGetPaymentStatusQuery } from '../../store';
import { OptimizedImage } from '../../components/common/OptimizedImage';
import vehicleService from '../../services/vehicleService';
import { colors } from '../../theme/colors';
import { useTranslation } from 'react-i18next';
import useNetworkStatus from '../../hooks/useNetworkStatus';
import OfflineIndicator from '../../components/common/OfflineIndicator';

type RouteParams = {
  VehicleDetail: {
    plaque: string;
  };
};

type NavigationProp = NativeStackNavigationProp<any>;

/**
 * Vehicle Detail Screen
 * Displays detailed information about a vehicle including tax info
 */
export const VehicleDetailScreen: React.FC = () => {
  const route = useRoute<RouteProp<RouteParams, 'VehicleDetail'>>();
  const navigation = useNavigation<NavigationProp>();
  const { t } = useTranslation();
  const { plaque } = route.params;
  const { isOnline } = useNetworkStatus();

  const { data: vehicle, isLoading: vehicleLoading } = useGetVehicleQuery(plaque);
  const { data: taxInfo, isLoading: taxLoading } = useGetVehicleTaxInfoQuery(plaque);
  const [deleteVehicle, { isLoading: deleting }] = useDeleteVehicleMutation();
  const { data: paymentHistory } = useGetPaymentHistoryQuery({ page: 1, pageSize: 50 });
  const latestReceipt = paymentHistory
    ?.filter((p) => p.vehicle_plaque === plaque)
    .sort((a, b) => new Date(b.paid_at).getTime() - new Date(a.paid_at).getTime())[0];
  const { data: latestStatus } = useGetPaymentStatusQuery(latestReceipt?.payment_id ?? 0, {
    skip: !latestReceipt,
  });

  const handlePayNow = () => {
    if (!isOnline) {
      Alert.alert(
        t('common.offline', 'Mode hors ligne'),
        t('payments.offlinePaymentMessage', 'Les paiements nécessitent une connexion internet. Veuillez vous connecter pour continuer.'),
        [{ text: t('common.ok', 'OK') }]
      );
      return;
    }
    
    if (vehicle) {
      navigation.navigate('PaymentMethod', { vehiclePlaque: vehicle.plaque_immatriculation });
    }
  };

  const handleDelete = () => {
    Alert.alert(
      t('vehicles.deleteVehicle', 'Supprimer le véhicule'),
      t('vehicles.deleteConfirm', 'Êtes-vous sûr de vouloir supprimer ce véhicule ?'),
      [
        {
          text: t('common.cancel', 'Annuler'),
          style: 'cancel',
        },
        {
          text: t('common.delete', 'Supprimer'),
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteVehicle(plaque).unwrap();
              navigation.goBack();
            } catch (error) {
              Alert.alert(
                t('common.error', 'Erreur'),
                'Impossible de supprimer le véhicule'
              );
            }
          },
        },
      ]
    );
  };

  if (vehicleLoading || taxLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>{t('common.loading', 'Chargement...')}</Text>
      </View>
    );
  }

  if (!vehicle) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Véhicule non trouvé</Text>
      </View>
    );
  }

  const statusColor = vehicleService.getTaxStatusColor(vehicle.tax_status);
  const statusLabel = vehicleService.getTaxStatusLabel(vehicle.tax_status);
  const displayName = vehicleService.getVehicleDisplayName(vehicle);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Offline Indicator */}
      <OfflineIndicator compact={true} showSyncInfo={true} />
      
      {/* Vehicle Image */}
      <View style={styles.imageContainer}>
        {vehicle.photo_url ? (
          <Image
            source={{ uri: vehicle.photo_url }}
            style={styles.image}
            resizeMode="cover"
          />
        ) : (
          <View style={[styles.image, styles.placeholderImage]}>
            <Text style={styles.placeholderText}>🚗</Text>
          </View>
        )}
      </View>

      {/* Vehicle Info Card */}
      <View style={styles.card}>
        <View style={styles.headerRow}>
          <View style={styles.headerInfo}>
            <Text style={styles.plaque}>{vehicle.plaque_immatriculation}</Text>
            <Text style={styles.vehicleName}>{displayName}</Text>
          </View>
          <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
            <Text style={styles.statusText}>{statusLabel}</Text>
          </View>
        </View>

        <View style={styles.divider} />

        {/* Basic Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Informations de base</Text>
          <InfoRow label="Couleur" value={vehicle.couleur} />
          {vehicle.vin && <InfoRow label="VIN" value={vehicle.vin} />}
          <InfoRow label="Type" value={vehicle.type_vehicule.nom} />
          <InfoRow label="Catégorie" value={vehicle.categorie_vehicule} />
        </View>

        <View style={styles.divider} />

        {/* Technical Specifications */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Spécifications techniques</Text>
          <InfoRow label="Puissance fiscale" value={`${vehicle.puissance_fiscale_cv} CV`} />
          <InfoRow label="Cylindrée" value={`${vehicle.cylindree_cm3} cm³`} />
          <InfoRow label="Source d'énergie" value={vehicle.source_energie} />
          <InfoRow
            label="Date de circulation"
            value={new Date(vehicle.date_premiere_circulation).toLocaleDateString('fr-FR')}
          />
        </View>
      </View>

      {/* Tax Information Card */}
      {taxInfo && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Informations fiscales</Text>
          
          {taxInfo.est_exonere ? (
            <View style={styles.exemptContainer}>
              <Text style={styles.exemptTitle}>Véhicule exonéré</Text>
              {taxInfo.details?.exemption_reason && (
                <Text style={styles.exemptReason}>{taxInfo.details.exemption_reason}</Text>
              )}
            </View>
          ) : (
            <>
              <View style={styles.taxAmountContainer}>
                <Text style={styles.taxLabel}>Montant de la taxe</Text>
                <Text style={styles.taxAmount}>
                  {taxInfo.montant_du_ariary.toLocaleString('fr-FR')} Ar
                </Text>
              </View>
              
              {taxInfo.date_limite && (
                <InfoRow
                  label="Date limite"
                  value={new Date(taxInfo.date_limite).toLocaleDateString('fr-FR')}
                />
              )}
              
              <InfoRow label="Année fiscale" value={taxInfo.annee_fiscale.toString()} />
              
              {taxInfo.grille_tarifaire && (
                <View style={styles.gridInfo}>
                  <Text style={styles.gridLabel}>Grille tarifaire</Text>
                  <Text style={styles.gridValue}>
                    {taxInfo.grille_tarifaire.puissance_min_cv} - {taxInfo.grille_tarifaire.puissance_max_cv} CV
                  </Text>
                </View>
              )}
            </>
          )}
        </View>
      )}

      {/* QR Code and Receipt (if paid) */}
      {vehicle.tax_status === 'PAYE' ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Preuve de paiement</Text>
          {latestReceipt?.qr_code_url ? (
            <>
              <TouchableOpacity
                activeOpacity={0.8}
                onPress={() =>
                  navigation.navigate('QRCodeViewer', {
                    imageUrl: latestReceipt.qr_code_url,
                    vehiclePlaque: vehicle.plaque_immatriculation,
                    paidAt: latestReceipt.paid_at,
                    expiresAt: latestStatus?.qr_code?.expires_at,
                    amount: `${latestReceipt.amount_paid_ariary.toLocaleString('fr-FR')} Ar`,
                  })
                }
              >
                <OptimizedImage
                  source={{ uri: latestReceipt.qr_code_url }}
                  style={styles.qrImage}
                  contentFit="contain"
                />
              </TouchableOpacity>
              <View style={styles.qrMetaRow}>
                <Text style={styles.metaLabel}>Généré le</Text>
                <Text style={styles.metaValue}>
                  {new Date(latestReceipt.paid_at).toLocaleDateString('fr-FR')} {new Date(latestReceipt.paid_at).toLocaleTimeString('fr-FR')}
                </Text>
              </View>
              {latestStatus?.qr_code?.expires_at && (
                <View style={styles.qrMetaRow}>
                  <Text style={styles.metaLabel}>Expire le</Text>
                  <Text style={styles.metaValue}>
                    {new Date(latestStatus.qr_code.expires_at).toLocaleDateString('fr-FR')} {new Date(latestStatus.qr_code.expires_at).toLocaleTimeString('fr-FR')}
                  </Text>
                </View>
              )}
            </>
          ) : (
            <Text style={styles.noQrText}>Aucun QR code disponible</Text>
          )}
        </View>
      ) : (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Preuve de paiement</Text>
          <Text style={styles.noQrText}>Aucun QR code disponible - Payez votre taxe pour obtenir un QR code</Text>
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        {vehicle.tax_status === 'IMPAYE' || vehicle.tax_status === 'EXPIRE' ? (
          <TouchableOpacity
            style={styles.payButton}
            onPress={handlePayNow}
            activeOpacity={0.8}
          >
            <Text style={styles.payButtonText}>Payer maintenant</Text>
          </TouchableOpacity>
        ) : null}

        <TouchableOpacity
          style={styles.deleteButton}
          onPress={handleDelete}
          disabled={deleting}
          activeOpacity={0.8}
        >
          {deleting ? (
            <ActivityIndicator size="small" color={colors.error} />
          ) : (
            <Text style={styles.deleteButtonText}>Supprimer le véhicule</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

interface InfoRowProps {
  label: string;
  value: string;
}

const InfoRow: React.FC<InfoRowProps> = ({ label, value }) => (
  <View style={styles.infoRow}>
    <Text style={styles.infoLabel}>{label}</Text>
    <Text style={styles.infoValue}>{value}</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundSecondary,
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.backgroundSecondary,
  },
  errorText: {
    fontSize: 16,
    color: colors.error,
  },
  imageContainer: {
    width: '100%',
    height: 250,
    backgroundColor: colors.gray200,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  placeholderImage: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.gray100,
  },
  placeholderText: {
    fontSize: 64,
  },
  card: {
    backgroundColor: colors.white,
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 12,
    padding: 16,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 16,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerInfo: {
    flex: 1,
  },
  plaque: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.textPrimary,
    marginBottom: 4,
  },
  vehicleName: {
    fontSize: 16,
    fontWeight: '500',
    color: colors.gray700,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginLeft: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.white,
  },
  divider: {
    height: 1,
    backgroundColor: colors.border,
    marginVertical: 16,
  },
  section: {
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.gray700,
    marginBottom: 12,
    textTransform: 'uppercase',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textPrimary,
  },
  taxAmountContainer: {
    alignItems: 'center',
    paddingVertical: 16,
    marginBottom: 16,
    backgroundColor: colors.backgroundSecondary,
    borderRadius: 8,
  },
  taxLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  taxAmount: {
    fontSize: 32,
    fontWeight: '700',
    color: colors.primary,
  },
  gridInfo: {
    marginTop: 12,
    padding: 12,
    backgroundColor: colors.backgroundSecondary,
    borderRadius: 8,
  },
  gridLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  gridValue: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textPrimary,
  },
  exemptContainer: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  exemptTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.info,
    marginBottom: 8,
  },
  exemptReason: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  receiptButton: {
    backgroundColor: colors.primary,
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  receiptButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  qrImage: {
    width: 160,
    height: 160,
    backgroundColor: colors.backgroundSecondary,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    alignSelf: 'center',
    marginBottom: 12,
  },
  qrMetaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
  },
  metaLabel: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  metaValue: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textPrimary,
  },
  noQrText: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  actionsContainer: {
    marginHorizontal: 16,
    marginTop: 16,
    marginBottom: 32,
  },
  payButton: {
    backgroundColor: colors.primary,
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  payButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  deleteButton: {
    backgroundColor: colors.white,
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.error,
  },
  deleteButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.error,
  },
});
