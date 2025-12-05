"""
Management command to test SMTP configuration
"""

from django.core.management.base import BaseCommand

from administration.email_utils import send_email
from administration.models import SMTPConfiguration


class Command(BaseCommand):
    help = "Test SMTP configuration by sending a test email"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email address to send test email to")
        parser.add_argument(
            "--config-id", type=int, help="ID of SMTP configuration to test (uses active config if not specified)"
        )

    def handle(self, *args, **options):
        email = options["email"]
        config_id = options.get("config_id")

        # Get SMTP configuration
        if config_id:
            try:
                smtp_config = SMTPConfiguration.objects.get(id=config_id)
                self.stdout.write(f"Using SMTP configuration: {smtp_config.name}")
            except SMTPConfiguration.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"SMTP configuration with ID {config_id} not found"))
                return
        else:
            smtp_config = SMTPConfiguration.get_active_config()
            if not smtp_config:
                self.stdout.write(self.style.ERROR("No active SMTP configuration found"))
                self.stdout.write("Please create and activate an SMTP configuration in the admin panel")
                return
            self.stdout.write(f"Using active SMTP configuration: {smtp_config.name}")

        # Test connection
        self.stdout.write("Testing SMTP connection...")
        success, message = smtp_config.test_connection()

        if not success:
            self.stdout.write(self.style.ERROR(f"Connection test failed: {message}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Connection test passed: {message}"))

        # Send test email
        self.stdout.write(f"\nSending test email to {email}...")

        subject = "Test Email - Tax Collector SMTP Configuration"
        message_body = f"""
Bonjour,

Ceci est un email de test pour vérifier la configuration SMTP.

Configuration utilisée:
- Nom: {smtp_config.name}
- Serveur: {smtp_config.host}:{smtp_config.port}
- Chiffrement: {smtp_config.get_encryption_display()}
- Expéditeur: {smtp_config.from_name} <{smtp_config.from_email}>

Si vous recevez cet email, la configuration SMTP fonctionne correctement!

Cordialement,
L'équipe Tax Collector
"""

        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #405189; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f8f9fa; padding: 30px; }}
        .info-box {{ background-color: white; padding: 15px; border-left: 4px solid #405189; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #6c757d; font-size: 12px; }}
        .success {{ color: #28a745; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✓ Test Email</h1>
        </div>
        <div class="content">
            <p>Bonjour,</p>
            <p>Ceci est un email de test pour vérifier la configuration SMTP.</p>
            
            <div class="info-box">
                <h3>Configuration utilisée:</h3>
                <ul>
                    <li><strong>Nom:</strong> {smtp_config.name}</li>
                    <li><strong>Serveur:</strong> {smtp_config.host}:{smtp_config.port}</li>
                    <li><strong>Chiffrement:</strong> {smtp_config.get_encryption_display()}</li>
                    <li><strong>Expéditeur:</strong> {smtp_config.from_name} &lt;{smtp_config.from_email}&gt;</li>
                </ul>
            </div>
            
            <p class="success">✓ Si vous recevez cet email, la configuration SMTP fonctionne correctement!</p>
        </div>
        <div class="footer">
            <p>Cordialement,<br>L'équipe Tax Collector</p>
        </div>
    </div>
</body>
</html>
"""

        success, result_message, logs = send_email(
            subject=subject,
            message=message_body,
            recipient_list=[email],
            html_message=html_message,
            email_type="test",
            fail_silently=False,
        )

        if success:
            self.stdout.write(self.style.SUCCESS(f"\n✓ {result_message}"))
            self.stdout.write(f"Email sent to: {email}")
            self.stdout.write(f"Subject: {subject}")
            self.stdout.write(f"\nCheck the email inbox for {email} to confirm delivery.")
        else:
            self.stdout.write(self.style.ERROR(f"\n✗ {result_message}"))

            # Show error details from logs
            for log in logs:
                if log.status == "failed":
                    self.stdout.write(self.style.ERROR(f"Error: {log.error_message}"))
