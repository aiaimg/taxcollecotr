import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../store';
import { API_ENDPOINTS } from '../../api/endpoints';
import {
  TaxCalculationRequest,
  TaxCalculationResponse,
  PaymentInitiationRequest,
  PaymentInitiationResponse,
  PaymentStatusResponse,
  PaymentReceipt,
} from '../../types/tax';

export const taxApi = createApi({
  reducerPath: 'taxApi',
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.tokens?.access;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['TaxCalculation', 'Payment', 'PaymentHistory'],
  keepUnusedDataFor: 600, // 10 minutes cache for payments
  endpoints: (builder) => ({
    // Tax Calculation Endpoints
    calculateTax: builder.mutation<TaxCalculationResponse, TaxCalculationRequest>({
      query: (body) => ({
        url: API_ENDPOINTS.TAX_CALCULATIONS.CALCULATE,
        method: 'POST',
        body,
      }),
      invalidatesTags: ['TaxCalculation'],
    }),

    // Payment Initiation Endpoints
    initiatePayment: builder.mutation<PaymentInitiationResponse, PaymentInitiationRequest>({
      query: (body) => ({
        url: API_ENDPOINTS.PAYMENTS.INITIATE,
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Payment'],
    }),

    // Payment Status and History Endpoints
    getPaymentStatus: builder.query<PaymentStatusResponse, number>({
      query: (paymentId) => API_ENDPOINTS.PAYMENTS.DETAIL(paymentId),
      providesTags: (result, error, paymentId) => [{ type: 'Payment', id: paymentId }],
    }),

    getPaymentReceipt: builder.query<PaymentReceipt, number>({
      query: (paymentId) => API_ENDPOINTS.PAYMENTS.RECEIPT(paymentId),
      providesTags: (result, error, paymentId) => [{ type: 'Payment', id: paymentId }],
    }),

    getPaymentHistory: builder.query<PaymentReceipt[], { page?: number; pageSize?: number }>({
      query: ({ page = 1, pageSize = 20 }) => ({
        url: API_ENDPOINTS.PAYMENTS.LIST,
        params: { page, page_size: pageSize },
      }),
      providesTags: ['PaymentHistory'],
    }),
  }),
});

// Export hooks for usage in functional components
export const {
  useCalculateTaxMutation,
  useInitiatePaymentMutation,
  useGetPaymentStatusQuery,
  useGetPaymentReceiptQuery,
  useGetPaymentHistoryQuery,
  useLazyGetPaymentStatusQuery,
  useLazyGetPaymentReceiptQuery,
  useLazyGetPaymentHistoryQuery,
} = taxApi;