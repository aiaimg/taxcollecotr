import apiClient from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import { PaymentInitiationRequest, PaymentInitiationResponse, PaymentStatusResponse } from '../types/tax';
import { formatAPIError } from '../api/interceptors';

/**
 * StripePaymentService - Handles Stripe payment processing
 */
class StripePaymentService {
  /**
   * Initiate Stripe payment
   * @param request - Payment initiation request
   * @returns Promise<PaymentInitiationResponse>
   */
  async initiatePayment(request: PaymentInitiationRequest): Promise<PaymentInitiationResponse> {
    try {
      const response = await apiClient.post<PaymentInitiationResponse>(
        API_ENDPOINTS.PAYMENTS.INITIATE,
        {
          ...request,
          payment_method: 'STRIPE',
        }
      );

      return response.data;
    } catch (error) {
      throw new Error(formatAPIError(error));
    }
  }

  /**
   * Confirm Stripe payment
   * @param paymentId - Payment ID
   * @param paymentMethodId - Stripe payment method ID
   * @returns Promise<PaymentStatusResponse>
   */
  async confirmPayment(paymentId: number, paymentMethodId: string): Promise<PaymentStatusResponse> {
    try {
      const response = await apiClient.post<PaymentStatusResponse>(
        `${API_ENDPOINTS.PAYMENTS.DETAIL(paymentId)}confirm/`,
        {
          payment_method_id: paymentMethodId,
        }
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
  async checkStatus(paymentId: number): Promise<PaymentStatusResponse> {
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
   * Handle 3D Secure authentication
   * @param paymentId - Payment ID
   * @param redirectUrl - Redirect URL from Stripe
   * @returns Promise<PaymentStatusResponse>
   */
  async handle3DSecure(paymentId: number, redirectUrl: string): Promise<PaymentStatusResponse> {
    try {
      const response = await apiClient.post<PaymentStatusResponse>(
        `${API_ENDPOINTS.PAYMENTS.DETAIL(paymentId)}3d-secure/`,
        {
          redirect_url: redirectUrl,
        }
      );
      return response.data;
    } catch (error) {
      throw new Error(formatAPIError(error));
    }
  }

  /**
   * Validate card details
   * @param cardNumber - Card number
   * @param expiryMonth - Expiry month (1-12)
   * @param expiryYear - Expiry year (4 digits)
   * @param cvc - CVC code
   * @returns Validation result
   */
  validateCardDetails(
    cardNumber: string,
    expiryMonth: number,
    expiryYear: number,
    cvc: string
  ): { isValid: boolean; errors: Record<string, string> } {
    const errors: Record<string, string> = {};

    // Validate card number using Luhn algorithm
    if (!this.isValidCardNumber(cardNumber.replace(/\s/g, ''))) {
      errors.cardNumber = 'Invalid card number';
    }

    // Validate expiry date
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1;

    if (expiryYear < currentYear || (expiryYear === currentYear && expiryMonth < currentMonth)) {
      errors.expiry = 'Card has expired';
    }

    if (expiryMonth < 1 || expiryMonth > 12) {
      errors.expiry = 'Invalid expiry month';
    }

    // Validate CVC
    if (!/^\d{3,4}$/.test(cvc)) {
      errors.cvc = 'Invalid CVC';
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }

  /**
   * Format card number for display
   * @param cardNumber - Raw card number
   * @returns Formatted card number
   */
  formatCardNumber(cardNumber: string): string {
    // Remove all non-digits
    const digits = cardNumber.replace(/\D/g, '');
    
    // Format in groups of 4
    return digits.match(/.{1,4}/g)?.join(' ') || digits;
  }

  /**
   * Detect card type from card number
   * @param cardNumber - Card number
   * @returns Card type
   */
  detectCardType(cardNumber: string): string {
    const patterns = {
      visa: /^4/,
      mastercard: /^5[1-5]/,
      amex: /^3[47]/,
      discover: /^6(?:011|5)/,
    };

    const digits = cardNumber.replace(/\s/g, '');

    for (const [type, pattern] of Object.entries(patterns)) {
      if (pattern.test(digits)) {
        return type;
      }
    }

    return 'unknown';
  }

  /**
   * Validate card number using Luhn algorithm
   * @param cardNumber - Card number without spaces
   * @returns true if valid
   */
  private isValidCardNumber(cardNumber: string): boolean {
    if (!/^\d+$/.test(cardNumber)) {
      return false;
    }

    let sum = 0;
    let isEven = false;

    // Process digits from right to left
    for (let i = cardNumber.length - 1; i >= 0; i--) {
      let digit = parseInt(cardNumber[i]);

      if (isEven) {
        digit *= 2;
        if (digit > 9) {
          digit -= 9;
        }
      }

      sum += digit;
      isEven = !isEven;
    }

    return sum % 10 === 0;
  }

  /**
   * Get Stripe instructions
   * @returns Instructions for Stripe payment
   */
  getInstructions(): string {
    return 'Enter your card details to complete the payment. Your payment information is processed securely by Stripe.';
  }

  /**
   * Get supported card types
   * @returns Array of supported card types
   */
  getSupportedCardTypes(): string[] {
    return ['visa', 'mastercard'];
  }
}

// Export singleton instance
export default new StripePaymentService();