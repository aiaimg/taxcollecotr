"""
Unit tests for MVola Fee Calculator Service

Tests the fee calculation logic for MVola transactions including:
- 3% platform fee calculation
- Total amount calculation
- Gateway fee extraction from callback data
- Rounding behavior
"""

from decimal import Decimal

from django.test import TestCase

from payments.services.mvola import MvolaFeeCalculator


class MvolaFeeCalculatorTests(TestCase):
    """Test MVola fee calculation logic"""

    def test_calculate_total_amount_basic(self):
        """Test basic 3% fee calculation with round numbers"""
        base_amount = Decimal("100000")
        result = MvolaFeeCalculator.calculate_total_amount(base_amount)

        self.assertEqual(result["base_amount"], Decimal("100000"))
        self.assertEqual(result["platform_fee"], Decimal("3000"))
        self.assertEqual(result["total_amount"], Decimal("103000"))

    def test_calculate_total_amount_with_rounding_up(self):
        """Test fee calculation with rounding up (ROUND_HALF_UP)"""
        # 3% of 10001 = 300.03, should round to 300
        base_amount = Decimal("10001")
        result = MvolaFeeCalculator.calculate_total_amount(base_amount)

        self.assertEqual(result["base_amount"], Decimal("10001"))
        self.assertEqual(result["platform_fee"], Decimal("300"))
        self.assertEqual(result["total_amount"], Decimal("10301"))

    def test_calculate_total_amount_with_rounding_half_up(self):
        """Test fee calculation with exact half rounding (should round up)"""
        # 3% of 10017 = 300.51, should round to 301
        base_amount = Decimal("10017")
        result = MvolaFeeCalculator.calculate_total_amount(base_amount)

        self.assertEqual(result["base_amount"], Decimal("10017"))
        self.assertEqual(result["platform_fee"], Decimal("301"))
        self.assertEqual(result["total_amount"], Decimal("10318"))

    def test_calculate_total_amount_small_amount(self):
        """Test fee calculation with small amounts"""
        base_amount = Decimal("100")
        result = MvolaFeeCalculator.calculate_total_amount(base_amount)

        self.assertEqual(result["base_amount"], Decimal("100"))
        self.assertEqual(result["platform_fee"], Decimal("3"))
        self.assertEqual(result["total_amount"], Decimal("103"))

    def test_calculate_total_amount_large_amount(self):
        """Test fee calculation with large amounts"""
        base_amount = Decimal("5000000")
        result = MvolaFeeCalculator.calculate_total_amount(base_amount)

        self.assertEqual(result["base_amount"], Decimal("5000000"))
        self.assertEqual(result["platform_fee"], Decimal("150000"))
        self.assertEqual(result["total_amount"], Decimal("5150000"))

    def test_calculate_total_amount_returns_dict(self):
        """Test that calculate_total_amount returns a dictionary with correct keys"""
        base_amount = Decimal("50000")
        result = MvolaFeeCalculator.calculate_total_amount(base_amount)

        self.assertIsInstance(result, dict)
        self.assertIn("base_amount", result)
        self.assertIn("platform_fee", result)
        self.assertIn("total_amount", result)
        self.assertEqual(len(result), 3)

    def test_extract_gateway_fees_with_fees(self):
        """Test extracting gateway fees from callback data with fees present"""
        callback_data = {
            "serverCorrelationId": "test123",
            "transactionStatus": "completed",
            "fees": [{"feeAmount": "500"}],
        }

        result = MvolaFeeCalculator.extract_gateway_fees(callback_data)
        self.assertEqual(result, Decimal("500"))

    def test_extract_gateway_fees_with_multiple_fees(self):
        """Test extracting gateway fees when multiple fees are present (takes first)"""
        callback_data = {"fees": [{"feeAmount": "500"}, {"feeAmount": "200"}]}

        result = MvolaFeeCalculator.extract_gateway_fees(callback_data)
        self.assertEqual(result, Decimal("500"))

    def test_extract_gateway_fees_no_fees_key(self):
        """Test extracting gateway fees when fees key is missing"""
        callback_data = {"serverCorrelationId": "test123", "transactionStatus": "completed"}

        result = MvolaFeeCalculator.extract_gateway_fees(callback_data)
        self.assertEqual(result, Decimal("0"))

    def test_extract_gateway_fees_empty_fees_array(self):
        """Test extracting gateway fees when fees array is empty"""
        callback_data = {"fees": []}

        result = MvolaFeeCalculator.extract_gateway_fees(callback_data)
        self.assertEqual(result, Decimal("0"))

    def test_extract_gateway_fees_no_fee_amount(self):
        """Test extracting gateway fees when feeAmount is missing"""
        callback_data = {"fees": [{"feeType": "gateway"}]}

        result = MvolaFeeCalculator.extract_gateway_fees(callback_data)
        self.assertEqual(result, Decimal("0"))

    def test_extract_gateway_fees_with_decimal_amount(self):
        """Test extracting gateway fees with decimal amounts"""
        callback_data = {"fees": [{"feeAmount": "1250.50"}]}

        result = MvolaFeeCalculator.extract_gateway_fees(callback_data)
        self.assertEqual(result, Decimal("1250.50"))

    def test_extract_gateway_fees_with_integer_amount(self):
        """Test extracting gateway fees with integer amounts"""
        callback_data = {"fees": [{"feeAmount": 750}]}

        result = MvolaFeeCalculator.extract_gateway_fees(callback_data)
        self.assertEqual(result, Decimal("750"))

    def test_platform_fee_percentage_constant(self):
        """Test that the platform fee percentage is correctly set to 3%"""
        self.assertEqual(MvolaFeeCalculator.PLATFORM_FEE_PERCENTAGE, Decimal("3.00"))

    def test_calculate_total_amount_precision(self):
        """Test that calculated fees maintain proper decimal precision"""
        base_amount = Decimal("123456")
        result = MvolaFeeCalculator.calculate_total_amount(base_amount)

        # 3% of 123456 = 3703.68, should round to 3704
        self.assertEqual(result["platform_fee"], Decimal("3704"))
        self.assertEqual(result["total_amount"], Decimal("127160"))

        # Verify no decimal places in result
        self.assertEqual(result["platform_fee"] % 1, 0)
        self.assertEqual(result["total_amount"] % 1, 0)
