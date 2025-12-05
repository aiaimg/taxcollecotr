#!/usr/bin/env python
"""
Script to create a test SMTP configuration
Usage: python scripts/create_test_smtp.py
"""
import os
import sys

import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

from django.contrib.auth.models import User

from administration.models import SMTPConfiguration


def create_test_smtp():
    """Create a test SMTP configuration"""

    print("=" * 60)
    print("SMTP Configuration Setup")
    print("=" * 60)
    print()

    # Get admin user
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("⚠ No admin user found. Creating one...")
            admin_user = User.objects.create_superuser(username="admin", email="admin@example.com", password="admin123")
            print(f"✓ Admin user created: {admin_user.username}")
    except Exception as e:
        print(f"✗ Error getting admin user: {e}")
        admin_user = None

    print()
    print("Choose SMTP Provider:")
    print("1. Gmail")
    print("2. Office 365 / Outlook")
    print("3. SendGrid")
    print("4. Mailgun")
    print("5. Custom")
    print()

    choice = input("Enter choice (1-5): ").strip()

    if choice == "1":
        # Gmail
        name = "Gmail"
        host = "smtp.gmail.com"
        port = 587
        encryption = "tls"
        print("\n📧 Gmail Configuration")
        print("Note: You need to use an App Password, not your Gmail password")
        print("Generate one at: https://myaccount.google.com/apppasswords")

    elif choice == "2":
        # Office 365
        name = "Office 365"
        host = "smtp.office365.com"
        port = 587
        encryption = "tls"
        print("\n📧 Office 365 Configuration")

    elif choice == "3":
        # SendGrid
        name = "SendGrid"
        host = "smtp.sendgrid.net"
        port = 587
        encryption = "tls"
        print("\n📧 SendGrid Configuration")
        print("Note: Username should be 'apikey' and password is your SendGrid API key")

    elif choice == "4":
        # Mailgun
        name = "Mailgun"
        host = "smtp.mailgun.org"
        port = 587
        encryption = "tls"
        print("\n📧 Mailgun Configuration")

    else:
        # Custom
        print("\n📧 Custom SMTP Configuration")
        name = input("Configuration name: ").strip()
        host = input("SMTP host: ").strip()
        port = int(input("SMTP port (587): ").strip() or "587")
        encryption = input("Encryption (tls/ssl/none): ").strip() or "tls"

    print()
    username = input("SMTP username/email: ").strip()
    password = input("SMTP password: ").strip()
    from_email = input(f"From email ({username}): ").strip() or username
    from_name = input("From name (Tax Collector): ").strip() or "Tax Collector"

    print()
    daily_limit = input("Daily email limit (500): ").strip()
    daily_limit = int(daily_limit) if daily_limit else 500

    print()
    is_active = input("Activate this configuration? (y/n): ").strip().lower() == "y"

    # Deactivate other configs if this one will be active
    if is_active:
        SMTPConfiguration.objects.filter(is_active=True).update(is_active=False)
        print("✓ Deactivated other SMTP configurations")

    # Create configuration
    try:
        smtp_config = SMTPConfiguration.objects.create(
            name=name,
            host=host,
            port=port,
            encryption=encryption,
            username=username,
            password=password,
            from_email=from_email,
            from_name=from_name,
            daily_limit=daily_limit,
            is_active=is_active,
            created_by=admin_user,
            modified_by=admin_user,
            description=f"Created via setup script on {django.utils.timezone.now().strftime('%Y-%m-%d %H:%M')}",
        )

        print()
        print("=" * 60)
        print("✓ SMTP Configuration Created Successfully!")
        print("=" * 60)
        print(f"Name: {smtp_config.name}")
        print(f"Host: {smtp_config.host}:{smtp_config.port}")
        print(f"Encryption: {smtp_config.get_encryption_display()}")
        print(f"From: {smtp_config.from_name} <{smtp_config.from_email}>")
        print(f"Daily Limit: {smtp_config.daily_limit}")
        print(f"Active: {'Yes' if smtp_config.is_active else 'No'}")
        print()

        # Test connection
        print("Testing SMTP connection...")
        success, message = smtp_config.test_connection()

        if success:
            print(f"✓ {message}")
            print()

            # Offer to send test email
            send_test = input("Send a test email? (y/n): ").strip().lower() == "y"

            if send_test:
                test_email = input("Enter test email address: ").strip()

                if test_email:
                    from administration.email_utils import send_email

                    success, result, logs = send_email(
                        subject="Test Email - Tax Collector SMTP",
                        message="This is a test email to verify SMTP configuration.",
                        recipient_list=[test_email],
                        html_message="<h1>Test Email</h1><p>This is a test email to verify SMTP configuration.</p>",
                        email_type="test",
                        fail_silently=False,
                    )

                    if success:
                        print(f"✓ Test email sent to {test_email}")
                    else:
                        print(f"✗ Failed to send test email: {result}")
        else:
            print(f"✗ {message}")
            print("Please check your SMTP settings and try again.")

        print()
        print("Next steps:")
        print(f"1. Access admin panel: http://127.0.0.1:8000/admin/administration/smtpconfiguration/")
        print(
            f"2. View configuration: http://127.0.0.1:8000/admin/administration/smtpconfiguration/{smtp_config.pk}/change/"
        )
        print(f"3. Test again: python manage.py test_smtp your-email@example.com")
        print()

    except Exception as e:
        print(f"\n✗ Error creating SMTP configuration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_test_smtp()
