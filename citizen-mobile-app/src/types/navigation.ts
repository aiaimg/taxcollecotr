import { NavigatorScreenParams } from '@react-navigation/native';

// Auth Stack
export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

// Main Tab Navigator
export type MainTabParamList = {
  Dashboard: undefined;
  Vehicles: undefined;
  Scanner: undefined;
  Notifications: undefined;
  Profile: undefined;
};

// Profile Stack
export type ProfileStackParamList = {
  Profile: undefined;
  ProfileEdit: undefined;
  Settings: undefined;
};

// Vehicle Stack
export type VehicleStackParamList = {
  VehicleList: undefined;
  VehicleDetail: { plaque: string };
  AddVehicle: undefined;
};

// Payment Stack
export type PaymentStackParamList = {
  PaymentMethod: { vehiclePlaque: string; amount: number; fiscalYear: number };
  PaymentProcessing: { vehiclePlaque: string; amount: number; fiscalYear: number; paymentMethod: 'MVOLA' | 'STRIPE' | 'CASH' };
  PaymentSuccess: { paymentId: number; amount: number; vehiclePlaque: string };
  PaymentHistory: undefined;
  QRCodeViewer: { imageUrl: string; vehiclePlaque?: string; paidAt?: string; expiresAt?: string; amount?: string };
};

// Root Navigator
export type RootStackParamList = {
  Auth: NavigatorScreenParams<AuthStackParamList>;
  Main: NavigatorScreenParams<MainTabParamList>;
  VehicleStack: NavigatorScreenParams<VehicleStackParamList>;
  PaymentStack: NavigatorScreenParams<PaymentStackParamList>;
  ProfileStack: NavigatorScreenParams<ProfileStackParamList>;
};

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
