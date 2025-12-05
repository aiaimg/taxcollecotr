"""
Management command to test email verification system
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test email verification system by creating a test user"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email address for test user")
        parser.add_argument("--username", type=str, help="Username (defaults to email prefix)")

    def handle(self, *args, **options):
        email = options["email"]
        username = options.get("username") or email.split("@")[0]

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f"User with username '{username}' already exists"))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f"User with email '{email}' already exists"))
            return

        # Create inactive user
        user = User.objects.create_user(
            username=username, email=email, password="TestPassword123!", is_active=False
        )
        user._user_type = "individual"  # Set for signal processing

        # Profile is created automatically by signal

        self.stdout.write(self.style.SUCCESS(f"✓ Created test user: {username}"))
        self.stdout.write(f"  Email: {email}")
        self.stdout.write(f"  Password: TestPassword123!")
        self.stdout.write(f"  Active: {user.is_active}")

        # Generate verification token
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        from core.tokens import email_verification_token

        token = email_verification_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        verification_url = f"http://localhost:8000/verify-email/{uid}/{token}/"

        self.stdout.write(f"\n✓ Verification URL:")
        self.stdout.write(f"  {verification_url}")

        self.stdout.write(f"\n✓ To test:")
        self.stdout.write(f"  1. Try to login with username '{username}' - should be blocked")
        self.stdout.write(f"  2. Visit the verification URL above")
        self.stdout.write(f"  3. Try to login again - should work")
