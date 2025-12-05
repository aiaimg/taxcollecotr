"""
MVola Validators

Validation utilities for MVola payment data including MSISDN format validation.
"""

import re

from .exceptions import MvolaValidationError

# Madagascar phone number pattern: starts with 03, followed by 8 digits
MSISDN_PATTERN = re.compile(r"^03[0-9]{8}$")


def validate_msisdn(msisdn: str) -> str:
    """
    Validate and clean Madagascar MSISDN (phone number) format.

    Madagascar mobile numbers follow the format: 03XXXXXXXX
    - Must start with "03"
    - Must be exactly 10 digits
    - Examples: 0340000000, 0341234567, 0320000000

    Args:
        msisdn: Phone number string to validate

    Returns:
        str: Cleaned MSISDN (whitespace removed)

    Raises:
        MvolaValidationError: If MSISDN format is invalid

    Examples:
        >>> validate_msisdn("0340000000")
        "0340000000"

        >>> validate_msisdn(" 0341234567 ")
        "0341234567"

        >>> validate_msisdn("1234567890")
        MvolaValidationError: Format de numéro invalide...
    """
    if not msisdn:
        raise MvolaValidationError(
            "Le numéro de téléphone est requis. " "Format attendu: 03XXXXXXXX (10 chiffres commençant par 03)"
        )

    # Remove whitespace
    cleaned_msisdn = msisdn.strip()

    # Validate format
    if not MSISDN_PATTERN.match(cleaned_msisdn):
        raise MvolaValidationError(
            f"Format de numéro invalide: '{msisdn}'. "
            f"Le numéro doit commencer par '03' et contenir exactement 10 chiffres. "
            f"Exemple: 0340000000"
        )

    return cleaned_msisdn
