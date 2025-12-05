import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  ActivityIndicator,
  Alert,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { 
  useInitiatePaymentMutation, 
  useLazyGetPaymentStatusQuery,
  setCurrentCalculation,
  setPaymentId,
  setPaymentStatus,
  resetCurrentPayment,
  selectCurrentPayment,
} from '../../store';
import { PaymentMethod } from '../../types/models';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';
import { formatAPIError } from '../../api/interceptors';
import { mvolaPaymentService, stripePaymentService } from '../../services';

// Navigation types
import { PaymentStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<PaymentStackParamList, 'PaymentProcessing'>;

interface PaymentFormData {
  phoneNumber?: string;
  cardNumber?: string;
  expiryMonth?: string;
  expiryYear?: string;
  cvc?: string;
  cardholderName?: string;
}

export const PaymentProcessingScreen: React.FC<Props> = ({ navigation, route }) => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const currentPayment = useAppSelector(selectCurrentPayment);
  
  const { amount, vehiclePlaque, fiscalYear, paymentMethod } = route.params;
  
  const [initiatePayment, { isLoading: isInitiating }] = useInitiatePaymentMutation();
  const [getPaymentStatus] = useLazyGetPaymentStatusQuery();
  
  const [formData, setFormData] = useState<PaymentFormData>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [cardErrors, setCardErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    return () => {
      // Cleanup polling on unmount
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
      mvolaPaymentService.stopAllPolling();
    };
  }, [pollingInterval]);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('fr-MG', {
      style: 'currency',
      currency: 'MGA',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const validateForm = (): boolean => {
    if (paymentMethod === 'MVOLA') {
      if (!formData.phoneNumber) {
        Alert.alert('Erreur', 'Veuillez entrer votre numéro de téléphone');
        return false;
      }
      if (!mvolaPaymentService.validatePhoneNumber(formData.phoneNumber)) {
        Alert.alert('Erreur', 'Format de numéro invalide. Utilisez +261XXXXXXXXX');
        return false;
      }
    } else if (paymentMethod === 'STRIPE') {
      const validation = stripePaymentService.validateCardDetails(
        formData.cardNumber || '',
        parseInt(formData.expiryMonth || '0'),
        parseInt(formData.expiryYear || '0'),
        formData.cvc || ''
      );
      
      if (!validation.isValid) {
        setCardErrors(validation.errors);
        return false;
      }
      setCardErrors({});
    }
    return true;
  };

  const handlePayment = async () => {
    if (!validateForm()) {
      return;
    }

    setIsProcessing(true);
    
    try {
      // Initiate payment
      const initiationRequest = {
        vehicle_plaque: vehiclePlaque,
        fiscal_year: fiscalYear,
        amount_ariary: amount,
        payment_method: paymentMethod,
        phone_number: paymentMethod === 'MVOLA' ? formData.phoneNumber : undefined,
      };

      const response = await initiatePayment(initiationRequest).unwrap();
      
      // Store payment ID in Redux
      dispatch(setPaymentId({
        paymentId: response.payment_id,
        transactionId: response.transaction_id,
      }));

      // Handle different payment flows
      if (paymentMethod === 'MVOLA') {
        await handleMVolaPayment(response);
      } else if (paymentMethod === 'STRIPE') {
        await handleStripePayment(response);
      }

    } catch (error) {
      console.error('Payment initiation error:', error);
      Alert.alert(
        'Erreur de paiement',
        formatAPIError(error)
      );
      setIsProcessing(false);
    }
  };

  const handleMVolaPayment = async (response: any) => {
    // Start polling for MVola payment status
    const interval = setInterval(async () => {
      try {
        const statusResponse = await getPaymentStatus(response.payment_id).unwrap();
        
        dispatch(setPaymentStatus({ status: statusResponse.status }));
        
        if (statusResponse.status === 'COMPLETED') {
          clearInterval(interval);
          setPollingInterval(null);
          navigation.replace('PaymentSuccess', {
            paymentId: response.payment_id,
            amount: amount,
            vehiclePlaque: vehiclePlaque,
          });
        } else if (statusResponse.status === 'FAILED' || statusResponse.status === 'CANCELLED') {
          clearInterval(interval);
          setPollingInterval(null);
          Alert.alert(
            'Paiement échoué',
            statusResponse.failure_reason || 'Le paiement a échoué. Veuillez réessayer.'
          );
          setIsProcessing(false);
        }
      } catch (error) {
        console.error('Payment status check error:', error);
      }
    }, 3000); // Poll every 3 seconds

    setPollingInterval(interval);
    
    // Show instructions to user
    Alert.alert(
      'Paiement MVola initié',
      'Vous allez recevoir une demande de paiement sur votre téléphone. Veuillez confirmer le paiement pour continuer.',
      [{ text: 'OK' }]
    );
  };

  const handleStripePayment = async (response: any) => {
    // For now, we'll simulate Stripe payment
    // In a real implementation, you would integrate with Stripe SDK
    setTimeout(() => {
      dispatch(setPaymentStatus({ status: 'COMPLETED' }));
      navigation.replace('PaymentSuccess', {
        paymentId: response.payment_id,
        amount: amount,
        vehiclePlaque: vehiclePlaque,
      });
    }, 2000);
  };

  const handleCardNumberChange = (text: string) => {
    const formatted = stripePaymentService.formatCardNumber(text);
    setFormData({ ...formData, cardNumber: formatted });
  };

  const renderPaymentForm = () => {
    if (paymentMethod === 'MVOLA') {
      return (
        <View style={styles.formSection}>
          <Text style={styles.sectionTitle}>Numéro MVola</Text>
          <TextInput
            style={styles.input}
            placeholder="+261XXXXXXXXX"
            value={formData.phoneNumber}
            onChangeText={(text) => setFormData({ ...formData, phoneNumber: text })}
            keyboardType="phone-pad"
            autoCapitalize="none"
          />
          <Text style={styles.helpText}>
            Entrez votre numéro MVola au format +261XXXXXXXXX
          </Text>
        </View>
      );
    } else if (paymentMethod === 'STRIPE') {
      return (
        <View style={styles.formSection}>
          <Text style={styles.sectionTitle}>Informations de carte</Text>
          
          <TextInput
            style={[styles.input, cardErrors.cardNumber && styles.inputError]}
            placeholder="Numéro de carte"
            value={formData.cardNumber}
            onChangeText={handleCardNumberChange}
            keyboardType="numeric"
            maxLength={19} // 16 digits + 3 spaces
          />
          {cardErrors.cardNumber && (
            <Text style={styles.errorText}>{cardErrors.cardNumber}</Text>
          )}

          <View style={styles.cardRow}>
            <TextInput
              style={[styles.cardInput, styles.expiryInput, cardErrors.expiry && styles.inputError]}
              placeholder="MM"
              value={formData.expiryMonth}
              onChangeText={(text) => setFormData({ ...formData, expiryMonth: text })}
              keyboardType="numeric"
              maxLength={2}
            />
            <TextInput
              style={[styles.cardInput, styles.expiryInput, cardErrors.expiry && styles.inputError]}
              placeholder="AA"
              value={formData.expiryYear}
              onChangeText={(text) => setFormData({ ...formData, expiryYear: text })}
              keyboardType="numeric"
              maxLength={2}
            />
            <TextInput
              style={[styles.cardInput, styles.cvcInput, cardErrors.cvc && styles.inputError]}
              placeholder="CVC"
              value={formData.cvc}
              onChangeText={(text) => setFormData({ ...formData, cvc: text })}
              keyboardType="numeric"
              maxLength={4}
              secureTextEntry
            />
          </View>
          {cardErrors.expiry && (
            <Text style={styles.errorText}>{cardErrors.expiry}</Text>
          )}
          {cardErrors.cvc && (
            <Text style={styles.errorText}>{cardErrors.cvc}</Text>
          )}

          <TextInput
            style={styles.input}
            placeholder="Nom du titulaire"
            value={formData.cardholderName}
            onChangeText={(text) => setFormData({ ...formData, cardholderName: text })}
            autoCapitalize="words"
          />
        </View>
      );
    }
    return null;
  };

  const platformFee = Math.round(amount * 0.03); // 3% platform fee
  const totalAmount = amount + platformFee;

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.header}>
            <Text style={styles.title}>Paiement sécurisé</Text>
            <Text style={styles.subtitle}>
              {paymentMethod === 'MVOLA' ? 'MVola' : 'Carte bancaire'}
            </Text>
          </View>

          <View style={styles.amountSection}>
            <Text style={styles.amountLabel}>Montant à payer</Text>
            <Text style={styles.amountValue}>{formatCurrency(totalAmount)}</Text>
            <Text style={styles.amountBreakdown}>
              Taxe: {formatCurrency(amount)} + Frais (3%): {formatCurrency(platformFee)}
            </Text>
          </View>

          {renderPaymentForm()}

          <TouchableOpacity
            style={[styles.payButton, (isProcessing || isInitiating) && styles.payButtonDisabled]}
            onPress={handlePayment}
            disabled={isProcessing || isInitiating}
          >
            {isProcessing || isInitiating ? (
              <ActivityIndicator color={colors.white} />
            ) : (
              <Text style={styles.payButtonText}>
                Payer {formatCurrency(totalAmount)}
              </Text>
            )}
          </TouchableOpacity>

          <Text style={styles.securityText}>
            Vos informations de paiement sont sécurisées et encryptées
          </Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    padding: spacing.md,
  },
  header: {
    marginBottom: spacing.lg,
    alignItems: 'center',
  },
  title: {
    ...typography.h1,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    ...typography.h3,
    color: colors.primary,
  },
  amountSection: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.lg,
    alignItems: 'center',
  },
  amountLabel: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  amountValue: {
    ...typography.h1,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  amountBreakdown: {
    ...typography.small,
    color: colors.textSecondary,
  },
  formSection: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    fontSize: 16,
    backgroundColor: colors.white,
    marginBottom: spacing.sm,
  },
  inputError: {
    borderColor: colors.error,
  },
  errorText: {
    ...typography.small,
    color: colors.error,
    marginBottom: spacing.sm,
  },
  helpText: {
    ...typography.small,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  cardRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  cardInput: {
    height: 50,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    fontSize: 16,
    backgroundColor: colors.white,
  },
  expiryInput: {
    flex: 1,
    marginRight: spacing.sm,
  },
  cvcInput: {
    flex: 1,
  },
  payButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  payButtonDisabled: {
    opacity: 0.6,
  },
  payButtonText: {
    ...typography.button,
    color: colors.white,
  },
  securityText: {
    ...typography.small,
    color: colors.textSecondary,
    textAlign: 'center',
  },
});