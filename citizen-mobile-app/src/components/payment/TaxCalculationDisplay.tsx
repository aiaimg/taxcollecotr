import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { TaxCalculationResponse } from '../../types/tax';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';

interface TaxCalculationDisplayProps {
  calculation: TaxCalculationResponse;
  onProceedToPayment: (amount: number) => void;
  loading?: boolean;
}

export const TaxCalculationDisplay: React.FC<TaxCalculationDisplayProps> = ({
  calculation,
  onProceedToPayment,
  loading = false,
}) => {
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('fr-MG', {
      style: 'currency',
      currency: 'MGA',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleProceedToPayment = () => {
    onProceedToPayment(calculation.final_amount_ariary);
  };

  if (calculation.is_exempt) {
    return (
      <View style={styles.container}>
        <View style={styles.exemptionContainer}>
          <Text style={styles.exemptionTitle}>Véhicule Exonéré</Text>
          <Text style={styles.exemptionText}>
            {calculation.exemption_reason || 'Ce véhicule est exonéré de la taxe annuelle.'}
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Calcul de la Taxe</Text>
        <Text style={styles.subtitle}>
          Année fiscale {calculation.fiscal_year}
        </Text>
      </View>

      <View style={styles.calculationCard}>
        {/* Tax Breakdown */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Détail du calcul</Text>
          
          <View style={styles.breakdownRow}>
            <Text style={styles.breakdownLabel}>Type de véhicule:</Text>
            <Text style={styles.breakdownValue}>{calculation.tax_breakdown.vehicle_type}</Text>
          </View>

          <View style={styles.breakdownRow}>
            <Text style={styles.breakdownLabel}>Puissance fiscale:</Text>
            <Text style={styles.breakdownValue}>{calculation.tax_breakdown.fiscal_power_cv} CV</Text>
          </View>

          <View style={styles.breakdownRow}>
            <Text style={styles.breakdownLabel}>Taux de base:</Text>
            <Text style={styles.breakdownValue}>{formatCurrency(calculation.tax_breakdown.base_rate_ariary)}</Text>
          </View>

          {calculation.tax_breakdown.age_factor !== 1 && (
            <View style={styles.breakdownRow}>
              <Text style={styles.breakdownLabel}>Facteur âge:</Text>
              <Text style={styles.breakdownValue}>{calculation.tax_breakdown.age_factor}x</Text>
            </View>
          )}

          {calculation.tax_breakdown.energy_factor !== 1 && (
            <View style={styles.breakdownRow}>
              <Text style={styles.breakdownLabel}>Facteur énergie:</Text>
              <Text style={styles.breakdownValue}>{calculation.tax_breakdown.energy_factor}x</Text>
            </View>
          )}

          {calculation.tax_breakdown.category_factor !== 1 && (
            <View style={styles.breakdownRow}>
              <Text style={styles.breakdownLabel}>Facteur catégorie:</Text>
              <Text style={styles.breakdownValue}>{calculation.tax_breakdown.category_factor}x</Text>
            </View>
          )}
        </View>

        {/* Discounts */}
        {calculation.applicable_discounts.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Réductions appliquées</Text>
            {calculation.applicable_discounts.map((discount, index) => (
              <View key={index} style={styles.discountRow}>
                <Text style={styles.discountName}>{discount.name}</Text>
                <Text style={styles.discountAmount}>-{formatCurrency(discount.amount_ariary)}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Amount Summary */}
        <View style={styles.summarySection}>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Montant de base:</Text>
            <Text style={styles.summaryValue}>{formatCurrency(calculation.base_amount_ariary)}</Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Frais de plateforme ({calculation.platform_fee_percentage}%):</Text>
            <Text style={styles.summaryValue}>{formatCurrency(calculation.platform_fee_ariary)}</Text>
          </View>

          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Montant total:</Text>
            <Text style={styles.totalValue}>{formatCurrency(calculation.final_amount_ariary)}</Text>
          </View>

          <Text style={styles.dueDateText}>
            Date limite: {new Date(calculation.due_date).toLocaleDateString('fr-FR')}
          </Text>
        </View>
      </View>

      <TouchableOpacity
        style={[styles.proceedButton, loading && styles.proceedButtonDisabled]}
        onPress={handleProceedToPayment}
        disabled={loading}
      >
        <Text style={styles.proceedButtonText}>
          {loading ? 'Chargement...' : `Payer ${formatCurrency(calculation.final_amount_ariary)}`}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
  },
  header: {
    marginBottom: spacing.lg,
    alignItems: 'center',
  },
  title: {
    ...typography.h2,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
  },
  calculationCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.md,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: spacing.lg,
  },
  section: {
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  breakdownRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  breakdownLabel: {
    ...typography.body,
    color: colors.textSecondary,
  },
  breakdownValue: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  discountRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  discountName: {
    ...typography.body,
    color: colors.success,
  },
  discountAmount: {
    ...typography.body,
    color: colors.success,
    fontWeight: '600',
  },
  summarySection: {
    marginTop: spacing.md,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  summaryLabel: {
    ...typography.body,
    color: colors.textSecondary,
  },
  summaryValue: {
    ...typography.body,
    color: colors.textPrimary,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 2,
    borderTopColor: colors.primary,
  },
  totalLabel: {
    ...typography.h3,
    color: colors.primary,
  },
  totalValue: {
    ...typography.h3,
    color: colors.primary,
    fontWeight: 'bold',
  },
  dueDateText: {
    ...typography.small,
    color: colors.warning,
    textAlign: 'center',
    marginTop: spacing.sm,
  },
  proceedButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    alignItems: 'center',
  },
  proceedButtonDisabled: {
    opacity: 0.6,
  },
  proceedButtonText: {
    ...typography.button,
    color: colors.white,
  },
  exemptionContainer: {
    backgroundColor: colors.success + '10',
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
  },
  exemptionTitle: {
    ...typography.h2,
    color: colors.success,
    marginBottom: spacing.sm,
  },
  exemptionText: {
    ...typography.body,
    color: colors.textPrimary,
    textAlign: 'center',
  },
});