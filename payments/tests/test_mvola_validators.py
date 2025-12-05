"""
Unit tests for MVola validators module.

Tests MSISDN validation logic for Madagascar phone numbers.
"""

from django.test import TestCase

from payments.services.mvola import MvolaValidationError, validate_msisdn


class MvolaValidatorsTestCase(TestCase):
    """Test cases for MVola validation functions"""

    def test_validate_msisdn_valid_format(self):
        """Test validation with valid MSISDN formats"""
        # Test various valid Madagascar phone numbers
        valid_msisdns = [
            "0340000000",  # Telma
            "0341234567",  # Telma
            "0349999999",  # Telma
            "0320000000",  # Orange
            "0321234567",  # Orange
            "0330000000",  # Airtel
            "0331234567",  # Airtel
            "0380000000",  # Other operator
            "0381234567",  # Other operator
        ]

        for msisdn in valid_msisdns:
            with self.subTest(msisdn=msisdn):
                result = validate_msisdn(msisdn)
                self.assertEqual(result, msisdn)

    def test_validate_msisdn_with_whitespace(self):
        """Test validation removes leading/trailing whitespace"""
        test_cases = [
            (" 0340000000", "0340000000"),
            ("0340000000 ", "0340000000"),
            (" 0340000000 ", "0340000000"),
            ("  0341234567  ", "0341234567"),
        ]

        for input_msisdn, expected in test_cases:
            with self.subTest(input=input_msisdn):
                result = validate_msisdn(input_msisdn)
                self.assertEqual(result, expected)

    def test_validate_msisdn_empty_string(self):
        """Test validation fails with empty string"""
        with self.assertRaises(MvolaValidationError) as context:
            validate_msisdn("")

        self.assertIn("numéro de téléphone est requis", str(context.exception))

    def test_validate_msisdn_none(self):
        """Test validation fails with None"""
        with self.assertRaises(MvolaValidationError) as context:
            validate_msisdn(None)

        self.assertIn("numéro de téléphone est requis", str(context.exception))

    def test_validate_msisdn_too_short(self):
        """Test validation fails with too few digits"""
        invalid_msisdns = [
            "034000000",  # 9 digits
            "03400",  # 5 digits
            "034",  # 3 digits
        ]

        for msisdn in invalid_msisdns:
            with self.subTest(msisdn=msisdn):
                with self.assertRaises(MvolaValidationError) as context:
                    validate_msisdn(msisdn)

                self.assertIn("Format de numéro invalide", str(context.exception))
                self.assertIn("10 chiffres", str(context.exception))

    def test_validate_msisdn_too_long(self):
        """Test validation fails with too many digits"""
        invalid_msisdns = [
            "03400000000",  # 11 digits
            "034000000000",  # 12 digits
        ]

        for msisdn in invalid_msisdns:
            with self.subTest(msisdn=msisdn):
                with self.assertRaises(MvolaValidationError) as context:
                    validate_msisdn(msisdn)

                self.assertIn("Format de numéro invalide", str(context.exception))

    def test_validate_msisdn_wrong_prefix(self):
        """Test validation fails when not starting with 03"""
        invalid_msisdns = [
            "0240000000",  # Starts with 02
            "0440000000",  # Starts with 04
            "1340000000",  # Starts with 13
            "3400000000",  # Missing leading 0
            "+261340000000",  # International format
        ]

        for msisdn in invalid_msisdns:
            with self.subTest(msisdn=msisdn):
                with self.assertRaises(MvolaValidationError) as context:
                    validate_msisdn(msisdn)

                self.assertIn("Format de numéro invalide", str(context.exception))
                self.assertIn("commencer par '03'", str(context.exception))

    def test_validate_msisdn_contains_letters(self):
        """Test validation fails with non-numeric characters"""
        invalid_msisdns = [
            "034000000A",
            "03400O0000",  # Letter O instead of zero
            "034-000-000",
            "034 000 000",
            "034.000.000",
        ]

        for msisdn in invalid_msisdns:
            with self.subTest(msisdn=msisdn):
                with self.assertRaises(MvolaValidationError) as context:
                    validate_msisdn(msisdn)

                self.assertIn("Format de numéro invalide", str(context.exception))

    def test_validate_msisdn_special_characters(self):
        """Test validation fails with special characters"""
        invalid_msisdns = [
            "034-000-0000",
            "034 000 0000",
            "(034)0000000",
            "+0340000000",
        ]

        for msisdn in invalid_msisdns:
            with self.subTest(msisdn=msisdn):
                with self.assertRaises(MvolaValidationError) as context:
                    validate_msisdn(msisdn)

                self.assertIn("Format de numéro invalide", str(context.exception))

    def test_validate_msisdn_error_message_includes_example(self):
        """Test error message includes example format"""
        with self.assertRaises(MvolaValidationError) as context:
            validate_msisdn("1234567890")

        error_message = str(context.exception)
        self.assertIn("0340000000", error_message)
        self.assertIn("Exemple", error_message)

    def test_validate_msisdn_error_message_in_french(self):
        """Test error messages are in French"""
        with self.assertRaises(MvolaValidationError) as context:
            validate_msisdn("invalid")

        error_message = str(context.exception)
        # Check for French keywords
        self.assertTrue(
            any(word in error_message for word in ["numéro", "invalide", "chiffres"]),
            "Error message should be in French",
        )
