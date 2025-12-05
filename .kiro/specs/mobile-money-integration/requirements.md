# Requirements Document: MVola Mobile Money Integration

## Introduction

This specification defines the requirements for integrating MVola mobile payment method into the existing payments application. MVola is Telma's mobile money service in Madagascar. The integration will implement MVola's Merchant Pay API v1.0 to enable users to pay vehicle taxes using their MVola mobile wallets. This integration will serve as the foundation for future mobile money provider integrations (Airtel Money, Orange Money).

## Glossary

- **Payment System**: The existing Django application that handles vehicle tax payments (payments app)
- **MVola**: Telma's mobile money service in Madagascar
- **Merchant Pay API**: MVola's API for merchant payment collection
- **Transaction**: A single payment operation initiated by a user
- **MSISDN**: Mobile Station International Subscriber Directory Number (phone number in international format, e.g., 0340000000)
- **Correlation ID**: A unique identifier for tracking requests (X-CorrelationID)
- **Server Correlation ID**: MVola's unique identifier for a transaction (serverCorrelationId)
- **Callback URL**: An HTTP endpoint that MVola uses to notify the system of payment status changes (X-Callback-URL)
- **OAuth2**: An authorization framework used by MVola for API authentication
- **Consumer Key**: MVola API credential for authentication
- **Consumer Secret**: MVola API credential for authentication
- **Partner MSISDN**: The merchant's registered phone number with MVola
- **Access Token**: A temporary authentication token obtained via OAuth2 (valid for 3600 seconds)
- **Ariary (Ar)**: The currency of Madagascar (currency code: Ar)

## Requirements

### Requirement 1: MVola Service Architecture

**User Story:** As a system architect, I want a dedicated MVola service module, so that MVola API interactions are encapsulated and maintainable.

#### Acceptance Criteria

1. THE Payment System SHALL implement a MvolaAPIClient service class that handles all MVola API communications
2. THE MvolaAPIClient SHALL manage OAuth2 authentication with automatic token refresh
3. THE MvolaAPIClient SHALL cache access tokens for 55 minutes to minimize token generation requests
4. THE MvolaAPIClient SHALL provide methods for initiating payments, checking status, and retrieving transaction details
5. THE MvolaAPIClient SHALL generate unique X-CorrelationID values for each API request using UUID4 format

### Requirement 2: MVola Payment Initiation

**User Story:** As a Madagascar user, I want to pay vehicle taxes using MVola, so that I can use Telma's mobile money service.

#### Acceptance Criteria

1. THE Payment System SHALL integrate with MVola Merchant Pay API version 1.0 for payment processing
2. WHEN a user initiates a MVola payment, THE Payment System SHALL validate the MSISDN format for Madagascar (0340000000 format)
3. THE Payment System SHALL support payment amounts between 100 Ar and 5,000,000 Ar for MVola
4. WHEN a MVola payment is initiated, THE Payment System SHALL send a push notification to the customer's MVola mobile wallet for confirmation
5. THE Payment System SHALL include required headers (Authorization, Version, X-CorrelationID, UserLanguage, UserAccountIdentifier, partnerName, X-Callback-URL) in payment requests
6. THE Payment System SHALL construct payment payload with amount, currency, descriptionText, requestDate, debitParty, creditParty, metadata, and requestingOrganisationTransactionReference
7. THE Payment System SHALL store MVola-specific transaction references (x_correlation_id, server_correlation_id, transaction_reference) in the PaiementTaxe model

### Requirement 3: MVola OAuth2 Authentication

**User Story:** As a system, I want to authenticate with MVola API using OAuth2, so that I can securely access MVola services.

#### Acceptance Criteria

1. THE Payment System SHALL implement OAuth2 client credentials flow for MVola authentication
2. THE Payment System SHALL generate Basic Authentication header using Base64 encoding of consumer_key:consumer_secret
3. THE Payment System SHALL request access tokens from MVola token endpoint with grant_type=client_credentials and scope=EXT_INT_MVOLA_SCOPE
4. THE Payment System SHALL cache access tokens for 55 minutes (token expires in 60 minutes)
5. WHEN an access token expires, THE Payment System SHALL automatically request a new token
6. THE Payment System SHALL include Bearer token in Authorization header for all API requests
7. THE Payment System SHALL handle token generation failures with appropriate error messages

### Requirement 4: MVola Transaction Status Management

**User Story:** As a user, I want to check the status of my MVola payment, so that I know when my payment is completed.

#### Acceptance Criteria

1. THE Payment System SHALL provide an endpoint to check MVola transaction status using server_correlation_id
2. THE Payment System SHALL call MVola status API endpoint: GET /mvola/mm/transactions/type/merchantpay/1.0.0/status/{serverCorrelationId}
3. THE Payment System SHALL update PaiementTaxe status based on MVola transaction status (pending, completed, failed)
4. THE Payment System SHALL retrieve transaction details using GET /mvola/mm/transactions/type/merchantpay/1.0.0/{transactionId}
5. THE Payment System SHALL store transaction completion timestamp when status changes to completed
6. THE Payment System SHALL extract and store fee information from MVola response
7. THE Payment System SHALL handle status check failures gracefully without affecting existing payment records

### Requirement 5: MVola Callback Handling

**User Story:** As a system, I want to receive real-time notifications from MVola, so that payment status updates are processed immediately.

#### Acceptance Criteria

1. THE Payment System SHALL provide a callback endpoint that accepts PUT requests from MVola
2. THE Payment System SHALL disable CSRF protection for the MVola callback endpoint
3. THE Payment System SHALL disable authentication requirements for the MVola callback endpoint
4. WHEN a callback is received, THE Payment System SHALL extract serverCorrelationId and transactionStatus from the payload
5. THE Payment System SHALL update the corresponding PaiementTaxe record based on serverCorrelationId
6. THE Payment System SHALL extract and store transactionReference and fee information from callback data
7. THE Payment System SHALL return HTTP 200 status with acknowledgment message to MVola

### Requirement 6: MVola Configuration Management

**User Story:** As a system administrator, I want to configure MVola settings through Django settings and environment variables, so that I can manage credentials securely.

#### Acceptance Criteria

1. THE Payment System SHALL read MVola configuration from Django settings (MVOLA_BASE_URL, MVOLA_CONSUMER_KEY, MVOLA_CONSUMER_SECRET, MVOLA_PARTNER_MSISDN, MVOLA_PARTNER_NAME, MVOLA_CALLBACK_URL)
2. THE Payment System SHALL support separate configurations for sandbox (https://devapi.mvola.mg) and production (https://api.mvola.mg) environments
3. THE Payment System SHALL load sensitive credentials from environment variables using python-decouple
4. THE Payment System SHALL validate that all required configuration values are present before allowing MVola payments
5. THE Payment System SHALL provide clear error messages when configuration is missing or invalid
6. THE Payment System SHALL allow configuration of minimum and maximum payment amounts
7. THE Payment System SHALL support configuration of callback URL for receiving transaction notifications

### Requirement 7: Database Model Extensions

**User Story:** As a developer, I want to extend the PaiementTaxe model to support MVola transactions, so that MVola-specific data is properly stored.

#### Acceptance Criteria

1. THE Payment System SHALL add mvola_x_correlation_id field to PaiementTaxe model for storing request correlation ID
2. THE Payment System SHALL add mvola_server_correlation_id field to PaiementTaxe model for storing MVola's transaction identifier
3. THE Payment System SHALL add mvola_transaction_reference field to PaiementTaxe model for storing final transaction reference
4. THE Payment System SHALL add mvola_customer_msisdn field to PaiementTaxe model for storing customer phone number
5. THE Payment System SHALL add mvola_platform_fee field to PaiementTaxe model for storing the 3% platform fee charged to customer
6. THE Payment System SHALL add mvola_gateway_fees field to PaiementTaxe model for storing actual fees charged by MVola gateway
7. THE Payment System SHALL add mvola_status field to PaiementTaxe model for storing MVola-specific status (pending, completed, failed)
8. THE Payment System SHALL ensure all MVola fields are nullable to maintain backward compatibility with existing records

### Requirement 8: Error Handling and Validation

**User Story:** As a system administrator, I want comprehensive error handling and validation, so that payment failures are handled gracefully and users receive clear feedback.

#### Acceptance Criteria

1. THE Payment System SHALL validate amount and customer_msisdn fields before initiating MVola payments
2. WHEN a payment initiation fails, THE Payment System SHALL return HTTP 400 with error details from MVola API
3. THE Payment System SHALL log all MVola API requests and responses for debugging purposes
4. THE Payment System SHALL handle network timeouts with retry logic (maximum 3 attempts)
5. THE Payment System SHALL provide user-friendly error messages in French for common MVola errors
6. THE Payment System SHALL validate MSISDN format (10 digits starting with 03)
7. THE Payment System SHALL handle token generation failures without crashing the application

### Requirement 9: User Interface Integration

**User Story:** As a user, I want to select MVola as a payment method, so that I can pay vehicle taxes using my MVola wallet.

#### Acceptance Criteria

1. THE Payment System SHALL add MVola as a payment method option on the payment creation page
2. WHEN a user selects MVola, THE Payment System SHALL display a phone number input field for MSISDN
3. THE Payment System SHALL validate MSISDN format in real-time as the user types
4. THE Payment System SHALL display MVola logo and branding on the payment selection interface
5. THE Payment System SHALL show payment instructions in French: "Vous recevrez une notification sur votre téléphone MVola pour confirmer le paiement"
6. THE Payment System SHALL display a status indicator showing payment progress (initiated, pending confirmation, completed)
7. THE Payment System SHALL provide a button to manually check payment status after initiation

### Requirement 10: Notification Integration

**User Story:** As a user, I want to receive notifications about my MVola payment status, so that I am informed of successful or failed payments.

#### Acceptance Criteria

1. WHEN a MVola payment is initiated, THE Payment System SHALL create a notification using NotificationService
2. WHEN a MVola payment succeeds, THE Payment System SHALL create a payment confirmation notification with transaction details
3. WHEN a MVola payment fails, THE Payment System SHALL create a payment failed notification with error information
4. THE Payment System SHALL support notifications in French and Malagasy languages based on user preference
5. THE Payment System SHALL include MVola transaction reference (server_correlation_id) in notifications
6. THE Payment System SHALL use existing notification templates with MVola-specific content
7. THE Payment System SHALL trigger notifications both from callback handler and status check endpoints

### Requirement 11: Fee Calculation and Tracking

**User Story:** As a user, I want to see the total amount including MVola fees before payment, so that I know exactly how much will be charged.

#### Acceptance Criteria

1. THE Payment System SHALL apply a 3% transaction fee for all MVola payments
2. WHEN calculating the total payment amount, THE Payment System SHALL add 3% to the base tax amount (total = tax_amount * 1.03)
3. THE Payment System SHALL display the fee breakdown showing: base tax amount, MVola fee (3%), and total amount to pay
4. THE Payment System SHALL store the MVola fee amount in a dedicated field (mvola_platform_fee)
5. THE Payment System SHALL extract actual fees charged by MVola from callback data and store in mvola_gateway_fees field
6. THE Payment System SHALL display both platform fee (3%) and gateway fees on payment detail pages
7. THE Payment System SHALL include fee breakdown in payment receipts showing: "Taxe: X Ar, Frais MVola (3%): Y Ar, Total: Z Ar"

### Requirement 12: Testing and Sandbox Support

**User Story:** As a developer, I want to test MVola integration in sandbox environment, so that I can verify functionality without processing real payments.

#### Acceptance Criteria

1. THE Payment System SHALL support MVola sandbox environment at https://devapi.mvola.mg
2. THE Payment System SHALL use sandbox credentials (consumer key, consumer secret) in development mode
3. THE Payment System SHALL clearly log when operating in sandbox mode
4. THE Payment System SHALL support MVola test MSISDNs provided in sandbox documentation
5. THE Payment System SHALL log all API requests and responses in development mode for debugging
6. THE Payment System SHALL use Django's cache framework (Redis) for token caching in all environments
7. THE Payment System SHALL allow switching between sandbox and production via MVOLA_BASE_URL setting

### Requirement 13: Migration and Data Compatibility

**User Story:** As a system administrator, I want the MVola integration to work with existing payment data, so that historical records remain accessible and consistent.

#### Acceptance Criteria

1. THE Payment System SHALL extend the existing PaiementTaxe model without breaking existing functionality
2. THE Payment System SHALL add MVola-specific fields as nullable fields to support existing records
3. THE Payment System SHALL maintain backward compatibility with existing payment methods (cash, carte_bancaire, mvola, orange_money, airtel_money)
4. THE Payment System SHALL provide database migrations that preserve all existing payment data
5. THE Payment System SHALL support querying payments by methode_paiement='mvola'
6. THE Payment System SHALL maintain existing QR code generation workflow for MVola payments
7. THE Payment System SHALL ensure existing views (PaymentListView, PaymentDetailView) display MVola payments correctly

### Requirement 14: API Endpoints and URL Routing

**User Story:** As a developer, I want well-defined API endpoints for MVola operations, so that the integration is organized and maintainable.

#### Acceptance Criteria

1. THE Payment System SHALL provide POST endpoint at /payments/mvola/initiate/ for initiating MVola payments
2. THE Payment System SHALL provide PUT endpoint at /payments/mvola/callback/ for receiving MVola callbacks
3. THE Payment System SHALL provide GET endpoint at /payments/mvola/status/<server_correlation_id>/ for checking transaction status
4. THE Payment System SHALL use Django REST Framework for API endpoint implementation
5. THE Payment System SHALL require authentication for initiate and status endpoints
6. THE Payment System SHALL disable authentication for callback endpoint (MVola server calls it)
7. THE Payment System SHALL return JSON responses with appropriate HTTP status codes (200, 400, 404, 500)

### Requirement 15: Logging and Monitoring

**User Story:** As a system administrator, I want comprehensive logging of MVola transactions, so that I can troubleshoot issues and monitor system health.

#### Acceptance Criteria

1. THE Payment System SHALL log all MVola API requests with timestamp, endpoint, and correlation ID
2. THE Payment System SHALL log all MVola API responses with status code and response body
3. THE Payment System SHALL log token generation attempts and results
4. THE Payment System SHALL log callback receipts with serverCorrelationId and status
5. THE Payment System SHALL use Python's logging module with appropriate log levels (INFO, WARNING, ERROR)
6. THE Payment System SHALL include correlation IDs in all log messages for request tracing
7. THE Payment System SHALL log payment status transitions (EN_ATTENTE -> PAYE)
