import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Alert,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import { PaymentMethod } from '../../types/models';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';
// Simple icon components
const CreditCardIcon = () => <Text style={styles.icon}>💳</Text>;
const SmartphoneIcon = () => <Text style={styles.icon}>📱</Text>;
const DollarSignIcon = () => <Text style={styles.icon}>💵</Text>;

// Navigation types
import { PaymentStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<PaymentStackParamList, 'PaymentMethod'>;

interface PaymentMethodOption {
  id: PaymentMethod;
  title: string;
  description: string;
  icon: React.ReactNode;
  processingTime: string;
  fees: string;
  disabled?: boolean;
}

export const PaymentMethodScreen: React.FC<Props> = ({ navigation, route }) => {
  const { t } = useTranslation();
  const { amount, vehiclePlaque, fiscalYear } = route.params;

  const paymentMethods: PaymentMethodOption[] = [
    {
      id: 'MVOLA',
      title: 'MVola',
      description: 'Pay with your MVola mobile money account',
      icon: <SmartphoneIcon />,
      processingTime: 'Instant',
      fees: '3% platform fee',
    },
    {
      id: 'STRIPE',
      title: 'Credit/Debit Card',
      description: 'Pay securely with your bank card',
      icon: <CreditCardIcon />,
      processingTime: 'Instant',
      fees: '3% platform fee',
    },
    {
      id: 'CASH',
      title: 'Cash Payment',
      description: 'Pay in person at designated collection points',
      icon: <DollarSignIcon />,
      processingTime: '1-2 business days',
      fees: 'No additional fees',
      disabled: true, // Disabled for now as it requires physical collection
    },
  ];

  const handlePaymentMethodSelect = (method: PaymentMethod) => {
    if (method === 'CASH') {
      // Show coming soon message
      Alert.alert(
        'Bientôt disponible',
        'Le paiement en espèces sera bientôt disponible. Veuillez utiliser MVola ou carte bancaire pour le moment.'
      );
      return;
    }

    // Navigate to unified payment processing screen
    navigation.navigate('PaymentProcessing', {
      amount,
      vehiclePlaque,
      fiscalYear,
      paymentMethod: method,
    });
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('fr-MG', {
      style: 'currency',
      currency: 'MGA',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>Choisissez votre méthode de paiement</Text>
          <Text style={styles.subtitle}>
            Montant à payer: {formatCurrency(amount)}
          </Text>
        </View>

        <View style={styles.methodsContainer}>
          {paymentMethods.map((method) => (
            <TouchableOpacity
              key={method.id}
              style={[styles.methodCard, method.disabled && styles.methodCardDisabled]}
              onPress={() => handlePaymentMethodSelect(method.id)}
              disabled={method.disabled}
            >
              <View style={styles.methodContent}>
                <View style={styles.methodIcon}>{method.icon}</View>
                
                <View style={styles.methodInfo}>
                  <Text style={styles.methodTitle}>{method.title}</Text>
                  <Text style={styles.methodDescription}>{method.description}</Text>
                  
                  <View style={styles.methodDetails}>
                    <View style={styles.detailItem}>
                      <Text style={styles.detailLabel}>Processing:</Text>
                      <Text style={styles.detailValue}>{method.processingTime}</Text>
                    </View>
                    <View style={styles.detailItem}>
                      <Text style={styles.detailLabel}>Fees:</Text>
                      <Text style={styles.detailValue}>{method.fees}</Text>
                    </View>
                  </View>
                </View>

                {method.disabled && (
                  <View style={styles.comingSoonBadge}>
                    <Text style={styles.comingSoonText}>Coming Soon</Text>
                  </View>
                )}
              </View>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.securityInfo}>
          <Text style={styles.securityTitle}>Sécurité des paiements</Text>
          <Text style={styles.securityText}>
            Tous les paiements sont sécurisés et encryptés. Vos informations de paiement ne sont jamais stockées sur nos serveurs.
          </Text>
        </View>
      </ScrollView>
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
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.h3,
    color: colors.primary,
    textAlign: 'center',
  },
  methodsContainer: {
    marginBottom: spacing.lg,
  },
  methodCard: {
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
  methodCardDisabled: {
    opacity: 0.6,
  },
  methodContent: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  methodIcon: {
    marginRight: spacing.md,
    marginTop: spacing.xs,
  },
  methodInfo: {
    flex: 1,
  },
  methodTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  methodDescription: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  methodDetails: {
    flexDirection: 'row',
  },
  detailItem: {
    marginRight: spacing.lg,
  },
  detailLabel: {
    ...typography.small,
    color: colors.textSecondary,
  },
  detailValue: {
    ...typography.small,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  comingSoonBadge: {
    backgroundColor: colors.warning,
    borderRadius: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  comingSoonText: {
    ...typography.small,
    color: colors.white,
    fontWeight: '600',
  },
  securityInfo: {
    backgroundColor: colors.info + '10',
    borderRadius: 8,
    padding: spacing.md,
  },
  securityTitle: {
    ...typography.h4,
    color: colors.info,
    marginBottom: spacing.xs,
  },
  securityText: {
    ...typography.small,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  icon: {
    fontSize: 32,
    marginBottom: spacing.sm,
  },
});