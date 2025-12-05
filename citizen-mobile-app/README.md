# Tax Collector Citizen Mobile App

A React Native mobile application for citizens and businesses in Madagascar to manage their vehicles, calculate and pay annual taxes, and access payment history.

## Tech Stack

- **Framework**: React Native with Expo (SDK 54)
- **Language**: TypeScript (strict mode)
- **Navigation**: React Navigation 7
- **State Management**: Redux Toolkit + RTK Query
- **API Client**: Axios
- **Internationalization**: i18next
- **Storage**: Expo SecureStore + AsyncStorage
- **Code Quality**: ESLint + Prettier

## Project Structure

```
src/
├── api/              # API client and endpoints
├── components/       # Reusable components
│   ├── common/      # Common UI components
│   ├── vehicle/     # Vehicle-related components
│   ├── payment/     # Payment components
│   └── navigation/  # Navigation components
├── screens/         # Application screens
│   ├── auth/       # Authentication screens
│   ├── dashboard/  # Dashboard screen
│   ├── vehicles/   # Vehicle management screens
│   ├── payments/   # Payment screens
│   ├── scanner/    # QR scanner screen
│   ├── profile/    # Profile screen
│   └── settings/   # Settings screen
├── navigation/      # Navigation configuration
├── store/          # Redux store
│   ├── slices/    # Redux slices
│   └── api/       # RTK Query APIs
├── services/       # Business logic services
├── utils/          # Utility functions
├── i18n/           # Internationalization
├── types/          # TypeScript types
└── theme/          # Theme configuration
```

## Getting Started

### Prerequisites

- Node.js 20.17.0 or higher
- npm or yarn
- Expo CLI
- iOS Simulator (for iOS development) or Android Studio (for Android development)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API configuration
```

### Development

Start the development server:
```bash
npm start
```

Run on iOS:
```bash
npm run ios
```

Run on Android:
```bash
npm run android
```

Run on Web:
```bash
npm run web
```

### Code Quality

Run linter:
```bash
npm run lint
```

Fix linting issues:
```bash
npm run lint:fix
```

Format code:
```bash
npm run format
```

Check formatting:
```bash
npm run format:check
```

Type check:
```bash
npm run type-check
```

## Environment Variables

- `API_BASE_URL`: Backend API base URL (default: http://localhost:8000)
- `API_TIMEOUT`: API request timeout in milliseconds (default: 30000)
- `NODE_ENV`: Environment (development/production)
- `ENABLE_BIOMETRIC`: Enable biometric authentication (default: true)
- `ENABLE_OFFLINE_MODE`: Enable offline mode (default: true)

## Features (To Be Implemented)

- ✅ Project structure and core configuration
- ⏳ User authentication (login, register, biometric)
- ⏳ Vehicle management (add, view, edit, delete)
- ⏳ Tax calculation and display
- ⏳ Payment processing (MVola, Stripe, Cash)
- ⏳ QR code scanner and verification
- ⏳ Push notifications
- ⏳ Offline mode with data synchronization
- ⏳ Multi-language support (French/Malagasy)
- ⏳ User profile management

## API Integration

The app connects to the existing Django backend at the configured `API_BASE_URL`. All API endpoints are defined in `src/api/endpoints.ts`.

## Contributing

1. Follow the TypeScript strict mode guidelines
2. Use ESLint and Prettier for code formatting
3. Write meaningful commit messages
4. Test on both iOS and Android before submitting

## License

Proprietary - Tax Collector Platform
