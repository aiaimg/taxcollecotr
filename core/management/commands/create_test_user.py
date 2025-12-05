from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = "Create a test user for development"

    def handle(self, *args, **options):
        try:
            user = User.objects.create_user(
                username="testuser",
                email="test@example.com",
                password="testpass123",
                first_name="Test",
                last_name="User",
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created test user: {user.username}\n"
                    f"Email: {user.email}\n"
                    f"Password: testpass123"
                )
            )
        except IntegrityError:
            self.stdout.write(self.style.WARNING("Test user already exists"))
