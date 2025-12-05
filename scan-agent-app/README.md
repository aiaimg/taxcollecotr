# Scan Agent App

A mobile scanning application for government agents and partner agents to scan and validate QR codes, barcodes, and license plates for tax collection purposes.

## Features

- **Role-based Access Control**: Separate interfaces for Government Agents and Partner Agents
- **Multi-format Scanning**: QR codes, barcodes, and license plates
- **Offline Capabilities**: Works without internet connection with sync functionality
- **Real-time Validation**: Online validation with offline fallback
- **Location Services**: GPS-based location tracking for scans
- **Payment Integration**: Secure payment processing
- **Scan History**: Complete scan history with filtering and details
- **Agent Profiles**: Agent information and settings management

## Agent Types

### Government Agents
- Full scanning capabilities (QR codes, barcodes, license plates)
- Payment processing
- Commission tracking
- Cash session management
- Complete scan history access

### Partner Agents
- Limited scanning (QR codes and barcodes only)
- Payment processing
- Commission tracking
- Restricted scan history

## Technology Stack

- **Frontend**: React Native with TypeScript
- **Navigation**: React Navigation
- **State Management**: React Context API
- **Storage**: Secure storage for sensitive data, async storage for general data
- **Camera**: Expo Camera for scanning
- **Location**: Expo Location services
- **Network**: React Native NetInfo for connectivity

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Start the development server:
   ```bash
   npm start
   # or
   yarn start
   ```

4. Run on your preferred platform:
   ```bash
   npm run android  # Android
   npm run ios      # iOS
   npm run web      # Web
   ```

## Project Structure

```
src/
├── components/          # Reusable UI components
├── screens/            # Screen components
├── services/           # API and business logic services
├── context/            # React Context providers
├── hooks/              # Custom React hooks
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
├── constants/          # App constants and configuration
└── assets/             # Images, icons, and other assets
```

## Key Services

- **AuthService**: Authentication and authorization
- **ScannerService**: Scanning operations and validation
- **APIService**: HTTP client with interceptors
- **StorageService**: Secure and general storage management

## Security Features

- Secure token storage
- Role-based access control
- Input validation and sanitization
- Offline data encryption
- Secure API communication

## Development

The app follows React Native best practices with:
- TypeScript for type safety
- Component-based architecture
- Custom hooks for reusable logic
- Context API for state management
- Comprehensive error handling

## License

This project is proprietary software for government tax collection purposes.