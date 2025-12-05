from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = "Configure Google OAuth SocialApp from environment variables"

    def handle(self, *args, **options):
        client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
        client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")

        if not client_id or not client_secret:
            self.stderr.write(self.style.ERROR("Missing GOOGLE_OAUTH_CLIENT_ID or GOOGLE_OAUTH_CLIENT_SECRET"))
            return 1

        site = Site.objects.filter(id=1).first()
        if site is None:
            site = Site.objects.create(id=1, domain="localhost", name="TaxCollector")

        app = SocialApp.objects.filter(provider="google").first()
        if app is None:
            app = SocialApp.objects.create(provider="google", name="Google", client_id=client_id, secret=client_secret)
            app.sites.add(site)
            self.stdout.write(self.style.SUCCESS("Created Google SocialApp and linked to Site ID 1"))
        else:
            app.client_id = client_id
            app.secret = client_secret
            app.save()
            self.stdout.write(self.style.SUCCESS("Updated Google SocialApp credentials"))

        return 0

