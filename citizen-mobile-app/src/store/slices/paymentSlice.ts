import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { PaymentReceipt, TaxCalculation } from '../../types/tax';
import { PaymentMethod } from '../../types/models';

interface PaymentState {
  currentCalculation: TaxCalculation | null;
  currentPayment: {
    paymentId: number | null;
    transactionId: string | null;
    amount: number;
    paymentMethod: PaymentMethod | null;
    status: 'IDLE' | 'INITIATING' | 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
    failureReason?: string;
  };
  payments: PaymentReceipt[];
  isLoading: boolean;
  error: string | null;
  filters: {
    year?: number;
    vehicle?: string;
    status?: string;
  };
}

const initialState: PaymentState = {
  currentCalculation: null,
  currentPayment: {
    paymentId: null,
    transactionId: null,
    amount: 0,
    paymentMethod: null,
    status: 'IDLE',
  },
  payments: [],
  isLoading: false,
  error: null,
  filters: {},
};

const paymentSlice = createSlice({
  name: 'payment',
  initialState,
  reducers: {
    // Tax Calculation Actions
    setCurrentCalculation: (state, action: PayloadAction<TaxCalculation | null>) => {
      state.currentCalculation = action.payload;
    },

    // Payment Actions
    initiatePayment: (state, action: PayloadAction<{ paymentMethod: PaymentMethod; amount: number }>) => {
      state.currentPayment.paymentMethod = action.payload.paymentMethod;
      state.currentPayment.amount = action.payload.amount;
      state.currentPayment.status = 'INITIATING';
      state.currentPayment.failureReason = undefined;
    },

    setPaymentId: (state, action: PayloadAction<{ paymentId: number; transactionId: string }>) => {
      state.currentPayment.paymentId = action.payload.paymentId;
      state.currentPayment.transactionId = action.payload.transactionId;
      state.currentPayment.status = 'PENDING';
    },

    setPaymentStatus: (state, action: PayloadAction<{
      status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
      failureReason?: string;
    }>) => {
      state.currentPayment.status = action.payload.status;
      state.currentPayment.failureReason = action.payload.failureReason;
    },

    resetCurrentPayment: (state) => {
      state.currentPayment = {
        paymentId: null,
        transactionId: null,
        amount: 0,
        paymentMethod: null,
        status: 'IDLE',
      };
    },

    // Payment History Actions
    setPayments: (state, action: PayloadAction<PaymentReceipt[]>) => {
      state.payments = action.payload;
    },

    addPayment: (state, action: PayloadAction<PaymentReceipt>) => {
      state.payments.unshift(action.payload);
    },

    updatePayment: (state, action: PayloadAction<PaymentReceipt>) => {
      const index = state.payments.findIndex(p => p.payment_id === action.payload.payment_id);
      if (index !== -1) {
        state.payments[index] = action.payload;
      }
    },

    // Filter Actions
    setFilters: (state, action: PayloadAction<typeof state.filters>) => {
      state.filters = action.payload;
    },

    clearFilters: (state) => {
      state.filters = {};
    },

    // Loading and Error Actions
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

// Actions
export const {
  setCurrentCalculation,
  initiatePayment,
  setPaymentId,
  setPaymentStatus,
  resetCurrentPayment,
  setPayments,
  addPayment,
  updatePayment,
  setFilters,
  clearFilters,
  setLoading,
  setError,
} = paymentSlice.actions;

// Selectors
export const selectCurrentCalculation = (state: { payment: PaymentState }) => state.payment.currentCalculation;
export const selectCurrentPayment = (state: { payment: PaymentState }) => state.payment.currentPayment;
export const selectPayments = (state: { payment: PaymentState }) => state.payment.payments;
export const selectFilteredPayments = (state: { payment: PaymentState }) => {
  const { payments, filters } = state.payment;
  
  return payments.filter(payment => {
    if (filters.year && payment.fiscal_year !== filters.year) return false;
    if (filters.vehicle && payment.vehicle_plaque !== filters.vehicle) return false;
    if (filters.status && payment.payment_method !== filters.status) return false;
    return true;
  });
};
export const selectPaymentLoading = (state: { payment: PaymentState }) => state.payment.isLoading;
export const selectPaymentError = (state: { payment: PaymentState }) => state.payment.error;
export const selectPaymentFilters = (state: { payment: PaymentState }) => state.payment.filters;

export default paymentSlice.reducer;