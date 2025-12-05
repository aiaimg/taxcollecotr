# Implementation Plan: MVola Mobile Money Integration

## Task Overview

This implementation plan breaks down the MVola integration into discrete, manageable coding tasks. Each task builds incrementally on previous tasks to create a complete, working MVola payment integration.

## Implementation Tasks

- [x] 1. Set up project dependencies and configuration
  - Install required Python packages (requests, python-decouple, django-redis)
  - Configure Redis cache backend in Django settings
  - Add MVola configuration variables to settings.py
  - Create .env.example file with MVola configuration template
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 2. Extend PaiementTaxe model with MVola fields
  - Add mvola_x_correlation_id field (CharField, max_length=100, nullable)
  - Add mvola_server_correlation_id field (CharField, max_length=100, nullable, indexed)
  - Add mvola_transaction_reference field (CharField, max_length=100, nullable)
  - Add mvola_customer_msisdn field (CharField, max_length=15, nullable)
  - Add mvola_platform_fee field (DecimalField, max_digits=12, decimal_places=2, nullable)
  - Add mvola_gateway_fees field (DecimalField, max_digits=12, decimal_places=2, nullable)
  - Add mvola_status field (CharField, max_length=20, nullable, choices)
  - Create and run database migration
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 13.1, 13.2, 13.4_

- [x] 3. Create MVola service module structure
  - Create payments/services/mvola/ directory
  - Create __init__.py to export main classes
  - Create exceptions.py with MVola error classes (MvolaError, MvolaAuthenticationError, MvolaAPIError, MvolaValidationError, MvolaCallbackError)
  - Create constants.py with MVola API constants (endpoints, headers, timeouts)
  - _Requirements: 1.1, 8.1, 8.7_

- [x] 4. Implement MvolaFeeCalculator service
  - Create payments/services/mvola/fee_calculator.py
  - Implement calculate_total_amount() static method with 3% fee calculation
  - Implement extract_gateway_fees() static method for callback data parsing
  - Add rounding logic (ROUND_HALF_UP to nearest Ariary)
  - Write unit tests for fee calculations
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 5. Implement OAuth2 token management in MvolaAPIClient
  - Create payments/services/mvola/api_client.py
  - Implement __init__() method to load configuration from Django settings
  - Implement get_access_token() method with Basic Auth header generation
  - Implement token caching using Django cache framework (55-minute TTL)
  - Add token refresh logic when cache miss occurs
  - Handle authentication errors with MvolaAuthenticationError
  - Add logging for token generation attempts
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 15.3_

- [x] 6. Implement payment initiation in MvolaAPIClient
  - Implement initiate_payment() method in MvolaAPIClient
  - Generate unique X-CorrelationID using uuid.uuid4()
  - Construct payment payload with all required fields (amount, currency, descriptionText, requestDate, debitParty, creditParty, metadata, requestingOrganisationTransactionReference)
  - Set all required headers (Authorization, Version, X-CorrelationID, UserLanguage, UserAccountIdentifier, partnerName, X-Callback-URL, Content-Type, Cache-Control)
  - Make POST request to /mvola/mm/transactions/type/merchantpay/1.0.0/
  - Parse response and extract serverCorrelationId
  - Handle API errors and return structured response
  - Add logging for payment initiation requests and responses
  - _Requirements: 2.1, 2.5, 2.6, 2.7, 8.2, 15.1, 15.2_

- [x] 7. Implement transaction status checking in MvolaAPIClient
  - Implement get_transaction_status() method in MvolaAPIClient
  - Set required headers for status check request
  - Make GET request to /mvola/mm/transactions/type/merchantpay/1.0.0/status/{serverCorrelationId}
  - Parse response and extract status information
  - Implement get_transaction_details() method for detailed transaction info
  - Handle API errors gracefully
  - Add logging for status check requests
  - _Requirements: 4.1, 4.2, 4.7, 15.1, 15.2_

- [x] 8. Implement MSISDN validation utility
  - Create payments/services/mvola/validators.py
  - Implement validate_msisdn() function to check Madagascar phone format (0340000000)
  - Add regex pattern for MSISDN validation (^03[0-9]{8}$)
  - Return cleaned MSISDN or raise MvolaValidationError
  - Write unit tests for MSISDN validation
  - _Requirements: 2.2, 8.1, 8.6_

- [x] 9. Create MVola payment initiation API endpoint
  - Create payments/mvola_views.py file
  - Implement MvolaInitiatePaymentView (APIView)
  - Add IsAuthenticated permission class
  - Validate request data (vehicle_plate, tax_year, customer_msisdn)
  - Retrieve vehicle and verify ownership
  - Calculate tax amount using TaxCalculationService
  - Calculate total amount with 3% fee using MvolaFeeCalculator
  - Validate MSISDN format
  - Call MvolaAPIClient.initiate_payment()
  - Create PaiementTaxe record with MVola fields populated
  - Return JSON response with payment details
  - Handle errors and return appropriate HTTP status codes
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.7, 8.1, 8.2, 14.1, 14.4, 14.7_

- [x] 10. Create MVola callback API endpoint
  - Implement MvolaCallbackView (APIView) in payments/mvola_views.py
  - Disable authentication and CSRF protection using decorators
  - Extract callback data (serverCorrelationId, transactionStatus, transactionReference, fees)
  - Find PaiementTaxe by mvola_server_correlation_id
  - Update payment status based on transactionStatus
  - Extract and store gateway fees using MvolaFeeCalculator.extract_gateway_fees()
  - Update mvola_status, mvola_transaction_reference, and mvola_gateway_fees fields
  - Set statut to 'PAYE' and date_paiement when status is 'completed'
  - Return HTTP 200 with acknowledgment JSON
  - Handle errors and return appropriate status codes
  - Add comprehensive logging for callback processing
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 11.1, 11.2, 14.2, 14.5, 14.7, 15.4_

- [x] 11. Create MVola status check API endpoint
  - Implement MvolaStatusCheckView (APIView) in payments/mvola_views.py
  - Add IsAuthenticated permission class
  - Retrieve PaiementTaxe by mvola_server_correlation_id
  - Verify user owns the payment (check vehicle ownership)
  - Call MvolaAPIClient.get_transaction_status()
  - Update PaiementTaxe status based on MVola response
  - Return JSON response with current status
  - Handle errors appropriately
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.7, 14.3, 14.4, 14.7_

- [x] 12. Configure URL routing for MVola endpoints
  - Add MVola URL patterns to payments/urls.py
  - Map /mvola/initiate/ to MvolaInitiatePaymentView
  - Map /mvola/callback/ to MvolaCallbackView
  - Map /mvola/status/<str:server_correlation_id>/ to MvolaStatusCheckView
  - Ensure URL names are properly set (mvola-initiate, mvola-callback, mvola-status)
  - _Requirements: 14.1, 14.2, 14.3_

- [x] 13. Integrate MVola with notification system
  - Update callback handler to create notifications using NotificationService
  - Create payment initiated notification when MVola payment starts
  - Create payment confirmation notification when payment succeeds
  - Create payment failed notification when payment fails
  - Include MVola transaction reference in notification content
  - Support French and Malagasy languages based on user preference
  - Use existing notification templates with MVola-specific variables
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [x] 14. Integrate MVola with QR code generation
  - Update callback handler to generate QR code when payment is completed
  - Use existing QRCode model and generation logic
  - Link QR code to PaiementTaxe record
  - Set QR code expiration to 1 year from payment date
  - Ensure QR code is shared across all payment methods for same vehicle/year
  - _Requirements: 13.6_

- [x] 15. Configure Django settings for MVola
  - Add MVOLA_BASE_URL, MVOLA_CONSUMER_KEY, MVOLA_CONSUMER_SECRET, MVOLA_PARTNER_MSISDN, MVOLA_PARTNER_NAME, MVOLA_CALLBACK_URL to settings.py
  - Configure cache backend in CACHES setting  Redis
  - Add MVola-specific logger configuration in LOGGING setting
  - Update .env.example file with MVola configuration template
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 15.1, 15.2, 15.3_

- [x] 16. Integrate MVola with payment creation view
  - Update PaymentCreateView in payments/views.py to add MVola option
  - Add customer_msisdn field to payment form when MVola is selected
  - Calculate and display total amount with 3% fee for MVola
  - Show fee breakdown (base tax, platform fee, total) in UI
  - Handle MVola payment initiation when form is submitted
  - Redirect to MVola status page after initiation
  - _Requirements: 9.1, 9.2, 9.3, 11.3, 11.7_

- [x] 17. Create MVola payment status display template
  - Create templates/payments/mvola_status.html
  - Display payment status indicator (initiated, pending, completed, failed)
  - Show MVola transaction details (server_correlation_id, customer_msisdn)
  - Display fee breakdown (base amount, platform fee, total)
  - Add "Check Status" button that calls status check endpoint
  - Show MVola logo and branding
  - Display payment instructions in French
  - Add auto-refresh functionality for pending payments
  - _Requirements: 9.4, 9.5, 9.6, 9.7, 11.3, 11.7_

- [x] 18. Update payment list and detail views for MVola
  - Update PaymentListView template (templates/payments/payment_list.html) to display MVola logo/icon for MVola payments
  - Update PaymentDetailView template (templates/payments/payment_detail.html) to show MVola-specific information
  - Display MVola transaction reference (mvola_transaction_reference) in payment details
  - Show fee breakdown (base amount, platform fee, gateway fees, total) in payment detail view
  - Add MVola-specific status indicators (mvola_status badge)
  - Display customer MSISDN (masked for privacy: 034****000)
  - Ensure backward compatibility with existing payment methods
  - _Requirements: 13.5, 13.7_

- [ ] 19. Update admin interface for MVola payments
  - Add MVola fields to PaiementTaxeAdmin list_display (mvola_status, mvola_server_correlation_id)
  - Add filters for mvola_status in list_filter
  - Add search fields for mvola_server_correlation_id and mvola_customer_msisdn
  - Create fieldset to group MVola-related fields in admin detail view
  - Add readonly fields for MVola transaction data (x_correlation_id, server_correlation_id, transaction_reference)
  - Display MVola fee information (platform_fee, gateway_fees) in admin
  - _Requirements: 6.5_

- [ ] 20. Create MVola integration documentation
  - Create MVOLA_INTEGRATION.md documentation file
  - Document environment variable setup for sandbox and production
  - Document MVola sandbox credentials setup process
  - Document callback URL configuration with MVola
  - Document production deployment steps and checklist
  - Document monitoring and logging setup
  - Create troubleshooting guide for common issues
  - Document API endpoints and their usage
  - _Requirements: 6.1, 6.2, 6.3, 6.7, 12.1, 12.2_

## Task Dependencies

```
COMPLETED (Tasks 1-17):
✓ Core MVola Service Implementation
  - Models with MVola fields (Task 2)
  - Service layer (Tasks 3-8)
    - API client with OAuth2 authentication
    - Fee calculator service
    - MSISDN validation
    - Exception handling
  - API endpoints (Tasks 9-12)
    - Payment initiation endpoint
    - Callback endpoint
    - Status check endpoint
    - URL routing
  - Integration (Tasks 13-17)
    - Notifications integration
    - QR code generation
    - Django settings configuration
    - Payment creation view integration
    - MVola status template

REMAINING (Tasks 18-20):
18 (Payment List/Detail Views) → 19 (Admin Interface) → 20 (Documentation)
```

## Estimated Timeline

- **Phase 1: UI Enhancements** (Task 18): 0.5-1 day
  - Update payment list and detail views for MVola display

- **Phase 2: Admin Interface** (Task 19): 0.5 day
  - Add MVola fields to admin interface

- **Phase 3: Documentation** (Task 20): 1 day
  - Create comprehensive MVola integration documentation

**Total Estimated Time:** 2-2.5 days

## Success Criteria

- [x] Core MVola API client implemented with OAuth2 authentication
- [x] Payment initiation endpoint working
- [x] Callback endpoint processing MVola notifications
- [x] Status check endpoint implemented
- [x] MVola fields added to PaiementTaxe model
- [x] Fee calculator service implemented (3% platform fee)
- [x] MSISDN validation implemented
- [x] Notifications integrated for payment events
- [x] QR codes generated for completed payments
- [x] Django settings configured with MVola credentials
- [x] Cache configured for token storage (LocMemCache, Redis recommended for production)
- [x] MVola logging configured
- [x] UI shows MVola as payment option
- [x] MVola status page displays payment details
- [x] Unit tests created for core MVola services
- [ ] Payment list and detail views display MVola payments correctly
- [ ] Admin interface displays MVola data correctly
- [ ] Documentation is complete and accurate

## Notes

- Each task should be completed and tested before moving to the next
- Commit code after completing each task
- Update this document to track progress
- Add notes for any deviations from the plan
- Consult design document for implementation details
- Refer to requirements document for acceptance criteria
