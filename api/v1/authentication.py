"""
JWT Authentication for API
"""

import logging

from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that provides better error handling
    """

    def authenticate(self, request):
        """
        Override authenticate to provide better error messages
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except TokenError as e:
            logger.warning(f"Token error: {str(e)}")
            raise exceptions.AuthenticationFailed({"detail": "Invalid or expired token.", "code": "token_invalid"})
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise exceptions.AuthenticationFailed({"detail": "Authentication failed.", "code": "authentication_failed"})
