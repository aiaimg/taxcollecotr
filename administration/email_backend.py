"""
Custom SMTP Email Backend with SSL certificate verification disabled.
This is useful for development environments or servers with self-signed certificates.
"""

import ssl
import smtplib

from django.core.mail.backends.smtp import EmailBackend


class SSLIgnoreEmailBackend(EmailBackend):
    """
    SMTP Email Backend that ignores SSL certificate verification errors.
    Use this when connecting to SMTP servers with self-signed or invalid certificates.
    """

    def open(self):
        """
        Open a connection to the mail server with SSL verification disabled.
        """
        if self.connection:
            return False

        # Create SSL context that ignores certificate errors
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connection_params = {"local_hostname": None}

        if self.timeout is not None:
            connection_params["timeout"] = self.timeout

        try:
            if self.use_ssl:
                # For SSL connections (port 465)
                self.connection = smtplib.SMTP_SSL(
                    self.host,
                    self.port,
                    context=ssl_context,
                    **connection_params
                )
            else:
                # For regular or TLS connections
                self.connection = smtplib.SMTP(
                    self.host,
                    self.port,
                    **connection_params
                )
                
                # Upgrade to TLS if required
                if self.use_tls:
                    self.connection.starttls(context=ssl_context)

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True

        except OSError:
            if not self.fail_silently:
                raise
            return False
