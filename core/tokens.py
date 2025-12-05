"""
Token generator for email verification
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token generator for email verification.
    Creates a unique token based on user's pk, email, and is_active status.
    """

    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key, email, and is_active status
        together with the timestamp.
        """
        return f"{user.pk}{user.email}{user.is_active}{timestamp}"


email_verification_token = EmailVerificationTokenGenerator()
