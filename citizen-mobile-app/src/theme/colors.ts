export const colors = {
  // Primary colors
  primary: '#405189',
  primaryDark: '#2f3d6b',
  primaryLight: '#5a6ba3',

  // Secondary colors
  secondary: '#3577f1',
  secondaryDark: '#2563d4',
  secondaryLight: '#5a91f5',

  // Status colors
  success: '#0ab39c',
  warning: '#f7b84b',
  error: '#f06548',
  info: '#299cdb',

  // Tax status colors
  taxPaid: '#0ab39c',
  taxUnpaid: '#f7b84b',
  taxExpired: '#f06548',
  taxExempt: '#299cdb',

  // Neutral colors
  white: '#ffffff',
  black: '#000000',
  gray100: '#f3f6f9',
  gray200: '#eff2f7',
  gray300: '#e9ecef',
  gray400: '#ced4da',
  gray500: '#adb5bd',
  gray600: '#878a99',
  gray700: '#495057',
  gray800: '#343a40',
  gray900: '#212529',

  // Background colors
  background: '#ffffff',
  backgroundSecondary: '#f3f6f9',
  surface: '#ffffff',

  // Text colors
  text: {
    primary: '#212529',
    secondary: '#878a99',
    tertiary: '#adb5bd',
    light: '#adb5bd',
  },
  textPrimary: '#212529',
  textSecondary: '#878a99',
  textLight: '#adb5bd',

  // Border colors
  border: '#e9ecef',
  borderLight: '#f3f6f9',

  // Overlay
  overlay: 'rgba(0, 0, 0, 0.5)',

  // Skeleton loading
  skeleton: '#e9ecef',
  skeletonHighlight: '#f3f6f9',

  // Status backgrounds
  infoBackground: '#e3f2fd',
  warningBackground: '#fff3cd',
  successBackground: '#d4edda',
  errorBackground: '#f8d7da',
};

export type Colors = typeof colors;
