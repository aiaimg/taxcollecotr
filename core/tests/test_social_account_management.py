import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.sites.models import Site


def ensure_google_app():
    app = SocialApp.objects.filter(provider="google").first()
    if app is None:
        app = SocialApp.objects.create(provider="google", name="Google", client_id="test", secret="test")
        site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "localhost", "name": "TaxCollector"})
        app.sites.add(site)
    return app


@pytest.mark.django_db
def test_linked_google_account_displays_email():
    User = get_user_model()
    user = User.objects.create_user(username="u1", email="u1@example.com", password="x")
    ensure_google_app()

    SocialAccount.objects.create(
        user=user,
        provider="google",
        uid="uid-123",
        extra_data={"email": "u1@example.com", "email_verified": True},
    )

    client = Client()
    client.force_login(user)
    resp = client.get(reverse("core:social_accounts"))
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")
    assert "u1@example.com" in content
    assert "Google" in content

