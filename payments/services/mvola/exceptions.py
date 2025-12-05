"""
MVola Exception Classes

Custom exceptions for handling MVola-specific errors throughout the integration.
"""


class MvolaError(Exception):
    """
    Base exception for all MVola-related errors.

    This is the parent class for all MVola exceptions and can be used
    to catch any MVola-related error.
    """

    pass


class MvolaAuthenticationError(MvolaError):
    """
    Raised when OAuth2 authentication with MVola fails.

    This includes:
    - Invalid consumer key or secret
    - Token generation failures
    - Token refresh failures
    - Expired or invalid access tokens
    """

    pass


class MvolaAPIError(MvolaError):
    """
    Raised when MVola API requests fail.

    This includes:
    - HTTP errors (4xx, 5xx)
    - Network timeouts
    - Invalid API responses
    - Payment initiation failures
    - Status check failures
    """

    pass


class MvolaValidationError(MvolaError):
    """
    Raised when input validation fails before making API calls.

    This includes:
    - Invalid MSISDN format
    - Invalid amount (below minimum or above maximum)
    - Missing required fields
    - Invalid data types
    """

    pass


class MvolaCallbackError(MvolaError):
    """
    Raised when callback processing fails.

    This includes:
    - Invalid callback payload
    - Missing serverCorrelationId
    - Transaction not found
    - Status update failures
    """

    pass
