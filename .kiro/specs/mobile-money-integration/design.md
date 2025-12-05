# Design Document: MVola Mobile Money Integration

## Overview

This design document outlines the technical architecture and implementation approach for integrating MVola mobile money payments into the existing vehicle tax payment system. The integration will enable Madagascar users to pay vehicle taxes using their MVola mobile wallets through Telma's Merchant Pay API v1.0.

The design follows a service-oriented architecture pattern, encapsulating MVola-specific logic in dedicated service classes while extending existing models and views to support the new payment method.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ Payment Creation │  │ Payment Status   │  │ Payment List  │ │
│  │      View        │  │     Check        │  │     View      │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ MVola Initiate   │  │ MVola Callback   │  │ MVola Status  │ │
│  │    Endpoint      │  │    Endpoint      │  │   Endpoint    │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              MvolaAPIClient Service                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │  │
│  │  │   OAuth2   │  │  Payment   │  │  Status Check    │   │  │
│  │  │   Token    │  │ Initiation │  │  & Details       │   │  │
│  │  │  Manager   │  │            │  │                  │   │  │
│  │  └────────────┘  └────────────┘  └──────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           MvolaFeeCalculator Service                      │  │
│  │  - Calculate 3% platform fee                              │  │
│  │  - Calculate total amount                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  PaiementTaxe    │  │    Vehicule      │  │   QRCode      │ │
│  │     Model        │  │     Model        │  │    Model      │ │
│  │  (Extended)      │  │                  │  │               │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              MVola API (Telma)                            │  │
│  │  - OAuth2 Token Endpoint                                  │  │
│  │  - Merchant Pay Transaction Endpoint                      │  │
│  │  - Transaction Status Endpoint                            │  │
│  │  - Transaction Details Endpoint                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

#### Payment Initiation Flow
```
User → Payment Form → Initiate Endpoint → MvolaAPIClient
                                              ↓
                                         Get Token (cached)
                                              ↓
                                         POST /merchantpay
                                              ↓
                                         MVola API
                                              ↓
                                         Push to User Phone
                                              ↓
                                         Return serverCorrelationId
                                              ↓
                                         Save PaiementTaxe
                                              ↓
                                         Return to User
```

#### Callback Flow
```
MVola API → PUT /callback → Extract Data → Find PaiementTaxe
                                              ↓
                                         Update Status
                                              ↓
                                         Store Fees
                                              ↓
                                         Create Notification
                                              ↓
                                         Generate QR Code
                                              ↓
                                         Return 200 OK
```

## Components and Interfaces

### 1. MvolaAPIClient Service

**Location:** `payments/services/mvola_service.py`

**Purpose:** Encapsulates all MVola API interactions including authentication, payment initiation, and status checking.

**Class Definition:**
```python
class MvolaAPIClient:
    """
    MVola API client for handling all MVola Merchant Pay operations.
    Manages OAuth2 authentication, payment initiation, and status checks.
    """
    
    def __init__(self):
        """Initialize client with configuration from Django settings"""
        
    def get_access_token(self) -> str:
        """
        Get or refresh OAuth2 access token.
        Caches token for 55 minutes.
        
        Returns:
            str: Bearer access token
            
        Raises:
            MvolaAuthenticationError: If token generation fails
        """
        
    def initiate_payment(
        self,
        amount: Decimal,
        customer_msisdn: str,
        description: str,
        vehicle_plate: str,
        tax_year: int
    ) -> Dict[str, Any]:
        """
        Initiate a merchant pay transaction.
        
        Args:
            amount: Total amount including 3% fee
            customer_msisdn: Customer phone number (0340000000 format)
            description: Transaction description (max 50 chars)
            vehicle_plate: Vehicle registration number
            tax_year: Tax year
            
        Returns:
            dict: {
                'success': bool,
                'x_correlation_id': str,
                'server_correlation_id': str,
                'status': str,
                'error': str (if failed)
            }
            
        Raises:
            MvolaAPIError: If API request fails
        """
        
    def get_transaction_status(self, server_correlation_id: str) -> Dict[str, Any]:
        """
        Check transaction status.
        
        Args:
            server_correlation_id: MVola's transaction identifier
            
        Returns:
            dict: {
                'success': bool,
                'status': str,
                'transaction_reference': str,
                'error': str (if failed)
            }
        """
        
    def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get detailed transaction information.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            dict: Transaction details including fees
        """
```

**Key Methods:**

1. **get_access_token()**
   - Generates Basic Auth header: `Base64(consumer_key:consumer_secret)`
   - Requests token from `/token` endpoint
   - Caches token in Redis for 55 minutes
   - Returns Bearer token for API requests

2. **initiate_payment()**
   - Generates unique X-CorrelationID using UUID4
   - Constructs payment payload with all required fields
   - Sets required headers (Authorization, Version, X-CorrelationID, etc.)
   - Posts to `/mvola/mm/transactions/type/merchantpay/1.0.0/`
   - Returns serverCorrelationId for tracking

3. **get_transaction_status()**
   - Calls GET `/mvola/mm/transactions/type/merchantpay/1.0.0/status/{serverCorrelationId}`
   - Returns current transaction status

### 2. MvolaFeeCalculator Service

**Location:** `payments/services/mvola_fee_calculator.py`

**Purpose:** Handles fee calculations for MVola transactions.

**Class Definition:**
```python
class MvolaFeeCalculator:
    """Calculate fees for MVola transactions"""
    
    PLATFORM_FEE_PERCENTAGE = Decimal('3.00')  # 3%
    
    @staticmethod
    def calculate_total_amount(base_tax_amount: Decimal) -> Dict[str, Decimal]:
        """
        Calculate total amount including 3% platform fee.
        
        Args:
            base_tax_amount: Base vehicle tax amount
            
        Returns:
            dict: {
                'base_amount': Decimal,
                'platform_fee': Decimal,
                'total_amount': Decimal
            }
        """
        platform_fee = (base_tax_amount * MvolaFeeCalculator.PLATFORM_FEE_PERCENTAGE / 100).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        )
        total_amount = base_tax_amount + platform_fee
        
        return {
            'base_amount': base_tax_amount,
            'platform_fee': platform_fee,
            'total_amount': total_amount
        }
    
    @staticmethod
    def extract_gateway_fees(callback_data: Dict) -> Decimal:
        """
        Extract gateway fees from MVola callback data.
        
        Args:
            callback_data: Callback payload from MVola
            
        Returns:
            Decimal: Gateway fee amount or 0 if not present
        """
        fees = callback_data.get('fees', [])
        if fees and len(fees) > 0:
            return Decimal(str(fees[0].get('feeAmount', 0)))
        return Decimal('0')
```

### 3. Database Model Extensions

**Location:** `payments/models.py`

**Extended PaiementTaxe Model:**

```python
class PaiementTaxe(models.Model):
    # ... existing fields ...
    
    # MVola-specific fields
    mvola_x_correlation_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="MVola X-Correlation-ID",
        help_text="Request correlation ID generated by our system"
    )
    
    mvola_server_correlation_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="MVola Server Correlation ID",
        help_text="Transaction identifier from MVola"
    )
    
    mvola_transaction_reference = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="MVola Transaction Reference",
        help_text="Final transaction reference from MVola"
    )
    
    mvola_customer_msisdn = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Customer MSISDN",
        help_text="Customer phone number for MVola payment"
    )
    
    mvola_platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="MVola Platform Fee (3%)",
        help_text="3% platform fee charged to customer"
    )
    
    mvola_gateway_fees = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="MVola Gateway Fees",
        help_text="Actual fees charged by MVola gateway"
    )
    
    mvola_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('pending', 'En attente'),
            ('completed', 'Complété'),
            ('failed', 'Échoué'),
        ],
        verbose_name="Statut MVola"
    )
    
    class Meta:
        indexes = [
            # ... existing indexes ...
            models.Index(fields=['mvola_server_correlation_id']),
            models.Index(fields=['mvola_status']),
        ]
```

### 4. API Endpoints

**Location:** `payments/mvola_views.py`

#### 4.1 Initiate Payment Endpoint

```python
class MvolaInitiatePaymentView(APIView):
    """
    POST /api/payments/mvola/initiate/
    
    Initiate a MVola payment transaction.
    
    Request Body:
    {
        "vehicle_plate": "1234AB01",
        "tax_year": 2024,
        "customer_msisdn": "0340000000"
    }
    
    Response (Success):
    {
        "success": true,
        "payment_id": "uuid",
        "server_correlation_id": "...",
        "total_amount": 103000,
        "base_amount": 100000,
        "platform_fee": 3000,
        "message": "Paiement initié. Veuillez confirmer sur votre téléphone MVola."
    }
    
    Response (Error):
    {
        "success": false,
        "error": "Message d'erreur"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Validate input
        # Calculate tax amount
        # Calculate fees
        # Initiate MVola payment
        # Create PaiementTaxe record
        # Return response
```

#### 4.2 Callback Endpoint

```python
class MvolaCallbackView(APIView):
    """
    PUT /api/payments/mvola/callback/
    
    Receive transaction status updates from MVola.
    
    Request Body (from MVola):
    {
        "serverCorrelationId": "...",
        "transactionStatus": "completed",
        "transactionReference": "...",
        "fees": [
            {
                "feeAmount": "500"
            }
        ]
    }
    
    Response:
    {
        "status": "received"
    }
    """
    authentication_classes = []
    permission_classes = []
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def put(self, request):
        # Extract callback data
        # Find PaiementTaxe by server_correlation_id
        # Update status
        # Store fees
        # Create notification
        # Generate QR code if completed
        # Return acknowledgment
```

#### 4.3 Status Check Endpoint

```python
class MvolaStatusCheckView(APIView):
    """
    GET /api/payments/mvola/status/<server_correlation_id>/
    
    Check transaction status manually.
    
    Response:
    {
        "success": true,
        "status": "completed",
        "transaction_reference": "...",
        "payment_status": "PAYE"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, server_correlation_id):
        # Verify user owns the payment
        # Call MVola status API
        # Update local record
        # Return status
```

### 5. URL Configuration

**Location:** `payments/urls.py`

```python
from django.urls import path
from .mvola_views import (
    MvolaInitiatePaymentView,
    MvolaCallbackView,
    MvolaStatusCheckView
)

urlpatterns = [
    # ... existing patterns ...
    
    # MVola endpoints
    path('mvola/initiate/', MvolaInitiatePaymentView.as_view(), name='mvola-initiate'),
    path('mvola/callback/', MvolaCallbackView.as_view(), name='mvola-callback'),
    path('mvola/status/<str:server_correlation_id>/', MvolaStatusCheckView.as_view(), name='mvola-status'),
]
```

## Data Models

### PaiementTaxe Model State Diagram

```
┌─────────────┐
│   IMPAYE    │ (Initial state)
└──────┬──────┘
       │
       │ User initiates MVola payment
       ▼
┌─────────────┐
│ EN_ATTENTE  │ (MVola payment initiated)
│ mvola_status│ = 'pending'
└──────┬──────┘
       │
       │ MVola callback received
       │ OR status check completed
       ▼
┌─────────────┐
│    PAYE     │ (Payment completed)
│ mvola_status│ = 'completed'
│ QR generated│
└─────────────┘
       │
       │ Payment failed
       ▼
┌─────────────┐
│   ANNULE    │ (Payment failed/cancelled)
│ mvola_status│ = 'failed'
└─────────────┘
```

### Database Migration Strategy

**Migration File:** `payments/migrations/000X_add_mvola_fields.py`

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('payments', '000X_previous_migration'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='paiementtaxe',
            name='mvola_x_correlation_id',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paiementtaxe',
            name='mvola_server_correlation_id',
            field=models.CharField(max_length=100, null=True, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name='paiementtaxe',
            name='mvola_transaction_reference',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paiementtaxe',
            name='mvola_customer_msisdn',
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paiementtaxe',
            name='mvola_platform_fee',
            field=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paiementtaxe',
            name='mvola_gateway_fees',
            field=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paiementtaxe',
            name='mvola_status',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddIndex(
            model_name='paiementtaxe',
            index=models.Index(fields=['mvola_server_correlation_id'], name='payments_pa_mvola_s_idx'),
        ),
        migrations.AddIndex(
            model_name='paiementtaxe',
            index=models.Index(fields=['mvola_status'], name='payments_pa_mvola_st_idx'),
        ),
    ]
```

## Error Handling

### Error Hierarchy

```python
class MvolaError(Exception):
    """Base exception for MVola-related errors"""
    pass

class MvolaAuthenticationError(MvolaError):
    """Raised when OAuth2 authentication fails"""
    pass

class MvolaAPIError(MvolaError):
    """Raised when MVola API request fails"""
    pass

class MvolaValidationError(MvolaError):
    """Raised when input validation fails"""
    pass

class MvolaCallbackError(MvolaError):
    """Raised when callback processing fails"""
    pass
```

### Error Response Format

```json
{
    "success": false,
    "error": "Message d'erreur en français",
    "error_code": "MVOLA_AUTH_FAILED",
    "details": {
        "field": "customer_msisdn",
        "message": "Format de numéro invalide"
    }
}
```

### Common Error Scenarios

| Scenario | HTTP Status | Error Code | User Message (FR) |
|----------|-------------|------------|-------------------|
| Invalid MSISDN | 400 | INVALID_MSISDN | "Numéro de téléphone invalide. Format attendu: 0340000000" |
| Token generation failed | 500 | AUTH_FAILED | "Erreur d'authentification MVola. Veuillez réessayer." |
| Payment initiation failed | 400 | PAYMENT_FAILED | "Impossible d'initier le paiement. Veuillez vérifier votre solde MVola." |
| Transaction not found | 404 | NOT_FOUND | "Transaction introuvable" |
| Callback processing error | 500 | CALLBACK_ERROR | "Erreur lors du traitement de la notification MVola" |

## Testing Strategy

### Unit Tests

**Location:** `payments/tests/test_mvola_service.py`

```python
class MvolaAPIClientTests(TestCase):
    """Test MVola API client methods"""
    
    def test_get_access_token_success(self):
        """Test successful token generation"""
        
    def test_get_access_token_cached(self):
        """Test token is retrieved from cache"""
        
    def test_initiate_payment_success(self):
        """Test successful payment initiation"""
        
    def test_initiate_payment_invalid_msisdn(self):
        """Test payment initiation with invalid MSISDN"""
        
    def test_get_transaction_status(self):
        """Test transaction status check"""
```

**Location:** `payments/tests/test_mvola_fee_calculator.py`

```python
class MvolaFeeCalculatorTests(TestCase):
    """Test fee calculation logic"""
    
    def test_calculate_total_amount(self):
        """Test 3% fee calculation"""
        base_amount = Decimal('100000')
        result = MvolaFeeCalculator.calculate_total_amount(base_amount)
        
        self.assertEqual(result['base_amount'], Decimal('100000'))
        self.assertEqual(result['platform_fee'], Decimal('3000'))
        self.assertEqual(result['total_amount'], Decimal('103000'))
    
    def test_extract_gateway_fees(self):
        """Test gateway fee extraction from callback"""
```

### Integration Tests

**Location:** `payments/tests/test_mvola_integration.py`

```python
class MvolaIntegrationTests(TestCase):
    """Test full MVola payment flow"""
    
    def test_full_payment_flow(self):
        """Test complete payment flow from initiation to completion"""
        # 1. Initiate payment
        # 2. Verify PaiementTaxe created
        # 3. Simulate callback
        # 4. Verify status updated
        # 5. Verify QR code generated
        
    def test_callback_processing(self):
        """Test callback endpoint"""
        
    def test_status_check(self):
        """Test status check endpoint"""
```

### Sandbox Testing

**Test Credentials:**
- Base URL: `https://devapi.mvola.mg`
- Consumer Key: (provided by MVola)
- Consumer Secret: (provided by MVola)
- Test MSISDN: (provided by MVola)

**Test Scenarios:**
1. Successful payment with test MSISDN
2. Failed payment (insufficient balance)
3. Timeout scenario
4. Callback processing
5. Status check after completion

## Security Considerations

### 1. Credential Management

- Store credentials in environment variables
- Never commit credentials to version control
- Use Django's `SECRET_KEY` for encryption
- Rotate credentials regularly

### 2. API Security

- Implement rate limiting on endpoints (10 requests/minute per user)
- Validate all input data
- Use HTTPS for all communications
- Log all API interactions for audit

### 3. Callback Security

- Validate callback source (IP whitelist if available)
- Verify serverCorrelationId exists in database
- Implement idempotency checks
- Log all callback attempts

### 4. Data Protection

- Encrypt sensitive fields at rest
- Mask MSISDN in logs (show only last 4 digits)
- Implement proper access controls
- Follow GDPR/data protection guidelines

## Configuration

### Django Settings

**Location:** `taxcollector_project/settings.py`

```python
# MVola Configuration
MVOLA_BASE_URL = config('MVOLA_BASE_URL', default='https://devapi.mvola.mg')
MVOLA_CONSUMER_KEY = config('MVOLA_CONSUMER_KEY')
MVOLA_CONSUMER_SECRET = config('MVOLA_CONSUMER_SECRET')
MVOLA_PARTNER_MSISDN = config('MVOLA_PARTNER_MSISDN')
MVOLA_PARTNER_NAME = config('MVOLA_PARTNER_NAME')
MVOLA_CALLBACK_URL = config('MVOLA_CALLBACK_URL')

# Cache configuration for token storage
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'taxcollector',
        'TIMEOUT': 3600,
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'mvola_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/mvola.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'payments.mvola': {
            'handlers': ['mvola_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Environment Variables

**Location:** `.env`

```bash
# MVola Sandbox Configuration
MVOLA_BASE_URL=https://devapi.mvola.mg
MVOLA_CONSUMER_KEY=your_consumer_key_here
MVOLA_CONSUMER_SECRET=your_consumer_secret_here
MVOLA_PARTNER_MSISDN=0340000000
MVOLA_PARTNER_NAME=YourCompanyName
MVOLA_CALLBACK_URL=https://yourdomain.com/api/payments/mvola/callback/

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1
```

## Deployment Considerations

### Prerequisites

1. **Redis Server**
   - Required for token caching
   - Install: `sudo apt-get install redis-server`
   - Start: `sudo systemctl start redis`

2. **SSL Certificate**
   - Required for callback URL
   - Use Let's Encrypt or commercial certificate

3. **MVola Production Credentials**
   - Request from MVola developer portal
   - Update environment variables

### Deployment Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Configure environment variables
4. Test in sandbox environment
5. Update to production credentials
6. Deploy to production server
7. Configure callback URL with MVola
8. Monitor logs and transactions

### Monitoring

- Monitor Redis cache hit rate
- Track token refresh frequency
- Monitor API response times
- Alert on failed transactions
- Track callback receipt rate

## Performance Optimization

### Caching Strategy

1. **Token Caching**
   - Cache access tokens for 55 minutes
   - Reduce token generation requests
   - Use Redis for distributed caching

2. **Query Optimization**
   - Add database indexes on MVola fields
   - Use select_related for vehicle queries
   - Implement pagination for payment lists

### Scalability

1. **Async Processing**
   - Consider Celery for status checks
   - Queue callback processing
   - Implement retry logic

2. **Load Balancing**
   - Distribute API requests
   - Use multiple Redis instances
   - Implement circuit breakers

## Future Enhancements

1. **Webhook Signature Validation**
   - Implement HMAC signature verification
   - Enhance callback security

2. **Retry Mechanism**
   - Automatic retry for failed payments
   - Exponential backoff strategy

3. **Admin Dashboard**
   - MVola transaction monitoring
   - Fee reconciliation reports
   - Status analytics

4. **Multi-Provider Support**
   - Abstract payment gateway interface
   - Add Airtel Money and Orange Money
   - Unified payment selection UI

5. **Refund Support**
   - Implement MVola refund API
   - Refund workflow and approval
   - Refund tracking and reporting
