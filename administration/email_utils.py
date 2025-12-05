"""
Email utility functions using SMTP configuration from database
"""

import logging
import ssl

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils import timezone

from .models import EmailLog, SMTPConfiguration

logger = logging.getLogger(__name__)


def get_smtp_backend():
    """
    Get configured SMTP backend settings from database
    Returns a dictionary with email backend configuration
    """
    smtp_config = SMTPConfiguration.get_active_config()

    if not smtp_config:
        logger.warning("No active SMTP configuration found. Using default settings.")
        return None

    if not smtp_config.can_send_email():
        logger.error(f"Daily email limit reached for {smtp_config.name}")
        return None

    # Auto-detect SSL for port 465 (common misconfiguration where users select TLS but use port 465)
    use_ssl = smtp_config.encryption == "ssl" or smtp_config.port == 465
    use_tls = smtp_config.encryption == "tls" and smtp_config.port != 465

    return {
        "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "EMAIL_HOST": smtp_config.host,
        "EMAIL_PORT": smtp_config.port,
        "EMAIL_HOST_USER": smtp_config.username,
        "EMAIL_HOST_PASSWORD": smtp_config.password,
        "EMAIL_USE_TLS": use_tls,
        "EMAIL_USE_SSL": use_ssl,
        "DEFAULT_FROM_EMAIL": f"{smtp_config.from_name} <{smtp_config.from_email}>",
        "SERVER_EMAIL": smtp_config.from_email,
    }


def send_email(
    subject,
    message,
    recipient_list,
    html_message=None,
    email_type="",
    related_object_type="",
    related_object_id="",
    fail_silently=False,
):
    """
    Send email using configured SMTP settings

    Args:
        subject: Email subject
        message: Plain text message
        recipient_list: List of recipient email addresses
        html_message: Optional HTML version of the message
        email_type: Type of email (e.g., 'reminder', 'notification')
        related_object_type: Type of related object
        related_object_id: ID of related object
        fail_silently: If True, don't raise exceptions on failure

    Returns:
        tuple: (success: bool, message: str, email_logs: list)
    """
    smtp_config = SMTPConfiguration.get_active_config()

    if not smtp_config:
        error_msg = "No active SMTP configuration found"
        logger.error(error_msg)
        if not fail_silently:
            raise Exception(error_msg)
        return False, error_msg, []

    if not smtp_config.can_send_email():
        error_msg = f"Daily email limit reached for {smtp_config.name}"
        logger.error(error_msg)
        if not fail_silently:
            raise Exception(error_msg)
        return False, error_msg, []

    # Auto-detect SSL for port 465 (common misconfiguration where users select TLS but use port 465)
    use_ssl = smtp_config.encryption == "ssl" or smtp_config.port == 465
    use_tls = smtp_config.encryption == "tls" and smtp_config.port != 465

    # Create SSL context that ignores certificate errors
    # This is necessary because many dev environments or corporate servers have certificate issues
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    email_logs = []
    success_count = 0

    try:
        # Create connection using custom backend that ignores SSL certificate errors
        connection = get_connection(
            backend="administration.email_backend.SSLIgnoreEmailBackend",
            host=smtp_config.host,
            port=smtp_config.port,
            username=smtp_config.username,
            password=smtp_config.password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            timeout=10,
            fail_silently=fail_silently,
        )

        for recipient in recipient_list:
            # Create email log entry
            email_log = EmailLog.objects.create(
                smtp_config=smtp_config,
                recipient=recipient,
                subject=subject,
                body=message,
                html_body=html_message or "",
                status="pending",
                email_type=email_type,
                related_object_type=related_object_type,
                related_object_id=str(related_object_id),
            )
            email_logs.append(email_log)

            try:
                # Create email message
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=f"{smtp_config.from_name} <{smtp_config.from_email}>",
                    to=[recipient],
                    reply_to=[smtp_config.reply_to_email] if smtp_config.reply_to_email else None,
                    connection=connection,
                )

                # Attach HTML version if provided
                if html_message:
                    email.attach_alternative(html_message, "text/html")

                # Send email
                email.send(fail_silently=False)

                # Update log
                email_log.status = "sent"
                email_log.sent_at = timezone.now()
                email_log.save(update_fields=["status", "sent_at"])

                # Increment sent counter
                smtp_config.increment_counter()

                success_count += 1
                logger.info(f"Email sent successfully to {recipient}")

            except Exception as e:
                error_msg = str(e)
                email_log.status = "failed"
                email_log.error_message = error_msg
                email_log.save(update_fields=["status", "error_message"])

                logger.error(f"Failed to send email to {recipient}: {error_msg}")

                if not fail_silently:
                    raise

        if success_count == len(recipient_list):
            return True, f"Successfully sent {success_count} email(s)", email_logs
        elif success_count > 0:
            return True, f"Sent {success_count}/{len(recipient_list)} email(s)", email_logs
        else:
            return False, "Failed to send all emails", email_logs

    except Exception as e:
        error_msg = f"Error sending emails: {str(e)}"
        logger.error(error_msg)

        if not fail_silently:
            raise

        return False, error_msg, email_logs


def send_template_email(
    template_name,
    context,
    recipient_list,
    email_type="",
    related_object_type="",
    related_object_id="",
    fail_silently=False,
):
    """
    
        template_name: Path to template
        context: Context dictionary
        recipient_list: List of recipients
        email_type: Email type
        related_object_type: Related object type
        related_object_id: Related object ID
        fail_silently: Fail silently
        
    Returns:
        tuple: (success, message, logs)
    """
