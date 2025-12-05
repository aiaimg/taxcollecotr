import paymentService from '../paymentService';
import mvolaPaymentService from '../mvolaPaymentService';
import stripePaymentService from '../stripePaymentService';
import taxCalculationService from '../taxCalculationService';

// Mock the services
jest.mock('../mvolaPaymentService');
jest.mock('../stripePaymentService');
jest.mock('../taxCalculationService');

describe('PaymentService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('processPayment', () => {
    it('should process MVola payment successfully', async () => {
      const mockResponse = {
        payment_id: 123,
        transaction_id: 'TRANS123',
        amount_ariary: 10000,
        payment_method: 'MVOLA',
        status: 'PENDING',
      };

      (mvolaPaymentService.initiatePayment as jest.Mock).mockResolvedValue(mockResponse);

      const request = {
        vehicle_plaque: 'ABC123',
        fiscal_year: 2024,
        amount_ariary: 10000,
        payment_method: 'MVOLA' as const,
        phone_number: '+261340000000',
      };

      const result = await paymentService.processPayment(request);

      expect(mvolaPaymentService.initiatePayment).toHaveBeenCalledWith(request);
      expect(result).toEqual(mockResponse);
    });

    it('should process Stripe payment successfully', async () => {
      const mockResponse = {
        payment_id: 124,
        transaction_id: 'TRANS124',
        amount_ariary: 15000,
        payment_method: 'STRIPE',
        status: 'PENDING',
      };

      (stripePaymentService.initiatePayment as jest.Mock).mockResolvedValue(mockResponse);

      const request = {
        vehicle_plaque: 'ABC123',
        fiscal_year: 2024,
        amount_ariary: 15000,
        payment_method: 'STRIPE' as const,
      };

      const result = await paymentService.processPayment(request);

      expect(stripePaymentService.initiatePayment).toHaveBeenCalledWith(request);
      expect(result).toEqual(mockResponse);
    });

    it('should throw error for unsupported payment method', async () => {
      const request = {
        vehicle_plaque: 'ABC123',
        fiscal_year: 2024,
        amount_ariary: 10000,
        payment_method: 'UNKNOWN' as any,
      };

      await expect(paymentService.processPayment(request)).rejects.toThrow(
        'Unsupported payment method: UNKNOWN'
      );
    });

    it('should throw error for cash payment (not implemented)', async () => {
      const request = {
        vehicle_plaque: 'ABC123',
        fiscal_year: 2024,
        amount_ariary: 10000,
        payment_method: 'CASH' as const,
      };

      await expect(paymentService.processPayment(request)).rejects.toThrow(
        'Cash payment is not yet supported'
      );
    });
  });

  describe('validatePaymentForm', () => {
    it('should validate MVola form correctly', () => {
      const validForm = { phoneNumber: '+261340000000' };
      const result = paymentService.validatePaymentForm('MVOLA', validForm);

      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual({});
    });

    it('should validate MVola form with invalid phone number', () => {
      const invalidForm = { phoneNumber: 'invalid' };
      const result = paymentService.validatePaymentForm('MVOLA', invalidForm);

      expect(result.isValid).toBe(false);
      expect(result.errors.phoneNumber).toContain('Invalid phone number format');
    });

    it('should validate Stripe form correctly', () => {
      const validForm = {
        cardNumber: '4111111111111111',
        expiryMonth: '12',
        expiryYear: '2025',
        cvc: '123',
      };

      (stripePaymentService.validateCardDetails as jest.Mock).mockReturnValue({
        isValid: true,
        errors: {},
      });

      const result = paymentService.validatePaymentForm('STRIPE', validForm);

      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual({});
    });

    it('should validate Stripe form with invalid card', () => {
      const invalidForm = {
        cardNumber: 'invalid',
        expiryMonth: '13',
        expiryYear: '2020',
        cvc: '12',
      };

      (stripePaymentService.validateCardDetails as jest.Mock).mockReturnValue({
        isValid: false,
        errors: {
          cardNumber: 'Invalid card number',
          expiry: 'Card has expired',
          cvc: 'Invalid CVC',
        },
      });

      const result = paymentService.validatePaymentForm('STRIPE', invalidForm);

      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveProperty('cardNumber');
      expect(result.errors).toHaveProperty('expiry');
      expect(result.errors).toHaveProperty('cvc');
    });
  });

  describe('getPaymentInstructions', () => {
    it('should return MVola instructions', () => {
      const instructions = paymentService.getPaymentInstructions('MVOLA');
      expect(instructions).toContain('MVola');
    });

    it('should return Stripe instructions', () => {
      const instructions = paymentService.getPaymentInstructions('STRIPE');
      expect(instructions).toContain('Stripe');
    });

    it('should return cash instructions', () => {
      const instructions = paymentService.getPaymentInstructions('CASH');
      expect(instructions).toContain('collection point');
    });
  });

  describe('calculatePlatformFee', () => {
    it('should calculate 3% platform fee correctly', () => {
      const fee = paymentService.calculatePlatformFee(10000);
      expect(fee).toBe(300);
    });

    it('should calculate custom platform fee correctly', () => {
      const fee = paymentService.calculatePlatformFee(10000, 5);
      expect(fee).toBe(500);
    });
  });

  describe('formatCurrency', () => {
    it('should format currency correctly', () => {
      const formatted = paymentService.formatCurrency(10000);
      expect(formatted).toContain('10,000');
      expect(formatted).toContain('MGA');
    });
  });

  describe('getSupportedPaymentMethods', () => {
    it('should return supported payment methods', () => {
      const methods = paymentService.getSupportedPaymentMethods();
      expect(methods).toContain('MVOLA');
      expect(methods).toContain('STRIPE');
      expect(methods).not.toContain('CASH');
    });
  });

  describe('isPaymentMethodSupported', () => {
    it('should return true for supported methods', () => {
      expect(paymentService.isPaymentMethodSupported('MVOLA')).toBe(true);
      expect(paymentService.isPaymentMethodSupported('STRIPE')).toBe(true);
    });

    it('should return false for unsupported methods', () => {
      expect(paymentService.isPaymentMethodSupported('CASH')).toBe(false);
      expect(paymentService.isPaymentMethodSupported('UNKNOWN' as any)).toBe(false);
    });
  });
});