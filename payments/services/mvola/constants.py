"""
MVola API Constants

Constants for MVola Merchant Pay API v1.0 integration including
endpoints, headers, timeouts, and configuration values.
"""

# API Endpoints
TOKEN_ENDPOINT = "/token"
MERCHANT_PAY_ENDPOINT = "/mvola/mm/transactions/type/merchantpay/1.0.0/"
TRANSACTION_STATUS_ENDPOINT = "/mvola/mm/transactions/type/merchantpay/1.0.0/status/{serverCorrelationId}"
TRANSACTION_DETAILS_ENDPOINT = "/mvola/mm/transactions/type/merchantpay/1.0.0/{transactionId}"

# API Version
API_VERSION = "1.0"

# HTTP Headers
HEADER_AUTHORIZATION = "Authorization"
HEADER_VERSION = "Version"
HEADER_X_CORRELATION_ID = "X-CorrelationID"
HEADER_USER_LANGUAGE = "UserLanguage"
HEADER_USER_ACCOUNT_IDENTIFIER = "UserAccountIdentifier"
HEADER_PARTNER_NAME = "partnerName"
HEADER_X_CALLBACK_URL = "X-Callback-URL"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_CACHE_CONTROL = "Cache-Control"

# Header Values
CONTENT_TYPE_JSON = "application/json"
CACHE_CONTROL_NO_CACHE = "no-cache"
USER_LANGUAGE_FR = "FR"

# OAuth2 Configuration
OAUTH_GRANT_TYPE = "client_credentials"
OAUTH_SCOPE = "EXT_INT_MVOLA_SCOPE"

# Token Configuration
TOKEN_CACHE_KEY_PREFIX = "mvola_access_token"
TOKEN_CACHE_TTL = 3300  # 55 minutes (token expires in 60 minutes)
TOKEN_EXPIRY_SECONDS = 3600  # 1 hour

# Request Timeouts (in seconds)
TIMEOUT_TOKEN_REQUEST = 10
TIMEOUT_PAYMENT_REQUEST = 30
TIMEOUT_STATUS_REQUEST = 15
TIMEOUT_DETAILS_REQUEST = 15

# Retry Configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff: 1s, 2s, 4s

# Payment Limits (in Ariary)
MIN_PAYMENT_AMOUNT = 100
MAX_PAYMENT_AMOUNT = 5000000

# MSISDN Validation
MSISDN_REGEX = r"^03[0-9]{8}$"
MSISDN_LENGTH = 10

# Transaction Status Values
STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# Currency
CURRENCY_CODE = "Ar"
CURRENCY_NAME = "Ariary"

# Fee Configuration
PLATFORM_FEE_PERCENTAGE = 3.0  # 3% platform fee

# Description Limits
MAX_DESCRIPTION_LENGTH = 50

# Callback Configuration
CALLBACK_METHOD = "PUT"
CALLBACK_TIMEOUT = 30

# Logging
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"

# Error Messages (French)
ERROR_INVALID_MSISDN = "Numéro de téléphone invalide. Format attendu: 0340000000"
ERROR_AUTH_FAILED = "Erreur d'authentification MVola. Veuillez réessayer."
ERROR_PAYMENT_FAILED = "Impossible d'initier le paiement. Veuillez vérifier votre solde MVola."
ERROR_TRANSACTION_NOT_FOUND = "Transaction introuvable"
ERROR_CALLBACK_ERROR = "Erreur lors du traitement de la notification MVola"
ERROR_AMOUNT_TOO_LOW = f"Le montant minimum est de {MIN_PAYMENT_AMOUNT} Ar"
ERROR_AMOUNT_TOO_HIGH = f"Le montant maximum est de {MAX_PAYMENT_AMOUNT} Ar"
ERROR_NETWORK_TIMEOUT = "Délai d'attente dépassé. Veuillez réessayer."
ERROR_INVALID_RESPONSE = "Réponse invalide de MVola"
ERROR_MISSING_CONFIGURATION = "Configuration MVola manquante"

# Success Messages (French)
SUCCESS_PAYMENT_INITIATED = "Paiement initié. Veuillez confirmer sur votre téléphone MVola."
SUCCESS_PAYMENT_COMPLETED = "Paiement complété avec succès"
SUCCESS_CALLBACK_RECEIVED = "Notification MVola reçue"

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503
