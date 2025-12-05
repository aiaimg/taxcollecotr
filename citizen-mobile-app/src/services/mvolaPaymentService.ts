import apiClient from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import { PaymentInitiationRequest, PaymentInitiationResponse, PaymentStatusResponse } from '../types/tax';
import { formatAPIError } from '../api/interceptors';

/**
 * MVolaPaymentService - Handles MVola payment processing
 */
class MVolaPaymentService {
  private pollingInterval: NodeJS.Timeout | null = null;
  private pollingCallbacks: Map<number, (status: PaymentStatusResponse) => void> = new Map();

  /**
   * Initiate MVola payment
   * @param request - Payment initiation request
   * @returns Promise<PaymentInitiationResponse>
   */
  async initiatePayment(request: PaymentInitiationRequest): Promise<PaymentInitiationResponse> {
    try {
      // Validate phone number format (+261XXXXXXXXX)
      if (!request.phone_number || !this.validatePhoneNumber(request.phone_number)) {
        throw new Error('Invalid phone number format. Must be +261XXXXXXXXX');
      }

      const response = await apiClient.post<PaymentInitiationResponse>(
        API_ENDPOINTS.PAYMENTS.INITIATE,
        {
          ...request,
          payment_method: 'MVOLA',
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
   * Start polling payment status
   * @param paymentId - Payment ID
   * @param interval - Polling interval in milliseconds (default: 3000ms)
   * @param callback - Callback function for status updates
   * @param maxAttempts - Maximum polling attempts (default: 60)
   */
  startPolling(
    paymentId: number,
    interval: number = 3000,
    callback: (status: PaymentStatusResponse) => void,
    maxAttempts: number = 60
  ): void {
    this.stopPolling(paymentId); // Stop any existing polling for this payment

    let attempts = 0;
    this.pollingCallbacks.set(paymentId, callback);

    this.pollingInterval = setInterval(async () => {
      attempts++;
      
      try {
        const status = await this.checkStatus(paymentId);
        callback(status);

        // Stop polling if payment is completed, failed, or cancelled
        if (status.status === 'COMPLETED' || status.status === 'FAILED' || status.status === 'CANCELLED') {
          this.stopPolling(paymentId);
          return;
        }

        // Stop polling if max attempts reached
        if (attempts >= maxAttempts) {
          this.stopPolling(paymentId);
          callback({
            ...status,
            status: 'FAILED',
            failure_reason: 'Payment timeout - maximum polling attempts reached',
          });
          return;
        }
      } catch (error) {
        console.error('MVola polling error:', error);
        
        // Stop polling on repeated errors
        if (attempts >= 3) {
          this.stopPolling(paymentId);
          callback({
            payment_id: paymentId,
            transaction_id: '',
            status: 'FAILED',
            amount_ariary: 0,
            payment_method: 'MVOLA',
            failure_reason: 'Network error during payment verification',
          });
        }
      }
    }, interval);
  }

  /**
   * Stop polling payment status
   * @param paymentId - Payment ID
   */
  stopPolling(paymentId: number): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    this.pollingCallbacks.delete(paymentId);
  }

  /**
   * Stop all polling
   */
  stopAllPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    this.pollingCallbacks.clear();
  }

  /**
   * Validate Malagasy phone number format
   * @param phoneNumber - Phone number to validate
   * @returns true if valid
   */
  validatePhoneNumber(phoneNumber: string): boolean {
    // Malagasy phone number format: +261XXXXXXXXX (10 digits after +261)
    const regex = /^\+261\d{9}$/;
    return regex.test(phoneNumber);
  }

  /**
   * Format phone number for display
   * @param phoneNumber - Phone number to format
   * @returns Formatted phone number
   */
  formatPhoneNumber(phoneNumber: string): string {
    if (!this.validatePhoneNumber(phoneNumber)) {
      return phoneNumber;
    }
    
    // Format as +261 XX XX XXX XX
    return phoneNumber.replace(/(\+261)(\d{2})(\d{2})(\d{3})(\d{2})/, '$1 $2 $3 $4 $5');
  }

  /**
   * Get MVola instructions
   * @returns Instructions for MVola payment
   */
  getInstructions(): string {
    return 'You will receive a payment request on your MVola account. Please confirm the payment to complete the transaction.';
  }
}

// Export singleton instance
export default new MVolaPaymentService();