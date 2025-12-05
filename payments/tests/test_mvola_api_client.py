"""
Unit tests for MvolaAPIClient OAuth2 token management.

Tests cover:
- Token generation with valid credentials
- Token caching mechanism
- Token refresh on cache miss
- Error handling for authentication failures
- Configuration validation
"""

import base64
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings

from payments.services.mvola import MvolaAPIClient, MvolaAuthenticationError
from payments.services.mvola.constants import (
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    TOKEN_CACHE_KEY_PREFIX,
    TOKEN_CACHE_TTL,
)


@override_settings(
    MVOLA_BASE_URL="https://devapi.mvola.mg",
    MVOLA_CONSUMER_KEY="test_consumer_key",
    MVOLA_CONSUMER_SECRET="test_consumer_secret",
    MVOLA_PARTNER_MSISDN="0340000000",
    MVOLA_PARTNER_NAME="TestPartner",
    MVOLA_CALLBACK_URL="http://localhost:8000/api/payments/mvola/callback/",
)
class MvolaAPIClientTokenTests(TestCase):
    """Test OAuth2 token management in MvolaAPIClient"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear cache before each test
        cache.clear()

        # Initialize client
        self.client = MvolaAPIClient()

    def tearDown(self):
        """Clean up after each test"""
        cache.clear()

    def test_initialization_with_valid_config(self):
        """Test client initializes correctly with valid configuration"""
        self.assertEqual(self.client.base_url, "https://devapi.mvola.mg")
        self.assertEqual(self.client.consumer_key, "test_consumer_key")
        self.assertEqual(self.client.consumer_secret, "test_consumer_secret")
        self.assertEqual(self.client.partner_msisdn, "0340000000")
        self.assertEqual(self.client.partner_name, "TestPartner")
        self.assertEqual(self.client.callback_url, "http://localhost:8000/api/payments/mvola/callback/")

    @override_settings(MVOLA_CONSUMER_KEY=None)
    def test_initialization_fails_with_missing_consumer_key(self):
        """Test initialization fails when consumer key is missing"""
        with self.assertRaises(MvolaAuthenticationError) as context:
            MvolaAPIClient()

        self.assertIn("MVOLA_CONSUMER_KEY", str(context.exception))

    @override_settings(MVOLA_CONSUMER_SECRET=None)
    def test_initialization_fails_with_missing_consumer_secret(self):
        """Test initialization fails when consumer secret is missing"""
        with self.assertRaises(MvolaAuthenticationError) as context:
            MvolaAPIClient()

        self.assertIn("MVOLA_CONSUMER_SECRET", str(context.exception))

    def test_generate_basic_auth_header(self):
        """Test Basic Auth header generation"""
        auth_header = self.client._generate_basic_auth_header()

        # Verify format
        self.assertTrue(auth_header.startswith("Basic "))

        # Decode and verify credentials
        base64_part = auth_header.replace("Basic ", "")
        decoded = base64.b64decode(base64_part).decode("utf-8")

        self.assertEqual(decoded, "test_consumer_key:test_consumer_secret")

    def test_get_token_cache_key(self):
        """Test cache key generation"""
        cache_key = self.client._get_token_cache_key()

        expected_key = f"{TOKEN_CACHE_KEY_PREFIX}_test_consumer_key"
        self.assertEqual(cache_key, expected_key)

    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_access_token_success(self, mock_post):
        """Test successful token generation"""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = HTTP_OK
        mock_response.json.return_value = {
            "access_token": "test_access_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        # Get token
        token = self.client.get_access_token()

        # Verify token
        self.assertEqual(token, "test_access_token_12345")

        # Verify API call was made
        self.assertTrue(mock_post.called)

        # Verify token was cached
        cache_key = self.client._get_token_cache_key()
        cached_token = cache.get(cache_key)
        self.assertEqual(cached_token, "test_access_token_12345")

    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_access_token_from_cache(self, mock_post):
        """Test token retrieval from cache (no API call)"""
        # Pre-populate cache
        cache_key = self.client._get_token_cache_key()
        cache.set(cache_key, "cached_token_12345", TOKEN_CACHE_TTL)

        # Get token
        token = self.client.get_access_token()

        # Verify cached token was returned
        self.assertEqual(token, "cached_token_12345")

        # Verify no API call was made
        self.assertFalse(mock_post.called)

    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_access_token_cache_miss_then_hit(self, mock_post):
        """Test token caching: first call generates, second call uses cache"""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = HTTP_OK
        mock_response.json.return_value = {
            "access_token": "new_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        # First call - should generate token
        token1 = self.client.get_access_token()
        self.assertEqual(token1, "new_token_12345")
        self.assertEqual(mock_post.call_count, 1)

        # Second call - should use cache
        token2 = self.client.get_access_token()
        self.assertEqual(token2, "new_token_12345")
        self.assertEqual(mock_post.call_count, 1)  # No additional call

    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_access_token_unauthorized(self, mock_post):
        """Test token generation fails with invalid credentials"""
        # Mock unauthorized response
        mock_response = Mock()
        mock_response.status_code = HTTP_UNAUTHORIZED
        mock_response.text = "Invalid credentials"
        mock_post.return_value = mock_response

        # Attempt to get token
        with self.assertRaises(MvolaAuthenticationError) as context:
            self.client.get_access_token()

        self.assertIn("Invalid consumer credentials", str(context.exception))

    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_access_token_invalid_json_response(self, mock_post):
        """Test token generation fails with invalid JSON response"""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = HTTP_OK
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        # Attempt to get token
        with self.assertRaises(MvolaAuthenticationError) as context:
            self.client.get_access_token()

        self.assertIn("Invalid JSON response", str(context.exception))

    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_access_token_missing_access_token_in_response(self, mock_post):
        """Test token generation fails when access_token is missing"""
        # Mock response without access_token
        mock_response = Mock()
        mock_response.status_code = HTTP_OK
        mock_response.json.return_value = {"token_type": "Bearer", "expires_in": 3600}
        mock_post.return_value = mock_response

        # Attempt to get token
        with self.assertRaises(MvolaAuthenticationError) as context:
            self.client.get_access_token()

        self.assertIn("No access_token in response", str(context.exception))

    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_access_token_timeout(self, mock_post):
        """Test token generation handles timeout"""
        # Mock timeout
        mock_post.side_effect = Exception("Timeout")

        # Attempt to get token
        with self.assertRaises(MvolaAuthenticationError) as context:
            self.client.get_access_token()

        self.assertIn("Unexpected error", str(context.exception))

    @patch("payments.services.mvola.api_client.requests.post")
    def test_token_caching_ttl(self, mock_post):
        """Test token is cached with correct TTL"""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = HTTP_OK
        mock_response.json.return_value = {"access_token": "test_token", "token_type": "Bearer", "expires_in": 3600}
        mock_post.return_value = mock_response

        # Get token
        self.client.get_access_token()

        # Verify token is in cache
        cache_key = self.client._get_token_cache_key()
        cached_token = cache.get(cache_key)
        self.assertIsNotNone(cached_token)

        # Note: We can't easily test the exact TTL without mocking time,
        # but we verify the token is cached


@override_settings(
    MVOLA_BASE_URL="https://devapi.mvola.mg",
    MVOLA_CONSUMER_KEY="test_consumer_key",
    MVOLA_CONSUMER_SECRET="test_consumer_secret",
    MVOLA_PARTNER_MSISDN="0340000000",
    MVOLA_PARTNER_NAME="TestPartner",
    MVOLA_CALLBACK_URL="http://localhost:8000/api/payments/mvola/callback/",
)
class MvolaAPIClientPaymentInitiationTests(TestCase):
    """Test payment initiation in MvolaAPIClient"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear cache before each test
        cache.clear()

        # Initialize client
        self.client = MvolaAPIClient()

        # Test payment data
        self.amount = Decimal("103000.00")
        self.customer_msisdn = "0340000001"
        self.description = "Taxe véhicule 2024"
        self.vehicle_plate = "1234AB01"
        self.tax_year = 2024

    def tearDown(self):
        """Clean up after each test"""
        cache.clear()

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_success(self, mock_post):
        """Test successful payment initiation"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token", "token_type": "Bearer", "expires_in": 3600}

        # Mock payment response
        payment_response = Mock()
        payment_response.status_code = HTTP_OK
        payment_response.json.return_value = {
            "serverCorrelationId": "server_corr_id_12345",
            "status": "pending",
            "notificationMethod": "push",
        }

        # Configure mock to return different responses for token and payment
        mock_post.side_effect = [token_response, payment_response]

        # Initiate payment
        result = self.client.initiate_payment(
            amount=self.amount,
            customer_msisdn=self.customer_msisdn,
            description=self.description,
            vehicle_plate=self.vehicle_plate,
            tax_year=self.tax_year,
        )

        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["server_correlation_id"], "server_corr_id_12345")
        self.assertEqual(result["status"], "pending")
        self.assertIn("x_correlation_id", result)

        # Verify payment API was called
        self.assertEqual(mock_post.call_count, 2)  # Token + Payment

        # Verify payment request details
        payment_call = mock_post.call_args_list[1]
        payment_url = payment_call[0][0]
        payment_headers = payment_call[1]["headers"]
        payment_payload = payment_call[1]["json"]

        # Verify URL
        self.assertIn("/mvola/mm/transactions/type/merchantpay/1.0.0/", payment_url)

        # Verify headers
        self.assertIn("Authorization", payment_headers)
        self.assertIn("Bearer test_token", payment_headers["Authorization"])
        self.assertIn("X-CorrelationID", payment_headers)
        self.assertEqual(payment_headers["Version"], "1.0")
        self.assertEqual(payment_headers["UserLanguage"], "FR")
        self.assertEqual(payment_headers["partnerName"], "TestPartner")
        self.assertEqual(payment_headers["X-Callback-URL"], "http://localhost:8000/api/payments/mvola/callback/")

        # Verify payload
        self.assertEqual(payment_payload["amount"], "103000.00")
        self.assertEqual(payment_payload["currency"], "Ar")
        self.assertEqual(payment_payload["descriptionText"], "Taxe véhicule 2024")
        self.assertEqual(payment_payload["debitParty"][0]["value"], "0340000001")
        self.assertEqual(payment_payload["creditParty"][0]["value"], "0340000000")

        # Verify metadata
        metadata = {item["key"]: item["value"] for item in payment_payload["metadata"]}
        self.assertEqual(metadata["vehicle_plate"], "1234AB01")
        self.assertEqual(metadata["tax_year"], "2024")

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_generates_unique_correlation_id(self, mock_post):
        """Test that each payment generates a unique X-CorrelationID"""
        # Mock responses
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}

        payment_response = Mock()
        payment_response.status_code = HTTP_OK
        payment_response.json.return_value = {"serverCorrelationId": "server_id", "status": "pending"}

        mock_post.side_effect = [token_response, payment_response, payment_response]  # Reuse for second call

        # Initiate two payments
        result1 = self.client.initiate_payment(
            self.amount, self.customer_msisdn, self.description, self.vehicle_plate, self.tax_year
        )
        result2 = self.client.initiate_payment(
            self.amount, self.customer_msisdn, self.description, self.vehicle_plate, self.tax_year
        )

        # Verify different correlation IDs
        self.assertNotEqual(result1["x_correlation_id"], result2["x_correlation_id"])

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_api_error(self, mock_post):
        """Test payment initiation handles API errors"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}

        # Mock payment error response
        payment_response = Mock()
        payment_response.status_code = 400
        payment_response.json.return_value = {"code": "INSUFFICIENT_BALANCE", "message": "Solde insuffisant"}
        payment_response.text = "Bad Request"

        mock_post.side_effect = [token_response, payment_response]

        # Initiate payment
        result = self.client.initiate_payment(
            self.amount, self.customer_msisdn, self.description, self.vehicle_plate, self.tax_year
        )

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("x_correlation_id", result)
        self.assertEqual(result["error_code"], "INSUFFICIENT_BALANCE")

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_missing_server_correlation_id(self, mock_post):
        """Test payment initiation handles missing serverCorrelationId"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}

        # Mock payment response without serverCorrelationId
        payment_response = Mock()
        payment_response.status_code = HTTP_OK
        payment_response.json.return_value = {
            "status": "pending"
            # Missing serverCorrelationId
        }

        mock_post.side_effect = [token_response, payment_response]

        # Initiate payment
        result = self.client.initiate_payment(
            self.amount, self.customer_msisdn, self.description, self.vehicle_plate, self.tax_year
        )

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Réponse invalide de MVola", result["error"])

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_invalid_json_response(self, mock_post):
        """Test payment initiation handles invalid JSON response"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}

        # Mock payment response with invalid JSON
        payment_response = Mock()
        payment_response.status_code = HTTP_OK
        payment_response.json.side_effect = ValueError("Invalid JSON")
        payment_response.text = "Invalid response"

        mock_post.side_effect = [token_response, payment_response]

        # Initiate payment
        result = self.client.initiate_payment(
            self.amount, self.customer_msisdn, self.description, self.vehicle_plate, self.tax_year
        )

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Réponse invalide de MVola", result["error"])

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_timeout(self, mock_post):
        """Test payment initiation handles timeout"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}

        # Mock timeout on payment request
        import requests

        mock_post.side_effect = [token_response, requests.exceptions.Timeout()]

        # Initiate payment
        result = self.client.initiate_payment(
            self.amount, self.customer_msisdn, self.description, self.vehicle_plate, self.tax_year
        )

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Délai d'attente dépassé", result["error"])

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_network_error(self, mock_post):
        """Test payment initiation handles network errors"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}

        # Mock network error on payment request
        import requests

        mock_post.side_effect = [token_response, requests.exceptions.RequestException("Network error")]

        # Initiate payment
        result = self.client.initiate_payment(
            self.amount, self.customer_msisdn, self.description, self.vehicle_plate, self.tax_year
        )

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_truncates_long_description(self, mock_post):
        """Test payment initiation truncates description to 50 chars"""
        # Mock responses
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}

        payment_response = Mock()
        payment_response.status_code = HTTP_OK
        payment_response.json.return_value = {"serverCorrelationId": "server_id", "status": "pending"}

        mock_post.side_effect = [token_response, payment_response]

        # Long description (more than 50 chars)
        long_description = "A" * 100

        # Initiate payment
        self.client.initiate_payment(
            self.amount, self.customer_msisdn, long_description, self.vehicle_plate, self.tax_year
        )

        # Verify description was truncated
        payment_call = mock_post.call_args_list[1]
        payment_payload = payment_call[1]["json"]
        self.assertEqual(len(payment_payload["descriptionText"]), 50)

    @patch("payments.services.mvola.api_client.requests.post")
    def test_initiate_payment_masks_msisdn_in_logs(self, mock_post):
        """Test that MSISDN is masked in log messages"""
        # Mock responses
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}

        payment_response = Mock()
        payment_response.status_code = HTTP_OK
        payment_response.json.return_value = {"serverCorrelationId": "server_id", "status": "pending"}

        mock_post.side_effect = [token_response, payment_response]

        # Initiate payment with logging
        with self.assertLogs("payments.mvola", level="INFO") as log_context:
            self.client.initiate_payment(
                self.amount, self.customer_msisdn, self.description, self.vehicle_plate, self.tax_year
            )

            # Verify MSISDN is masked in logs
            log_output = " ".join(log_context.output)
            self.assertNotIn("0340000001", log_output)
            self.assertIn("0001", log_output)  # Last 4 digits visible


@override_settings(
    MVOLA_BASE_URL="https://devapi.mvola.mg",
    MVOLA_CONSUMER_KEY="test_consumer_key",
    MVOLA_CONSUMER_SECRET="test_consumer_secret",
    MVOLA_PARTNER_MSISDN="0340000000",
    MVOLA_PARTNER_NAME="TestPartner",
    MVOLA_CALLBACK_URL="http://localhost:8000/api/payments/mvola/callback/",
)
class MvolaAPIClientStatusCheckTests(TestCase):
    """Test transaction status checking in MvolaAPIClient"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear cache before each test
        cache.clear()

        # Initialize client
        self.client = MvolaAPIClient()

        # Test server correlation ID
        self.server_correlation_id = "server_corr_id_12345"

    def tearDown(self):
        """Clean up after each test"""
        cache.clear()

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_status_success(self, mock_post, mock_get):
        """Test successful transaction status check"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token", "token_type": "Bearer", "expires_in": 3600}
        mock_post.return_value = token_response

        # Mock status response
        status_response = Mock()
        status_response.status_code = HTTP_OK
        status_response.json.return_value = {
            "status": "completed",
            "transactionReference": "TXN_REF_12345",
            "serverCorrelationId": self.server_correlation_id,
        }
        mock_get.return_value = status_response

        # Get transaction status
        result = self.client.get_transaction_status(self.server_correlation_id)

        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["transaction_reference"], "TXN_REF_12345")
        self.assertEqual(result["server_correlation_id"], self.server_correlation_id)

        # Verify GET request was made
        self.assertTrue(mock_get.called)

        # Verify request details
        status_call = mock_get.call_args
        status_url = status_call[0][0]
        status_headers = status_call[1]["headers"]

        # Verify URL contains server correlation ID
        self.assertIn(self.server_correlation_id, status_url)
        self.assertIn("/mvola/mm/transactions/type/merchantpay/1.0.0/status/", status_url)

        # Verify headers
        self.assertIn("Authorization", status_headers)
        self.assertIn("Bearer test_token", status_headers["Authorization"])
        self.assertIn("X-CorrelationID", status_headers)
        self.assertEqual(status_headers["Version"], "1.0")
        self.assertEqual(status_headers["UserLanguage"], "FR")

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_status_pending(self, mock_post, mock_get):
        """Test status check for pending transaction"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock pending status response
        status_response = Mock()
        status_response.status_code = HTTP_OK
        status_response.json.return_value = {"status": "pending", "serverCorrelationId": self.server_correlation_id}
        mock_get.return_value = status_response

        # Get transaction status
        result = self.client.get_transaction_status(self.server_correlation_id)

        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "pending")
        self.assertIsNone(result["transaction_reference"])

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_status_not_found(self, mock_post, mock_get):
        """Test status check for non-existent transaction"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock 404 response
        status_response = Mock()
        status_response.status_code = 404
        status_response.json.return_value = {"code": "NOT_FOUND", "message": "Transaction not found"}
        mock_get.return_value = status_response

        # Get transaction status
        result = self.client.get_transaction_status(self.server_correlation_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Transaction introuvable", result["error"])
        self.assertEqual(result["status_code"], 404)

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_status_api_error(self, mock_post, mock_get):
        """Test status check handles API errors"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock error response
        status_response = Mock()
        status_response.status_code = 500
        status_response.json.return_value = {"code": "INTERNAL_ERROR", "message": "Internal server error"}
        status_response.text = "Internal Server Error"
        mock_get.return_value = status_response

        # Get transaction status
        result = self.client.get_transaction_status(self.server_correlation_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["error_code"], "INTERNAL_ERROR")

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_status_invalid_json(self, mock_post, mock_get):
        """Test status check handles invalid JSON response"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock invalid JSON response
        status_response = Mock()
        status_response.status_code = HTTP_OK
        status_response.json.side_effect = ValueError("Invalid JSON")
        status_response.text = "Invalid response"
        mock_get.return_value = status_response

        # Get transaction status
        result = self.client.get_transaction_status(self.server_correlation_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Réponse invalide de MVola", result["error"])

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_status_timeout(self, mock_post, mock_get):
        """Test status check handles timeout"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock timeout
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        # Get transaction status
        result = self.client.get_transaction_status(self.server_correlation_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Délai d'attente dépassé", result["error"])

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_status_network_error(self, mock_post, mock_get):
        """Test status check handles network errors"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock network error
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # Get transaction status
        result = self.client.get_transaction_status(self.server_correlation_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("error", result)


@override_settings(
    MVOLA_BASE_URL="https://devapi.mvola.mg",
    MVOLA_CONSUMER_KEY="test_consumer_key",
    MVOLA_CONSUMER_SECRET="test_consumer_secret",
    MVOLA_PARTNER_MSISDN="0340000000",
    MVOLA_PARTNER_NAME="TestPartner",
    MVOLA_CALLBACK_URL="http://localhost:8000/api/payments/mvola/callback/",
)
class MvolaAPIClientTransactionDetailsTests(TestCase):
    """Test transaction details retrieval in MvolaAPIClient"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear cache before each test
        cache.clear()

        # Initialize client
        self.client = MvolaAPIClient()

        # Test transaction ID
        self.transaction_id = "TXN_REF_12345"

    def tearDown(self):
        """Clean up after each test"""
        cache.clear()

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_details_success(self, mock_post, mock_get):
        """Test successful transaction details retrieval"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token", "token_type": "Bearer", "expires_in": 3600}
        mock_post.return_value = token_response

        # Mock details response
        details_response = Mock()
        details_response.status_code = HTTP_OK
        details_response.json.return_value = {
            "transactionId": self.transaction_id,
            "status": "completed",
            "amount": "103000",
            "currency": "Ar",
            "fees": [{"feeAmount": "500", "feeCurrency": "Ar"}],
            "creationDate": "2024-01-15T10:30:00Z",
            "completionDate": "2024-01-15T10:31:00Z",
        }
        mock_get.return_value = details_response

        # Get transaction details
        result = self.client.get_transaction_details(self.transaction_id)

        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["transaction_id"], self.transaction_id)
        self.assertIn("details", result)
        self.assertEqual(result["details"]["status"], "completed")
        self.assertEqual(result["details"]["amount"], "103000")

        # Verify GET request was made
        self.assertTrue(mock_get.called)

        # Verify request details
        details_call = mock_get.call_args
        details_url = details_call[0][0]
        details_headers = details_call[1]["headers"]

        # Verify URL contains transaction ID
        self.assertIn(self.transaction_id, details_url)
        self.assertIn("/mvola/mm/transactions/type/merchantpay/1.0.0/", details_url)

        # Verify headers
        self.assertIn("Authorization", details_headers)
        self.assertIn("Bearer test_token", details_headers["Authorization"])
        self.assertIn("X-CorrelationID", details_headers)
        self.assertEqual(details_headers["Version"], "1.0")

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_details_not_found(self, mock_post, mock_get):
        """Test details retrieval for non-existent transaction"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock 404 response
        details_response = Mock()
        details_response.status_code = 404
        details_response.json.return_value = {"code": "NOT_FOUND", "message": "Transaction not found"}
        mock_get.return_value = details_response

        # Get transaction details
        result = self.client.get_transaction_details(self.transaction_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Transaction introuvable", result["error"])
        self.assertEqual(result["status_code"], 404)

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_details_api_error(self, mock_post, mock_get):
        """Test details retrieval handles API errors"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock error response
        details_response = Mock()
        details_response.status_code = 500
        details_response.json.return_value = {"code": "INTERNAL_ERROR", "message": "Internal server error"}
        details_response.text = "Internal Server Error"
        mock_get.return_value = details_response

        # Get transaction details
        result = self.client.get_transaction_details(self.transaction_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["error_code"], "INTERNAL_ERROR")

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_details_invalid_json(self, mock_post, mock_get):
        """Test details retrieval handles invalid JSON response"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock invalid JSON response
        details_response = Mock()
        details_response.status_code = HTTP_OK
        details_response.json.side_effect = ValueError("Invalid JSON")
        details_response.text = "Invalid response"
        mock_get.return_value = details_response

        # Get transaction details
        result = self.client.get_transaction_details(self.transaction_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Réponse invalide de MVola", result["error"])

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_details_timeout(self, mock_post, mock_get):
        """Test details retrieval handles timeout"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock timeout
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        # Get transaction details
        result = self.client.get_transaction_details(self.transaction_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Délai d'attente dépassé", result["error"])

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_details_network_error(self, mock_post, mock_get):
        """Test details retrieval handles network errors"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock network error
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # Get transaction details
        result = self.client.get_transaction_details(self.transaction_id)

        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch("payments.services.mvola.api_client.requests.get")
    @patch("payments.services.mvola.api_client.requests.post")
    def test_get_transaction_details_with_fees(self, mock_post, mock_get):
        """Test details retrieval includes fee information"""
        # Mock token response
        token_response = Mock()
        token_response.status_code = HTTP_OK
        token_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = token_response

        # Mock details response with fees
        details_response = Mock()
        details_response.status_code = HTTP_OK
        details_response.json.return_value = {
            "transactionId": self.transaction_id,
            "status": "completed",
            "amount": "103000",
            "fees": [{"feeAmount": "500", "feeCurrency": "Ar", "feeType": "gateway"}],
        }
        mock_get.return_value = details_response

        # Get transaction details
        result = self.client.get_transaction_details(self.transaction_id)

        # Verify fees are included
        self.assertTrue(result["success"])
        self.assertIn("fees", result["details"])
        self.assertEqual(len(result["details"]["fees"]), 1)
        self.assertEqual(result["details"]["fees"][0]["feeAmount"], "500")
