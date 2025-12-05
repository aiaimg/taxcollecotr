import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
  Modal,
  ScrollView,
  Alert,
  Share,
} from 'react-native';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { formatAPIError } from '../../api/interceptors';
import useNetworkStatus from '../../hooks/useNetworkStatus';
import OfflineIndicator from '../../components/common/OfflineIndicator';
import { setPayments } from '../../store/slices/paymentSlice';
import { 
  useGetPaymentHistoryQuery,
  selectFilteredPayments,
  selectPaymentLoading,
  selectPaymentError,
} from '../../store';
import { PaymentReceipt } from '../../types/tax';
import { PaymentMethod } from '../../types/models';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';
import { OptimizedImage } from '../../components/common/OptimizedImage';
// Simple icon components
const SmartphoneIcon = () => <Text style={styles.icon}>📱</Text>;
const CreditCardIcon = () => <Text style={styles.icon}>💳</Text>;
const DollarSignIcon = () => <Text style={styles.icon}>💵</Text>;
const CalendarIcon = () => <Text style={styles.icon}>📅</Text>;
const CarIcon = () => <Text style={styles.icon}>🚗</Text>;
const DownloadIcon = () => <Text style={styles.icon}>↓</Text>;
const XIcon = () => <Text style={styles.icon}>✕</Text>;

// Navigation types
import { PaymentStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<PaymentStackParamList, 'PaymentHistory'>;

interface FilterState {
  year?: number;
  vehicle?: string;
  status?: string;
}

export const PaymentHistoryScreen: React.FC<Props> = ({ navigation }) => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  
  const { data: payments, isLoading, error } = useGetPaymentHistoryQuery({ page: 1, pageSize: 50 });
  const filteredPayments = useAppSelector(selectFilteredPayments);
  const loading = useAppSelector(selectPaymentLoading);
  const paymentError = useAppSelector(selectPaymentError);
  const { isOnline, isSyncing, getCachedPayments } = useNetworkStatus();
  const [displayPayments, setDisplayPayments] = useState<PaymentReceipt[]>([]);
  
  const [selectedPayment, setSelectedPayment] = useState<PaymentReceipt | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [filters, setFilters] = useState<FilterState>({});

  // Handle offline data loading
  useEffect(() => {
    const loadPayments = async () => {
      if (isOnline && payments) {
        // When online, use API data and cache it
        setDisplayPayments(payments);
        dispatch(setPayments(payments));
      } else if (!isOnline) {
        // When offline, use cached data
        const cachedPayments = await getCachedPayments();
        setDisplayPayments(cachedPayments);
        dispatch(setPayments(cachedPayments));
      }
    };

    loadPayments();
  }, [isOnline, payments, getCachedPayments, dispatch]);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('fr-MG', {
      style: 'currency',
      currency: 'MGA',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getPaymentMethodIcon = (method: PaymentMethod) => {
    switch (method) {
      case 'MVOLA':
        return <SmartphoneIcon />;
      case 'STRIPE':
        return <CreditCardIcon />;
      case 'CASH':
        return <DollarSignIcon />;
      default:
        return <DollarSignIcon />;
    }
  };

  const getPaymentMethodName = (method: PaymentMethod): string => {
    switch (method) {
      case 'MVOLA':
        return 'MVola';
      case 'STRIPE':
        return 'Carte Bancaire';
      case 'CASH':
        return 'Espèces';
      default:
        return method;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
      case 'PAYE':
        return colors.success;
      case 'PENDING':
      case 'EN_ATTENTE':
        return colors.warning;
      case 'FAILED':
      case 'ECHOUE':
        return colors.error;
      default:
        return colors.textSecondary;
    }
  };

  const getStatusText = (status: string): string => {
    switch (status) {
      case 'COMPLETED':
      case 'PAYE':
        return 'Payé';
      case 'PENDING':
      case 'EN_ATTENTE':
        return 'En attente';
      case 'FAILED':
      case 'ECHOUE':
        return 'Échoué';
      default:
        return status;
    }
  };

  const handlePaymentPress = (payment: PaymentReceipt) => {
    setSelectedPayment(payment);
    setModalVisible(true);
  };

  const handleDownloadReceipt = () => {
    if (!selectedPayment || !selectedPayment.receipt_url) {
      Alert.alert('Erreur', 'Reçu non disponible');
      return;
    }

    // In a real app, you would download the PDF here
    Alert.alert(
      'Téléchargement',
      'Le reçu sera téléchargé dans votre galerie',
      [{ text: 'OK' }]
    );
  };

  const handleShareQR = async () => {
    if (!selectedPayment?.qr_code_url) return;
    try {
      await Share.share({
        message: `QR – ${selectedPayment.vehicle_plaque}\nMontant: ${formatCurrency(selectedPayment.amount_paid_ariary)}\nLien: ${selectedPayment.qr_code_url}`,
      });
    } catch (e) {
      Alert.alert('Erreur', "Impossible de partager le code QR");
    }
  };

  const handleSaveQR = async () => {
    if (!selectedPayment?.qr_code_url) return;
    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', "Autorisez l'accès à la galerie pour enregistrer le QR");
        return;
      }
      const fileUri = `${FileSystem.cacheDirectory}qr_${Date.now()}.png`;
      const download = await FileSystem.downloadAsync(selectedPayment.qr_code_url, fileUri);
      await MediaLibrary.saveAsync(download.uri);
      Alert.alert('Succès', 'Code QR enregistré dans la galerie');
    } catch (e) {
      Alert.alert('Erreur', "Impossible d'enregistrer le code QR");
    }
  };

  const renderPaymentItem = ({ item }: { item: PaymentReceipt }) => (
    <TouchableOpacity
      style={styles.paymentCard}
      onPress={() => handlePaymentPress(item)}
    >
      <View style={styles.paymentHeader}>
        <View style={styles.paymentMethod}>
          {getPaymentMethodIcon(item.payment_method)}
          <Text style={styles.paymentMethodText}>
            {getPaymentMethodName(item.payment_method)}
          </Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.payment_method) + '20' }]}>
          <Text style={[styles.statusText, { color: getStatusColor(item.payment_method) }]}>
            {getStatusText('COMPLETED')} {/* Assuming all history items are completed */}
          </Text>
        </View>
      </View>

      <View style={styles.paymentContent}>
        <View style={styles.infoRow}>
          <CarIcon />
          <Text style={styles.infoText}>{item.vehicle_plaque}</Text>
        </View>

        <View style={styles.infoRow}>
          <CalendarIcon />
          <Text style={styles.infoText}>{formatDate(item.paid_at)}</Text>
        </View>

        <View style={styles.amountRow}>
          <Text style={styles.amountLabel}>Montant:</Text>
          <Text style={styles.amountText}>{formatCurrency(item.amount_paid_ariary)}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <DollarSignIcon />
      <Text style={styles.emptyTitle}>
        {!isOnline 
          ? t('payments.noPaymentsOffline', 'Mode hors ligne - Aucun paiement')
          : t('payments.noPayments', 'Aucun paiement')}
      </Text>
      <Text style={styles.emptyText}>
        {!isOnline 
          ? t('payments.connectToViewPayments', 'Connectez-vous à internet pour voir vos paiements')
          : t('payments.noPaymentsMessage', "Vous n'avez effectué aucun paiement pour le moment.")}
      </Text>
      <TouchableOpacity style={styles.emptyButton} onPress={() => navigation.goBack()}>
        <Text style={styles.emptyButtonText}>Retour</Text>
      </TouchableOpacity>
    </View>
  );

  if (isLoading) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Chargement des paiements...</Text>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.errorContainer}>
        <Text style={styles.errorText}>Erreur lors du chargement des paiements</Text>
        <Text style={styles.errorDetails}>{formatAPIError(error)}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => {}}>
          <Text style={styles.retryButtonText}>Réessayer</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Offline Indicator */}
      <OfflineIndicator compact={true} showSyncInfo={true} />
      
      <View style={styles.header}>
        <Text style={styles.title}>Historique des Paiements</Text>
        <Text style={styles.subtitle}>
          {displayPayments.length} paiement{displayPayments.length !== 1 ? 's' : ''}
        </Text>
      </View>

      <FlatList
        data={displayPayments}
        renderItem={renderPaymentItem}
        keyExtractor={(item) => item.payment_id.toString()}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={renderEmptyState}
        showsVerticalScrollIndicator={false}
      />

      {/* Payment Detail Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Détails du Paiement</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <XIcon />
              </TouchableOpacity>
            </View>

            {selectedPayment && (
              <ScrollView style={styles.modalBody}>
                <View style={styles.modalSection}>
                  <Text style={styles.modalSectionTitle}>Informations du paiement</Text>
                  
                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>ID de transaction:</Text>
                    <Text style={styles.modalValue}>{selectedPayment.transaction_id}</Text>
                  </View>

                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Méthode de paiement:</Text>
                    <Text style={styles.modalValue}>
                      {getPaymentMethodName(selectedPayment.payment_method)}
                    </Text>
                  </View>

                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Date et heure:</Text>
                    <Text style={styles.modalValue}>
                      {formatDate(selectedPayment.paid_at)}
                    </Text>
                  </View>
                </View>

                <View style={styles.modalSection}>
                  <Text style={styles.modalSectionTitle}>Informations du véhicule</Text>
                  
                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Plaque d'immatriculation:</Text>
                    <Text style={styles.modalValue}>{selectedPayment.vehicle_plaque}</Text>
                  </View>

                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Marque:</Text>
                    <Text style={styles.modalValue}>{selectedPayment.vehicle_details.marque}</Text>
                  </View>

                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Modèle:</Text>
                    <Text style={styles.modalValue}>{selectedPayment.vehicle_details.modele}</Text>
                  </View>

                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Puissance fiscale:</Text>
                    <Text style={styles.modalValue}>
                      {selectedPayment.vehicle_details.puissance_fiscale_cv} CV
                    </Text>
                  </View>

                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Année fiscale:</Text>
                    <Text style={styles.modalValue}>{selectedPayment.fiscal_year}</Text>
                  </View>
                </View>

                <View style={styles.modalSection}>
                  <Text style={styles.modalSectionTitle}>Détail des taxes</Text>
                  
                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Montant de base:</Text>
                    <Text style={styles.modalValue}>
                      {formatCurrency(selectedPayment.tax_breakdown.calculated_base_ariary)}
                    </Text>
                  </View>

                  <View style={styles.modalInfoRow}>
                    <Text style={styles.modalLabel}>Montant total payé:</Text>
                    <Text style={[styles.modalValue, styles.amountValue]}>
                      {formatCurrency(selectedPayment.amount_paid_ariary)}
                    </Text>
                  </View>
                </View>

                {selectedPayment.qr_code_url && (
                  <View style={styles.modalSection}>
                    <Text style={styles.modalSectionTitle}>Code QR</Text>
                    <Text style={styles.modalText}>
                      Ce code QR peut être utilisé pour vérifier votre paiement:
                    </Text>
                    <TouchableOpacity
                      activeOpacity={0.8}
                      onPress={() =>
                        navigation.navigate('QRCodeViewer', {
                          imageUrl: selectedPayment.qr_code_url,
                          vehiclePlaque: selectedPayment.vehicle_plaque,
                          paidAt: selectedPayment.paid_at,
                          amount: formatCurrency(selectedPayment.amount_paid_ariary),
                        })
                      }
                    >
                      <OptimizedImage
                        source={{ uri: selectedPayment.qr_code_url }}
                        style={styles.qrImage}
                        contentFit="contain"
                      />
                    </TouchableOpacity>
                    <View style={styles.qrActionsRow}>
                      <TouchableOpacity style={styles.qrActionButton} onPress={handleShareQR}>
                        <Text style={[styles.icon, { color: colors.primary }]}>↗</Text>
                        <Text style={styles.qrActionText}>Partager le QR</Text>
                      </TouchableOpacity>
                      <TouchableOpacity style={styles.qrActionButton} onPress={handleSaveQR}>
                        <Text style={[styles.icon, { color: colors.primary }]}>↓</Text>
                        <Text style={styles.qrActionText}>Enregistrer le QR</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                )}

                <TouchableOpacity style={styles.downloadButton} onPress={handleDownloadReceipt}>
                  <DownloadIcon />
                  <Text style={styles.downloadButtonText}>Télécharger le reçu</Text>
                </TouchableOpacity>
              </ScrollView>
            )}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
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
  loadingText: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: spacing.md,
  },
  errorText: {
    ...typography.h3,
    color: colors.error,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  errorDetails: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  retryButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  retryButtonText: {
    ...typography.button,
    color: colors.white,
  },
  header: {
    padding: spacing.md,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  title: {
    ...typography.h1,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
  },
  listContent: {
    padding: spacing.md,
  },
  paymentCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  paymentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  paymentMethod: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  paymentMethodText: {
    ...typography.body,
    color: colors.textPrimary,
    marginLeft: spacing.sm,
  },
  statusBadge: {
    borderRadius: 12,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  statusText: {
    ...typography.small,
    fontWeight: '600',
  },
  paymentContent: {
    marginBottom: spacing.sm,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  infoText: {
    ...typography.body,
    color: colors.textPrimary,
    marginLeft: spacing.sm,
  },
  amountRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  amountLabel: {
    ...typography.body,
    color: colors.textSecondary,
  },
  amountText: {
    ...typography.h3,
    color: colors.primary,
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  emptyTitle: {
    ...typography.h2,
    color: colors.textPrimary,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  emptyButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  emptyButtonText: {
    ...typography.button,
    color: colors.white,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: colors.white,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  modalBody: {
    padding: spacing.md,
  },
  modalSection: {
    marginBottom: spacing.lg,
  },
  modalSectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  modalInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  modalLabel: {
    ...typography.body,
    color: colors.textSecondary,
  },
  modalValue: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  amountValue: {
    color: colors.primary,
    fontWeight: 'bold',
  },
  modalText: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  qrCodeText: {
    ...typography.mono,
    color: colors.primary,
    backgroundColor: colors.background,
    padding: spacing.sm,
    borderRadius: 4,
    textAlign: 'center',
  },
  qrImage: {
    width: 160,
    height: 160,
    backgroundColor: colors.background,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    alignSelf: 'center',
  },
  qrActionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-evenly',
    marginTop: spacing.sm,
  },
  qrActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 8,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  qrActionText: {
    ...typography.button,
    color: colors.primary,
    marginLeft: spacing.xs,
  },
  downloadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: spacing.md,
    marginTop: spacing.md,
  },
  downloadButtonText: {
    ...typography.button,
    color: colors.white,
    marginLeft: spacing.sm,
  },
  icon: {
    fontSize: 20,
    marginRight: spacing.sm,
  },
});