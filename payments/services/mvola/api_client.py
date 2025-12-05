"""
MVola API Client

Handles all interactions with MVola Merchant Pay API v1.0 including:
- OAuth2 authentication and token management
- Payment initiation
- Transaction status checking
- Transaction details retrieval
"""

import base64
import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from django.conf import settings
from django.core.cache import cache

import requests

from .constants import (
    API_VERSION,
    CACHE_CONTROL_NO_CACHE,
    CONTENT_TYPE_JSON,
    CURRENCY_CODE,
    ERROR_AUTH_FAILED,
    ERROR_INVALID_RESPONSE,
    ERROR_MISSING_CONFIGURATION,
    ERROR_NETWORK_TIMEOUT,
    ERROR_PAYMENT_FAILED,
    ERROR_TRANSACTION_NOT_FOUND,
    HEADER_AUTHORIZATION,
    HEADER_CACHE_CONTROL,
    HEADER_CONTENT_TYPE,
    HEADER_PARTNER_NAME,
    HEADER_USER_ACCOUNT_IDENTIFIER,
    HEADER_USER_LANGUAGE,
    HEADER_VERSION,
    HEADER_X_CALLBACK_URL,
    HEADER_X_CORRELATION_ID,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    MAX_DESCRIPTION_LENGTH,
    MERCHANT_PAY_ENDPOINT,
    OAUTH_GRANT_TYPE,
    OAUTH_SCOPE,
    STATUS_PENDING,
    TIMEOUT_DETAILS_REQUEST,
    TIMEOUT_PAYMENT_REQUEST,
    TIMEOUT_STATUS_REQUEST,
    TIMEOUT_TOKEN_REQUEST,
    TOKEN_CACHE_KEY_PREFIX,
    TOKEN_CACHE_TTL,
    TOKEN_ENDPOINT,
    TRANSACTION_DETAILS_ENDPOINT,
    TRANSACTION_STATUS_ENDPOINT,
    USER_LANGUAGE_FR,
)
from .exceptions import MvolaAPIError, MvolaAuthenticationError

# Configure logger for MVola operations
logger = logging.getLogger("payments.mvola")


class MvolaAPIClient:
    """
    MVola API client for handling all MVola Merchant Pay operations.

    This client manages OAuth2 authentication with automatic token refresh,
    payment initiation, status checking, and transaction details retrieval.

    Attributes:
        base_url (str): Base URL for MVola API (sandbox or production)
        consumer_key (str): OAuth2 consumer key
        consumer_secret (str): OAuth2 consumer secret
        partner_msisdn (str): Merchant's registered phone number
        partner_name (str): Merchant's registered name
        callback_url (str): URL for receiving transaction callbacks
    """

    def __init__(self):
        """
        Initialize MVola API client with configuration from Django settings.

        Loads all required configuration values from Django settings and validates
        that all necessary credentials are present.

        Raises:
            MvolaAuthenticationError: If required configuration is missing
        """
        # Load configuration from Django settings
        self.base_url = getattr(settings, "MVOLA_BASE_URL", "https://devapi.mvola.mg")
        self.consumer_key = getattr(settings, "MVOLA_CONSUMER_KEY", None)
        self.consumer_secret = getattr(settings, "MVOLA_CONSUMER_SECRET", None)
        self.partner_msisdn = getattr(settings, "MVOLA_PARTNER_MSISDN", None)
        self.partner_name = getattr(settings, "MVOLA_PARTNER_NAME", None)
        self.callback_url = getattr(settings, "MVOLA_CALLBACK_URL", None)

        # Validate required configuration
        self._validate_configuration()

        # Log initialization with environment info
        env_type = "PRODUCTION" if "api.mvola.mg" in self.base_url else "SANDBOX"
        logger.info(
            f"MvolaAPIClient initialized with base_url={self.base_url}, "
            f"partner_name={self.partner_name}, environment={env_type}"
        )

        # Warn about sandbox test numbers if in sandbox
        if env_type == "SANDBOX":
            logger.info(
                "SANDBOX environment detected. " "Note: Sandbox test phone numbers are fixed: 0343500003 or 0343500004"
            )

    def _validate_configuration(self):
        """
        Validate that all required configuration values are present.

        Raises:
            MvolaAuthenticationError: If any required configuration is missing
        """
        missing_configs = []

        # Check if credentials exist and are not just whitespace
        if not self.consumer_key or not self.consumer_key.strip():
            missing_configs.append("MVOLA_CONSUMER_KEY")
        elif self.consumer_key != self.consumer_key.strip():
            logger.warning("Consumer Key contient des espaces en début/fin. " "Ils seront automatiquement supprimés.")

        if not self.consumer_secret or not self.consumer_secret.strip():
            missing_configs.append("MVOLA_CONSUMER_SECRET")
        elif self.consumer_secret != self.consumer_secret.strip():
            logger.warning(
                "Consumer Secret contient des espaces en début/fin. " "Ils seront automatiquement supprimés."
            )

        if not self.partner_msisdn:
            missing_configs.append("MVOLA_PARTNER_MSISDN")
        if not self.partner_name:
            missing_configs.append("MVOLA_PARTNER_NAME")
        if not self.callback_url:
            missing_configs.append("MVOLA_CALLBACK_URL")

        if missing_configs:
            error_msg = f"{ERROR_MISSING_CONFIGURATION}: {', '.join(missing_configs)}"
            logger.error(f"Configuration validation failed: {error_msg}")
            raise MvolaAuthenticationError(error_msg)

        # Log environment detection
        env_type = "PRODUCTION" if "api.mvola.mg" in self.base_url else "SANDBOX"
        logger.info(
            f"MVola configuration validated: "
            f"environment={env_type}, "
            f"base_url={self.base_url}, "
            f"partner_name={self.partner_name}, "
            f"partner_msisdn={self.partner_msisdn[:3]}***"
        )

    def _generate_basic_auth_header(self) -> str:
        """
        Generate Basic Authentication header for OAuth2 token request.

        Creates a Base64-encoded string from consumer_key:consumer_secret
        as required by MVola's OAuth2 implementation.

        Returns:
            str: Basic authentication header value (e.g., "Basic base64string")
        """
        # Strip any whitespace from credentials (common issue)
        consumer_key = self.consumer_key.strip() if self.consumer_key else ""
        consumer_secret = self.consumer_secret.strip() if self.consumer_secret else ""

        # Validate credentials are not empty after stripping
        if not consumer_key or not consumer_secret:
            raise MvolaAuthenticationError(
                "Consumer Key ou Consumer Secret est vide. "
                "Vérifiez que les identifiants sont correctement configurés."
            )

        # Combine consumer key and secret with colon separator
        credentials = f"{consumer_key}:{consumer_secret}"

        # Encode to bytes and then to base64
        credentials_bytes = credentials.encode("utf-8")
        base64_credentials = base64.b64encode(credentials_bytes).decode("utf-8")

        # Log credential info (without exposing secrets)
        logger.debug(
            f"Generated Basic Auth header: "
            f"consumer_key_length={len(consumer_key)}, "
            f"consumer_secret_length={len(consumer_secret)}, "
            f"base64_length={len(base64_credentials)}"
        )

        # Return Basic auth header
        return f"Basic {base64_credentials}"

    def _get_token_cache_key(self) -> str:
        """
        Generate cache key for storing access token.

        Returns:
            str: Cache key for token storage
        """
        return f"{TOKEN_CACHE_KEY_PREFIX}_{self.consumer_key}"

    def get_access_token(self) -> str:
        """
        Get or refresh OAuth2 access token.

        This method implements token caching to minimize token generation requests.
        Tokens are cached for 55 minutes (MVola tokens expire in 60 minutes).

        Flow:
        1. Check if valid token exists in cache
        2. If cache hit, return cached token
        3. If cache miss, request new token from MVola
        4. Cache new token for 55 minutes
        5. Return new token

        Returns:
            str: Bearer access token for API requests

        Raises:
            MvolaAuthenticationError: If token generation fails
        """
        # Generate cache key
        cache_key = self._get_token_cache_key()

        # Try to get token from cache
        cached_token = cache.get(cache_key)

        if cached_token:
            logger.info(f"Access token retrieved from cache (key={cache_key})")
            return cached_token

        # Cache miss - request new token
        logger.info("Access token not in cache, requesting new token from MVola")

        try:
            # Generate Basic Auth header
            basic_auth = self._generate_basic_auth_header()

            # Prepare token request
            token_url = f"{self.base_url}{TOKEN_ENDPOINT}"
            headers = {
                HEADER_AUTHORIZATION: basic_auth,
                HEADER_CONTENT_TYPE: "application/x-www-form-urlencoded",
                HEADER_CACHE_CONTROL: CACHE_CONTROL_NO_CACHE,
            }

            payload = {
                "grant_type": OAUTH_GRANT_TYPE,
                "scope": OAUTH_SCOPE,
            }

            # Log token request attempt (with environment info)
            env_type = "PRODUCTION" if "api.mvola.mg" in token_url else "SANDBOX"
            logger.info(
                f"Requesting OAuth2 token from {token_url} "
                f"(environment={env_type}, grant_type={OAUTH_GRANT_TYPE}, scope={OAUTH_SCOPE})"
            )

            # Make token request
            response = requests.post(token_url, headers=headers, data=payload, timeout=TIMEOUT_TOKEN_REQUEST)

            # Log response status
            logger.info(f"Token request response: status_code={response.status_code}")

            # Check for authentication errors
            if response.status_code == HTTP_UNAUTHORIZED:
                # Try to extract error details from response
                api_error_detail = None
                try:
                    error_response = response.json()
                    api_error_detail = (
                        error_response.get("error_description")
                        or error_response.get("error")
                        or error_response.get("message")
                    )
                except (ValueError, AttributeError):
                    # If response is not JSON, try to get text
                    api_error_detail = response.text.strip() if response.text else None

                # Determine environment for better error message
                is_sandbox = "devapi" in self.base_url or "sandbox" in self.base_url.lower()
                is_production = "api.mvola.mg" in self.base_url and not is_sandbox

                # Check if credentials are present (but don't log them)
                has_credentials = bool(self.consumer_key and self.consumer_secret)

                # Build detailed error message
                if not has_credentials:
                    error_msg = (
                        f"{ERROR_AUTH_FAILED} " f"Les identifiants (Consumer Key/Secret) sont manquants ou vides."
                    )
                else:
                    env_info = ""
                    if is_sandbox:
                        env_info = " (Mode SANDBOX - utilisez les identifiants de test)"
                    elif is_production:
                        env_info = " (Mode PRODUCTION - utilisez les identifiants de production)"

                    base_msg = (
                        f"{ERROR_AUTH_FAILED} "
                        f"Identifiants MVola invalides ou expirés{env_info}. "
                        f"Vérifiez que: (1) Consumer Key et Consumer Secret sont corrects, "
                        f"(2) Les identifiants correspondent à l'environnement configuré, "
                        f"(3) Les identifiants n'ont pas expiré."
                    )

                    # Append API error detail if available
                    if api_error_detail:
                        error_msg = f"{base_msg} Détail API: {api_error_detail}"
                    else:
                        error_msg = base_msg

                logger.error(
                    f"Token generation failed: {error_msg} "
                    f"(base_url={self.base_url}, "
                    f"consumer_key_present={bool(self.consumer_key)}, "
                    f"consumer_secret_present={bool(self.consumer_secret)}, "
                    f"api_error_detail={api_error_detail})"
                )
                raise MvolaAuthenticationError(error_msg)

            # Check for other errors
            if response.status_code not in [HTTP_OK, HTTP_CREATED]:
                error_msg = f"{ERROR_AUTH_FAILED} " f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Token generation failed: {error_msg}")
                raise MvolaAuthenticationError(error_msg)

            # Parse response
            try:
                response_data = response.json()
            except ValueError as e:
                error_msg = f"{ERROR_AUTH_FAILED} Invalid JSON response from token endpoint"
                logger.error(f"Token response parsing failed: {error_msg}, error={str(e)}")
                raise MvolaAuthenticationError(error_msg)

            # Extract access token
            access_token = response_data.get("access_token")

            if not access_token:
                error_msg = f"{ERROR_AUTH_FAILED} No access_token in response"
                logger.error(f"Token extraction failed: {error_msg}")
                raise MvolaAuthenticationError(error_msg)

            # Cache the token for 55 minutes
            cache.set(cache_key, access_token, TOKEN_CACHE_TTL)

            logger.info(f"Access token generated successfully and cached " f"(key={cache_key}, ttl={TOKEN_CACHE_TTL}s)")

            return access_token

        except requests.exceptions.Timeout:
            error_msg = f"{ERROR_AUTH_FAILED} Token request timeout"
            logger.error(f"Token generation failed: {error_msg}")
            raise MvolaAuthenticationError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"{ERROR_AUTH_FAILED} Network error: {str(e)}"
            logger.error(f"Token generation failed: {error_msg}")
            raise MvolaAuthenticationError(error_msg)

        except MvolaAuthenticationError:
            # Re-raise MVola authentication errors
            raise

        except Exception as e:
            error_msg = f"{ERROR_AUTH_FAILED} Unexpected error: {str(e)}"
            logger.error(f"Token generation failed: {error_msg}")
            raise MvolaAuthenticationError(error_msg)

    def initiate_payment(
        self, amount: Decimal, customer_msisdn: str, description: str, vehicle_plate: str, tax_year: int
    ) -> Dict[str, Any]:
        """
        Initiate a MVola merchant pay transaction.

        This method initiates a payment request to MVola which sends a push
        notification to the customer's mobile wallet for confirmation.

        Args:
            amount: Total amount including 3% fee (in Ariary)
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
        # Generate unique X-CorrelationID using UUID4
        x_correlation_id = str(uuid.uuid4())

        # Log payment initiation attempt
        logger.info(
            f"Initiating MVola payment: "
            f"x_correlation_id={x_correlation_id}, "
            f"amount={amount}, "
            f"customer_msisdn={customer_msisdn[-4:].rjust(len(customer_msisdn), '*')}, "
            f"vehicle_plate={vehicle_plate}, "
            f"tax_year={tax_year}"
        )

        try:
            # Get access token
            access_token = self.get_access_token()

            # Prepare payment endpoint URL
            payment_url = f"{self.base_url}{MERCHANT_PAY_ENDPOINT}"

            # Generate request date in ISO 8601 format
            request_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

            # Construct payment payload with all required fields
            payload = {
                "amount": str(amount),
                "currency": CURRENCY_CODE,
                "descriptionText": description[:MAX_DESCRIPTION_LENGTH],
                "requestDate": request_date,
                "debitParty": [{"key": "msisdn", "value": customer_msisdn}],
                "creditParty": [{"key": "msisdn", "value": self.partner_msisdn}],
                "metadata": [
                    {"key": "partnerName", "value": self.partner_name[:MAX_DESCRIPTION_LENGTH]},
                    {"key": "vehicle_plate", "value": vehicle_plate},
                    {"key": "tax_year", "value": str(tax_year)},
                    {"key": "XCorrelationId", "value": x_correlation_id},
                ],
                "requestingOrganisationTransactionReference": x_correlation_id,
                "originalTransactionReference": "",
            }

            # Set all required headers
            headers = {
                HEADER_AUTHORIZATION: f"Bearer {access_token}",
                HEADER_VERSION: API_VERSION,
                HEADER_X_CORRELATION_ID: x_correlation_id,
                HEADER_USER_LANGUAGE: USER_LANGUAGE_FR,
                HEADER_USER_ACCOUNT_IDENTIFIER: f"msisdn;{self.partner_msisdn}",
                HEADER_PARTNER_NAME: self.partner_name,
                HEADER_X_CALLBACK_URL: self.callback_url,
                HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
                HEADER_CACHE_CONTROL: CACHE_CONTROL_NO_CACHE,
            }

            # Log request details (without sensitive data)
            logger.info(
                f"POST {payment_url} "
                f"(X-CorrelationID={x_correlation_id}, "
                f"amount={amount}, "
                f"currency={CURRENCY_CODE})"
            )

            # Make POST request to MVola merchant pay endpoint
            response = requests.post(payment_url, headers=headers, json=payload, timeout=TIMEOUT_PAYMENT_REQUEST)

            # Log response status
            logger.info(
                f"Payment initiation response: "
                f"status_code={response.status_code}, "
                f"x_correlation_id={x_correlation_id}"
            )

            # Parse response
            try:
                response_data = response.json()
            except ValueError as e:
                error_msg = f"Invalid JSON response from payment endpoint: {response.text}"
                logger.error(f"Payment initiation failed: {error_msg}, " f"x_correlation_id={x_correlation_id}")
                return {"success": False, "x_correlation_id": x_correlation_id, "error": ERROR_INVALID_RESPONSE}

            # Check for successful response
            if response.status_code in [HTTP_OK, HTTP_CREATED]:
                # Extract serverCorrelationId from response
                server_correlation_id = response_data.get("serverCorrelationId")
                status = response_data.get("status", STATUS_PENDING)

                if not server_correlation_id:
                    error_msg = "No serverCorrelationId in response"
                    logger.error(
                        f"Payment initiation failed: {error_msg}, "
                        f"x_correlation_id={x_correlation_id}, "
                        f"response={response_data}"
                    )
                    return {"success": False, "x_correlation_id": x_correlation_id, "error": ERROR_INVALID_RESPONSE}

                # Log successful payment initiation
                logger.info(
                    f"Payment initiated successfully: "
                    f"x_correlation_id={x_correlation_id}, "
                    f"server_correlation_id={server_correlation_id}, "
                    f"status={status}"
                )

                # Return structured success response
                return {
                    "success": True,
                    "x_correlation_id": x_correlation_id,
                    "server_correlation_id": server_correlation_id,
                    "status": status,
                    "response_data": response_data,
                }

            # Handle API errors
            else:
                error_message = response_data.get("message", response.text)
                error_code = response_data.get("code", response.status_code)

                logger.error(
                    f"Payment initiation failed: "
                    f"status_code={response.status_code}, "
                    f"error_code={error_code}, "
                    f"error_message={error_message}, "
                    f"x_correlation_id={x_correlation_id}"
                )

                # Return structured error response
                return {
                    "success": False,
                    "x_correlation_id": x_correlation_id,
                    "error": ERROR_PAYMENT_FAILED,
                    "error_code": error_code,
                    "error_message": error_message,
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout:
            error_msg = ERROR_NETWORK_TIMEOUT
            logger.error(f"Payment initiation timeout: " f"x_correlation_id={x_correlation_id}")
            return {"success": False, "x_correlation_id": x_correlation_id, "error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"Payment initiation network error: " f"{error_msg}, " f"x_correlation_id={x_correlation_id}")
            return {"success": False, "x_correlation_id": x_correlation_id, "error": ERROR_PAYMENT_FAILED}

        except MvolaAuthenticationError as e:
            # Token generation failed
            logger.error(f"Payment initiation auth error: " f"{str(e)}, " f"x_correlation_id={x_correlation_id}")
            return {"success": False, "x_correlation_id": x_correlation_id, "error": str(e)}

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(
                f"Payment initiation unexpected error: " f"{error_msg}, " f"x_correlation_id={x_correlation_id}"
            )
            return {"success": False, "x_correlation_id": x_correlation_id, "error": ERROR_PAYMENT_FAILED}

    def get_transaction_status(self, server_correlation_id: str) -> Dict[str, Any]:
        """
        Check transaction status using server correlation ID.

        This method queries MVola's status endpoint to get the current status
        of a transaction. It's useful for polling transaction status or manually
        checking status when callback is not received.

        Args:
            server_correlation_id: MVola's transaction identifier returned from initiate_payment

        Returns:
            dict: {
                'success': bool,
                'status': str (pending, completed, failed),
                'transaction_reference': str (if available),
                'response_data': dict (full response from MVola),
                'error': str (if failed)
            }

        Raises:
            MvolaAPIError: If API request fails critically
        """
        # Log status check attempt
        logger.info(f"Checking transaction status: " f"server_correlation_id={server_correlation_id}")

        try:
            # Get access token
            access_token = self.get_access_token()

            # Prepare status endpoint URL with server correlation ID
            status_url = (
                f"{self.base_url}{TRANSACTION_STATUS_ENDPOINT.format(serverCorrelationId=server_correlation_id)}"
            )

            # Generate unique X-CorrelationID for this status check request
            x_correlation_id = str(uuid.uuid4())

            # Set required headers for status check request
            headers = {
                HEADER_AUTHORIZATION: f"Bearer {access_token}",
                HEADER_VERSION: API_VERSION,
                HEADER_X_CORRELATION_ID: x_correlation_id,
                HEADER_USER_LANGUAGE: USER_LANGUAGE_FR,
                HEADER_USER_ACCOUNT_IDENTIFIER: f"msisdn;{self.partner_msisdn}",
                HEADER_PARTNER_NAME: self.partner_name,
                HEADER_CACHE_CONTROL: CACHE_CONTROL_NO_CACHE,
            }

            # Log request details
            logger.info(
                f"GET {status_url} "
                f"(X-CorrelationID={x_correlation_id}, "
                f"server_correlation_id={server_correlation_id})"
            )

            # Make GET request to transaction status endpoint
            response = requests.get(status_url, headers=headers, timeout=TIMEOUT_STATUS_REQUEST)

            # Log response status
            logger.info(
                f"Status check response: "
                f"status_code={response.status_code}, "
                f"server_correlation_id={server_correlation_id}, "
                f"x_correlation_id={x_correlation_id}"
            )

            # Parse response
            try:
                response_data = response.json()
            except ValueError as e:
                error_msg = f"Invalid JSON response from status endpoint: {response.text}"
                logger.error(
                    f"Status check failed: {error_msg}, "
                    f"server_correlation_id={server_correlation_id}, "
                    f"x_correlation_id={x_correlation_id}"
                )
                return {
                    "success": False,
                    "server_correlation_id": server_correlation_id,
                    "error": ERROR_INVALID_RESPONSE,
                }

            # Check for successful response
            if response.status_code == HTTP_OK:
                # Extract status information from response
                transaction_status = response_data.get("status", STATUS_PENDING)
                transaction_reference = response_data.get("transactionReference")

                # Log successful status check
                logger.info(
                    f"Status check successful: "
                    f"server_correlation_id={server_correlation_id}, "
                    f"status={transaction_status}, "
                    f"transaction_reference={transaction_reference}"
                )

                # Return structured success response
                return {
                    "success": True,
                    "server_correlation_id": server_correlation_id,
                    "status": transaction_status,
                    "transaction_reference": transaction_reference,
                    "response_data": response_data,
                }

            # Handle 404 - transaction not found
            elif response.status_code == HTTP_NOT_FOUND:
                error_msg = ERROR_TRANSACTION_NOT_FOUND
                logger.warning(
                    f"Transaction not found: "
                    f"server_correlation_id={server_correlation_id}, "
                    f"x_correlation_id={x_correlation_id}"
                )
                return {
                    "success": False,
                    "server_correlation_id": server_correlation_id,
                    "error": error_msg,
                    "status_code": response.status_code,
                }

            # Handle other API errors
            else:
                error_message = response_data.get("message", response.text)
                error_code = response_data.get("code", response.status_code)

                logger.error(
                    f"Status check failed: "
                    f"status_code={response.status_code}, "
                    f"error_code={error_code}, "
                    f"error_message={error_message}, "
                    f"server_correlation_id={server_correlation_id}, "
                    f"x_correlation_id={x_correlation_id}"
                )

                # Return structured error response
                return {
                    "success": False,
                    "server_correlation_id": server_correlation_id,
                    "error": error_message,
                    "error_code": error_code,
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout:
            error_msg = ERROR_NETWORK_TIMEOUT
            logger.error(f"Status check timeout: " f"server_correlation_id={server_correlation_id}")
            return {"success": False, "server_correlation_id": server_correlation_id, "error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(
                f"Status check network error: " f"{error_msg}, " f"server_correlation_id={server_correlation_id}"
            )
            return {"success": False, "server_correlation_id": server_correlation_id, "error": ERROR_INVALID_RESPONSE}

        except MvolaAuthenticationError as e:
            # Token generation failed
            logger.error(f"Status check auth error: " f"{str(e)}, " f"server_correlation_id={server_correlation_id}")
            return {"success": False, "server_correlation_id": server_correlation_id, "error": str(e)}

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(
                f"Status check unexpected error: " f"{error_msg}, " f"server_correlation_id={server_correlation_id}"
            )
            return {"success": False, "server_correlation_id": server_correlation_id, "error": ERROR_INVALID_RESPONSE}

    def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get detailed transaction information using transaction ID.

        This method retrieves comprehensive transaction details including
        fees, timestamps, and full transaction history. It's useful for
        reconciliation and detailed reporting.

        Args:
            transaction_id: Transaction identifier (can be transactionReference or serverCorrelationId)

        Returns:
            dict: {
                'success': bool,
                'transaction_id': str,
                'details': dict (full transaction details including fees),
                'error': str (if failed)
            }

        Raises:
            MvolaAPIError: If API request fails critically
        """
        # Log details retrieval attempt
        logger.info(f"Retrieving transaction details: " f"transaction_id={transaction_id}")

        try:
            # Get access token
            access_token = self.get_access_token()

            # Prepare details endpoint URL with transaction ID
            details_url = f"{self.base_url}{TRANSACTION_DETAILS_ENDPOINT.format(transactionId=transaction_id)}"

            # Generate unique X-CorrelationID for this details request
            x_correlation_id = str(uuid.uuid4())

            # Set required headers for details request
            headers = {
                HEADER_AUTHORIZATION: f"Bearer {access_token}",
                HEADER_VERSION: API_VERSION,
                HEADER_X_CORRELATION_ID: x_correlation_id,
                HEADER_USER_LANGUAGE: USER_LANGUAGE_FR,
                HEADER_USER_ACCOUNT_IDENTIFIER: f"msisdn;{self.partner_msisdn}",
                HEADER_PARTNER_NAME: self.partner_name,
                HEADER_CACHE_CONTROL: CACHE_CONTROL_NO_CACHE,
            }

            # Log request details
            logger.info(
                f"GET {details_url} " f"(X-CorrelationID={x_correlation_id}, " f"transaction_id={transaction_id})"
            )

            # Make GET request to transaction details endpoint
            response = requests.get(details_url, headers=headers, timeout=TIMEOUT_DETAILS_REQUEST)

            # Log response status
            logger.info(
                f"Details retrieval response: "
                f"status_code={response.status_code}, "
                f"transaction_id={transaction_id}, "
                f"x_correlation_id={x_correlation_id}"
            )

            # Parse response
            try:
                response_data = response.json()
            except ValueError as e:
                error_msg = f"Invalid JSON response from details endpoint: {response.text}"
                logger.error(
                    f"Details retrieval failed: {error_msg}, "
                    f"transaction_id={transaction_id}, "
                    f"x_correlation_id={x_correlation_id}"
                )
                return {"success": False, "transaction_id": transaction_id, "error": ERROR_INVALID_RESPONSE}

            # Check for successful response
            if response.status_code == HTTP_OK:
                # Log successful details retrieval
                logger.info(
                    f"Details retrieval successful: "
                    f"transaction_id={transaction_id}, "
                    f"x_correlation_id={x_correlation_id}"
                )

                # Return structured success response with full details
                return {"success": True, "transaction_id": transaction_id, "details": response_data}

            # Handle 404 - transaction not found
            elif response.status_code == HTTP_NOT_FOUND:
                error_msg = ERROR_TRANSACTION_NOT_FOUND
                logger.warning(
                    f"Transaction not found: "
                    f"transaction_id={transaction_id}, "
                    f"x_correlation_id={x_correlation_id}"
                )
                return {
                    "success": False,
                    "transaction_id": transaction_id,
                    "error": error_msg,
                    "status_code": response.status_code,
                }

            # Handle other API errors
            else:
                error_message = response_data.get("message", response.text)
                error_code = response_data.get("code", response.status_code)

                logger.error(
                    f"Details retrieval failed: "
                    f"status_code={response.status_code}, "
                    f"error_code={error_code}, "
                    f"error_message={error_message}, "
                    f"transaction_id={transaction_id}, "
                    f"x_correlation_id={x_correlation_id}"
                )

                # Return structured error response
                return {
                    "success": False,
                    "transaction_id": transaction_id,
                    "error": error_message,
                    "error_code": error_code,
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout:
            error_msg = ERROR_NETWORK_TIMEOUT
            logger.error(f"Details retrieval timeout: " f"transaction_id={transaction_id}")
            return {"success": False, "transaction_id": transaction_id, "error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"Details retrieval network error: " f"{error_msg}, " f"transaction_id={transaction_id}")
            return {"success": False, "transaction_id": transaction_id, "error": ERROR_INVALID_RESPONSE}

        except MvolaAuthenticationError as e:
            # Token generation failed
            logger.error(f"Details retrieval auth error: " f"{str(e)}, " f"transaction_id={transaction_id}")
            return {"success": False, "transaction_id": transaction_id, "error": str(e)}

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Details retrieval unexpected error: " f"{error_msg}, " f"transaction_id={transaction_id}")
            return {"success": False, "transaction_id": transaction_id, "error": ERROR_INVALID_RESPONSE}
