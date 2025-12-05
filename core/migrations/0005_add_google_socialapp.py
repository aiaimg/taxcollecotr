from django.db import migrations
import os


def create_google_socialapp(apps, schema_editor):
    SocialApp = apps.get_model("socialaccount", "SocialApp")
    Site = apps.get_model("sites", "Site")

    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

    site = Site.objects.filter(id=1).first()
    if site is None:
        site = Site.objects.create(id=1, domain="localhost", name="TaxCollector")

    if not SocialApp.objects.filter(provider="google").exists():
        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id=client_id,
            secret=client_secret,
        )
        app.sites.add(site)


def remove_google_socialapp(apps, schema_editor):
    SocialApp = apps.get_model("socialaccount", "SocialApp")
    SocialApp.objects.filter(provider="google").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_refactor_user_types"),
        ("sites", "0002_alter_domain_unique"),
        ("socialaccount", "0006_alter_socialaccount_extra_data"),
    ]

    operations = [
        migrations.RunPython(create_google_socialapp, remove_google_socialapp),
    ]

