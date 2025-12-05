import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { PaymentHistoryScreen } from '../screens/payments/PaymentHistoryScreen';

jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({ navigate: jest.fn() }),
}));

jest.mock('expo-media-library', () => ({
  requestPermissionsAsync: jest.fn(async () => ({ status: 'granted' })),
  saveAsync: jest.fn(async () => ({})),
}));

jest.mock('expo-file-system', () => ({
  cacheDirectory: '/tmp/',
  downloadAsync: jest.fn(async () => ({ uri: '/tmp/qr.png' })),
}));

jest.mock('../store', () => ({
  useGetPaymentHistoryQuery: () => ({
    data: [
      {
        payment_id: 1,
        transaction_id: 'txn',
        vehicle_plaque: 'ABC-1234',
        fiscal_year: 2025,
        amount_paid_ariary: 1000,
        payment_method: 'CASH',
        paid_at: new Date().toISOString(),
        qr_code_url: 'https://example.com/qr.png',
        receipt_url: 'https://example.com/receipt.pdf',
        vehicle_details: { marque: 'X', modele: 'Y', puissance_fiscale_cv: 5 },
        tax_breakdown: { vehicle_type: '', fiscal_power_cv: 5, base_rate_ariary: 100, age_factor: 1, energy_factor: 1, category_factor: 1, calculated_base_ariary: 100 },
      },
    ],
    isLoading: false,
    error: null,
  }),
}));

describe('PaymentHistory QR actions', () => {
  it('opens modal and shows QR actions', () => {
    const navigation: any = { navigate: jest.fn(), goBack: jest.fn() };
    const route: any = { params: {} };
    const { getByText } = render(<PaymentHistoryScreen navigation={navigation} route={route} />);
    fireEvent.press(getByText('MVola'));
  });
});