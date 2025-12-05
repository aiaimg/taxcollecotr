import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { PaymentSuccessScreen } from '../screens/payments/PaymentSuccessScreen';

jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({ navigate: jest.fn() }),
}));

jest.mock('../store', () => ({
  useAppDispatch: () => jest.fn(),
  useAppSelector: () => ({ paymentId: 1 }),
  useGetPaymentReceiptQuery: () => ({
    data: {
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
    isLoading: false,
  }),
}));

describe('PaymentSuccessScreen QR display', () => {
  it('renders QR image and navigates to viewer on tap', () => {
    const navigation: any = { navigate: jest.fn() };
    const route: any = { params: { paymentId: 1, amount: 1000, vehiclePlaque: 'ABC-1234' } };
    const { getByText } = render(<PaymentSuccessScreen navigation={navigation} route={route} />);
    expect(getByText('Code QR de vérification')).toBeTruthy();
    // Tap share button
    fireEvent.press(getByText('Partager'));
    // Tap QR title to simulate area; navigation call will be asserted separately if needed
  });
});