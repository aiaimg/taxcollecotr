import apiClient from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import { 
  TaxCalculationRequest, 
  TaxCalculationResponse, 
  TaxCalculation,
  PaymentInitiationRequest,
  PaymentInitiationResponse,
  PaymentStatusResponse,
  PaymentReceipt 
} from '../types/tax';
import { formatAPIError } from '../api/interceptors';

/**
 * TaxCalculationService - Handles tax calculations and payment processing
 */
class TaxCalculationService {
  /**
   * Calculate tax for a vehicle
   * @param request - Tax calculation request
   * @returns Promise<TaxCalculationResponse>
   */
  async calculateTax(request: TaxCalculationRequest): Promise<TaxCalculationResponse> {
    try {
      const response = await apiClient.post<TaxCalculationResponse>(
        API_ENDPOINTS.TAX_CALCULATIONS.CALCULATE,
        request
      );
      return response.data;
    } catch (error) {
      throw new Error(formatAPIError(error));
    }
  }

  /**
   * Calculate tax and create a local calculation object
   * @param vehiclePlaque - Vehicle plate number
   * @param fiscalYear - Fiscal year
   * @returns Promise<TaxCalculation>
   */
  async calculate(vehiclePlaque: string, fiscalYear: number): Promise<TaxCalculation> {
    const response = await this.calculateTax({
      vehicle_plaque: vehiclePlaque,
      fiscal_year: fiscalYear,
    });

    // Create a local calculation object with expiration time
    const expiresAt = new Date();
    expiresAt.setMinutes(expiresAt.getMinutes() + 30); // Expires in 30 minutes

    return {
      id: `${vehiclePlaque}-${fiscalYear}-${Date.now()}`,
      vehicle_plaque: response.vehicle_plaque,
      fiscal_year: response.fiscal_year,
      base_amount_ariary: response.base_amount_ariary,
      platform_fee_ariary: response.platform_fee_ariary,
      total_amount_ariary: response.total_amount_ariary,
      final_amount_ariary: response.final_amount_ariary,
      due_date: response.due_date,
      is_exempt: response.is_exempt,
      exemption_reason: response.exemption_reason,
      calculated_at: new Date().toISOString(),
      expires_at: expiresAt.toISOString(),
    };
  }

  /**
   * Initiate a payment
   * @param request - Payment initiation request
   * @returns Promise<PaymentInitiationResponse>
   */
  async initiatePayment(request: PaymentInitiationRequest): Promise<PaymentInitiationResponse> {
    try {
      const response = await apiClient.post<PaymentInitiationResponse>(
        API_ENDPOINTS.PAYMENTS.INITIATE,
        request
      );
      return response.data;
    } catch (error) {
      throw new Error(formatAPIError(error));
    }
  }

  /**
   * Check payment status
   * @param paymentId - Payment ID
   * @returns Promise<PaymentStatusResponse>
   */
  async checkPaymentStatus(paymentId: number): Promise<PaymentStatusResponse> {
    try {
      const response = await apiClient.get<PaymentStatusResponse>(
        API_ENDPOINTS.PAYMENTS.DETAIL(paymentId)
      );
      return response.data;
    } catch (error) {
      throw new Error(formatAPIError(error));
    }
  }

  /**
   * Get payment receipt
   * @param paymentId - Payment ID
   * @returns Promise<PaymentReceipt>
   */
  async getPaymentReceipt(paymentId: number): Promise<PaymentReceipt> {
    try {
      const response = await apiClient.get<PaymentReceipt>(
        API_ENDPOINTS.PAYMENTS.RECEIPT(paymentId)
      );
      return response.data;
    } catch (error) {
      throw new Error(formatAPIError(error));
    }
  }

  /**
   * Get payment history
   * @param page - Page number (optional)
   * @param pageSize - Page size (optional)
   * @returns Promise<PaymentReceipt[]>
   */
  async getPaymentHistory(page?: number, pageSize?: number): Promise<PaymentReceipt[]> {
    try {
      const params = new URLSearchParams();
      if (page) params.append('page', page.toString());
      if (pageSize) params.append('page_size', pageSize.toString());

      const response = await apiClient.get<PaymentReceipt[]>(
        `${API_ENDPOINTS.PAYMENTS.LIST}?${params.toString()}`
      );
      return response.data;
    } catch (error) {
      throw new Error(formatAPIError(error));
    }
  }

  /**
   * Format currency in Ariary
   * @param amount - Amount in Ariary
   * @returns Formatted currency string
   */
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('fr-MG', {
      style: 'currency',
      currency: 'MGA',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  /**
   * Calculate platform fee
   * @param baseAmount - Base amount in Ariary
   * @param feePercentage - Fee percentage (default: 3%)
   * @returns Platform fee amount
   */
  calculatePlatformFee(baseAmount: number, feePercentage: number = 3): number {
    return Math.round(baseAmount * (feePercentage / 100));
  }

  /**
   * Check if a tax calculation is expired
   * @param calculation - Tax calculation
   * @returns true if expired
   */
  isCalculationExpired(calculation: TaxCalculation): boolean {
    return new Date() > new Date(calculation.expires_at);
  }

  /**
   * Get tax calculation expiration time remaining
   * @param calculation - Tax calculation
   * @returns Time remaining in minutes
   */
  getCalculationTimeRemaining(calculation: TaxCalculation): number {
    const now = new Date();
    const expires = new Date(calculation.expires_at);
    const diffMs = expires.getTime() - now.getTime();
    return Math.max(0, Math.ceil(diffMs / (1000 * 60)));
  }
}

// Export singleton instance
export default new TaxCalculationService();