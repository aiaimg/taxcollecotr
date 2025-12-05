import { PaymentMethod } from '../types/models';
import { PaymentInitiationRequest, PaymentInitiationResponse, PaymentStatusResponse } from '../types/tax';
import mvolaPaymentService from './mvolaPaymentService';
import stripePaymentService from './stripePaymentService';
import taxCalculationService from './taxCalculationService';

/**
 * Unified payment service that handles all payment methods
 */
class PaymentService {
  /**
   * Process payment based on payment method
   * @param request - Payment initiation request
   * @param onStatusUpdate - Callback for status updates
   * @returns Promise<PaymentInitiationResponse>
   */
  async processPayment(
    request: PaymentInitiationRequest,
    onStatusUpdate?: (status: PaymentStatusResponse) => void
  ): Promise<PaymentInitiationResponse> {
    switch (request.payment_method) {
      case 'MVOLA':
        return this.processMVolaPayment(request, onStatusUpdate);
      case 'STRIPE':
        return this.processStripePayment(request, onStatusUpdate);
      case 'CASH':
        return this.processCashPayment(request);
      default:
        throw new Error(`Unsupported payment method: ${request.payment_method}`);
    }
  }

  /**
   * Process MVola payment
   * @param request - Payment initiation request
   * @param onStatusUpdate - Callback for status updates
   * @returns Promise<PaymentInitiationResponse>
   */
  private async processMVolaPayment(
    request: PaymentInitiationRequest,
    onStatusUpdate?: (status: PaymentStatusResponse) => void
  ): Promise<PaymentInitiationResponse> {
    // Validate phone number
    if (!request.phone_number) {
      throw new Error('Phone number is required for MVola payment');
    }

    // Initiate MVola payment
    const response = await mvolaPaymentService.initiatePayment(request);

    // Start polling if callback is provided
    if (onStatusUpdate && response.payment_id) {
      mvolaPaymentService.startPolling(
        response.payment_id,
        3000, // 3 seconds
        onStatusUpdate,
        60 // Max 60 attempts (3 minutes)
      );
    }

    return response;
  }

  /**
   * Process Stripe payment
   * @param request - Payment initiation request
   * @param onStatusUpdate - Callback for status updates
   * @returns Promise<PaymentInitiationResponse>
   */
  private async processStripePayment(
    request: PaymentInitiationRequest,
    onStatusUpdate?: (status: PaymentStatusResponse) => void
  ): Promise<PaymentInitiationResponse> {
    // Initiate Stripe payment
    const response = await stripePaymentService.initiatePayment(request);

    // Handle 3D Secure or other authentication flows
    if (response.next_action?.type === 'REDIRECT' && response.next_action.url) {
      // In a real implementation, you would handle the redirect here
      // For now, we'll just return the response
      console.log('Stripe requires redirect to:', response.next_action.url);
    }

    return response;
  }

  /**
   * Process cash payment (placeholder for future implementation)
   * @param request - Payment initiation request
   * @returns Promise<PaymentInitiationResponse>
   */
  private async processCashPayment(request: PaymentInitiationRequest): Promise<PaymentInitiationResponse> {
    // For now, cash payments are not supported
    throw new Error('Cash payment is not yet supported. Please use MVola or Stripe.');
  }

  /**
   * Get payment status
   * @param paymentId - Payment ID
   * @returns Promise<PaymentStatusResponse>
   */
  async getPaymentStatus(paymentId: number): Promise<PaymentStatusResponse> {
    // Try MVola first, then Stripe
    try {
      return await mvolaPaymentService.checkStatus(paymentId);
    } catch (error) {
      try {
        return await stripePaymentService.checkStatus(paymentId);
      } catch (stripeError) {
        throw new Error('Unable to retrieve payment status');
      }
    }
  }

  /**
   * Cancel payment
   * @param paymentId - Payment ID
   * @param paymentMethod - Payment method
   * @returns Promise<void>
   */
  async cancelPayment(paymentId: number, paymentMethod: PaymentMethod): Promise<void> {
    switch (paymentMethod) {
      case 'MVOLA':
        mvolaPaymentService.stopPolling(paymentId);
        break;
      case 'STRIPE':
        // Stripe payments can't be cancelled once initiated
        break;
      default:
        throw new Error(`Cancellation not supported for ${paymentMethod}`);
    }
  }

  /**
   * Get payment instructions for a specific method
   * @param paymentMethod - Payment method
   * @returns Instructions string
   */
  getPaymentInstructions(paymentMethod: PaymentMethod): string {
    switch (paymentMethod) {
      case 'MVOLA':
        return mvolaPaymentService.getInstructions();
      case 'STRIPE':
        return stripePaymentService.getInstructions();
      case 'CASH':
        return 'Please visit a designated collection point to make your cash payment.';
      default:
        return 'Please follow the on-screen instructions to complete your payment.';
    }
  }

  /**
   * Validate payment form data
   * @param paymentMethod - Payment method
   * @param formData - Form data to validate
   * @returns Validation result
   */
  validatePaymentForm(paymentMethod: PaymentMethod, formData: any): { isValid: boolean; errors: Record<string, string> } {
    const errors: Record<string, string> = {};

    switch (paymentMethod) {
      case 'MVOLA':
        if (!formData.phoneNumber) {
          errors.phoneNumber = 'Phone number is required';
        } else if (!mvolaPaymentService.validatePhoneNumber(formData.phoneNumber)) {
          errors.phoneNumber = 'Invalid phone number format. Use +261XXXXXXXXX';
        }
        break;

      case 'STRIPE':
        return stripePaymentService.validateCardDetails(
          formData.cardNumber || '',
          parseInt(formData.expiryMonth || '0'),
          parseInt(formData.expiryYear || '0'),
          formData.cvc || ''
        );

      case 'CASH':
        // No validation needed for cash payments
        break;

      default:
        errors.paymentMethod = 'Unsupported payment method';
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }

  /**
   * Format currency for display
   * @param amount - Amount in Ariary
   * @returns Formatted currency string
   */
  formatCurrency(amount: number): string {
    return taxCalculationService.formatCurrency(amount);
  }

  /**
   * Calculate platform fee
   * @param baseAmount - Base amount
   * @param feePercentage - Fee percentage (default: 3%)
   * @returns Platform fee amount
   */
  calculatePlatformFee(baseAmount: number, feePercentage: number = 3): number {
    return taxCalculationService.calculatePlatformFee(baseAmount, feePercentage);
  }

  /**
   * Get supported payment methods
   * @returns Array of supported payment methods
   */
  getSupportedPaymentMethods(): PaymentMethod[] {
    return ['MVOLA', 'STRIPE']; // 'CASH' will be added when implemented
  }

  /**
   * Check if payment method is supported
   * @param paymentMethod - Payment method to check
   * @returns true if supported
   */
  isPaymentMethodSupported(paymentMethod: PaymentMethod): boolean {
    return this.getSupportedPaymentMethods().includes(paymentMethod);
  }
}

// Export singleton instance
export default new PaymentService();