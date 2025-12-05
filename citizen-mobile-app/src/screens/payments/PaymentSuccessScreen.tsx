import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Share,
  Alert,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { 
  useGetPaymentReceiptQuery,
  addPayment,
  selectCurrentPayment,
} from '../../store';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';
import { OptimizedImage } from '../../components/common/OptimizedImage';

// Navigation types
import { PaymentStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<PaymentStackParamList, 'PaymentSuccess'>;

export const PaymentSuccessScreen: React.FC<Props> = ({ navigation, route }) => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { paymentId, amount, vehiclePlaque } = route.params;
  
  const currentPayment = useAppSelector(selectCurrentPayment);
  const { data: receipt, isLoading } = useGetPaymentReceiptQuery(paymentId, {
    skip: !paymentId,
  });

  useEffect(() => {
    if (receipt) {
      // Add the completed payment to the history
      dispatch(addPayment(receipt));
    }
  }, [receipt, dispatch]);

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
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleShareReceipt = async () => {
    if (!receipt) return;

    try {
      const message = `
Reçu de Paiement - Tax Collector

Véhicule: ${receipt.vehicle_plaque}
Montant: ${formatCurrency(receipt.amount_paid_ariary)}
Date: ${formatDate(receipt.paid_at)}
Méthode: ${receipt.payment_method}
Transaction: ${receipt.transaction_id}

Merci pour votre paiement!
      `.trim();

      await Share.share({
        message,
        title: 'Reçu de Paiement',
      });
    } catch (error) {
      console.error('Error sharing receipt:', error);
      Alert.alert('Erreur', 'Impossible de partager le reçu');
    }
  };

  const handleOpenQRViewer = () => {
    if (!receipt?.qr_code_url) return;
    navigation.navigate('QRCodeViewer', {
      imageUrl: receipt.qr_code_url,
      vehiclePlaque,
      paidAt: receipt.paid_at,
      amount: formatCurrency(amount),
    });
  };

  const handleDownloadReceipt = () => {
    if (!receipt || !receipt.receipt_url) {
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

  const handleGoHome = () => {
    navigation.popToTop();
    navigation.goBack();
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Chargement du reçu...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.successHeader}>
          <Text style={[styles.successIcon, { color: colors.success }]}>✓</Text>
          <Text style={styles.successTitle}>Paiement Réussi!</Text>
          <Text style={styles.successSubtitle}>
            Votre paiement a été traité avec succès
          </Text>
        </View>

        <View style={styles.receiptCard}>
          <View style={styles.receiptHeader}>
            <Text style={styles.receiptTitle}>Reçu de Paiement</Text>
            <Text style={styles.receiptDate}>
              {receipt ? formatDate(receipt.paid_at) : formatDate(new Date().toISOString())}
            </Text>
          </View>

          <View style={styles.receiptContent}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Véhicule:</Text>
              <Text style={styles.infoValue}>{vehiclePlaque}</Text>
            </View>

            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Montant payé:</Text>
              <Text style={styles.amountValue}>{formatCurrency(amount)}</Text>
            </View>

            {receipt && (
              <>
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>Méthode de paiement:</Text>
                  <Text style={styles.infoValue}>{receipt.payment_method}</Text>
                </View>

                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>ID de transaction:</Text>
                  <Text style={styles.infoValue}>{receipt.transaction_id}</Text>
                </View>

                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>Année fiscale:</Text>
                  <Text style={styles.infoValue}>{receipt.fiscal_year}</Text>
                </View>
              </>
            )}
          </View>

          {receipt?.qr_code_url && (
            <View style={styles.qrCodeSection}>
              <Text style={styles.qrCodeTitle}>Code QR de vérification</Text>
              <Text style={styles.qrCodeText}>
                Ce code QR peut être utilisé pour vérifier votre paiement
              </Text>
              <TouchableOpacity onPress={handleOpenQRViewer} activeOpacity={0.8}>
                <OptimizedImage
                  source={{ uri: receipt.qr_code_url }}
                  style={styles.qrImage}
                  contentFit="contain"
                />
              </TouchableOpacity>
            </View>
          )}
        </View>

        <View style={styles.actionsContainer}>
          <TouchableOpacity style={styles.actionButton} onPress={handleShareReceipt}>
            <Text style={[styles.iconText, { color: colors.primary }]}>↗</Text>
            <Text style={styles.actionButtonText}>Partager</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton} onPress={handleDownloadReceipt}>
            <Text style={[styles.iconText, { color: colors.primary }]}>↓</Text>
            <Text style={styles.actionButtonText}>Télécharger</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.homeButton} onPress={handleGoHome}>
          <Text style={[styles.iconText, { color: colors.white }]}>🏠</Text>
          <Text style={styles.homeButtonText}>Retour à l'accueil</Text>
        </TouchableOpacity>
      </ScrollView>
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
  },
  scrollContent: {
    padding: spacing.md,
  },
  successHeader: {
    alignItems: 'center',
    marginBottom: spacing.lg,
    paddingTop: spacing.xl,
  },
  successTitle: {
    ...typography.h1,
    color: colors.success,
    marginTop: spacing.md,
    marginBottom: spacing.xs,
  },
  successSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  receiptCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.lg,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  receiptHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  receiptTitle: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  receiptDate: {
    ...typography.small,
    color: colors.textSecondary,
  },
  receiptContent: {
    marginBottom: spacing.md,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  infoLabel: {
    ...typography.body,
    color: colors.textSecondary,
  },
  infoValue: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  amountValue: {
    ...typography.h3,
    color: colors.primary,
    fontWeight: 'bold',
  },
  qrCodeSection: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    alignItems: 'center',
  },
  qrCodeTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  qrCodeText: {
    ...typography.small,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  qrCodePlaceholder: {
    display: 'none',
  },
  qrCodePlaceholderText: {
    ...typography.small,
    color: colors.textSecondary,
  },
  qrImage: {
    width: 160,
    height: 160,
    backgroundColor: colors.background,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.white,
    borderRadius: 8,
    paddingVertical: spacing.md,
    marginHorizontal: spacing.xs,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  actionButtonText: {
    ...typography.button,
    color: colors.primary,
    marginLeft: spacing.xs,
  },
  homeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: spacing.md,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  homeButtonText: {
    ...typography.button,
    color: colors.white,
    marginLeft: spacing.xs,
  },
  iconText: {
    fontSize: 20,
    fontWeight: '600' as const,
    marginRight: spacing.xs,
  },
  successIcon: {
    fontSize: 80,
    fontWeight: 'bold' as const,
    marginBottom: spacing.md,
  },
});