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
def test_unlink_requires_password_redirect():
    User = get_user_model()
    user = User.objects.create_user(username="nopass", email="nopass@example.com")
    user.set_unusable_password()
    user.save()
    ensure_google_app()
    sa = SocialAccount.objects.create(user=user, provider="google", uid="uid-x", extra_data={"email": user.email})

    client = Client()
    client.force_login(user)
    resp = client.get(reverse("core:social_account_unlink", args=[sa.id]))
    assert resp.status_code == 302
    assert reverse("account_set_password") in resp.url


@pytest.mark.django_db
def test_unlink_success_message_and_delete():
    User = get_user_model()
    user = User.objects.create_user(username="withpass", email="withpass@example.com", password="x")
    ensure_google_app()
    sa = SocialAccount.objects.create(user=user, provider="google", uid="uid-y", extra_data={"email": user.email})

    client = Client()
    client.force_login(user)
    # Confirm page
    resp = client.get(reverse("core:social_account_unlink", args=[sa.id]))
    assert resp.status_code == 200
    # Post confirm
    resp = client.post(reverse("core:social_account_unlink", args=[sa.id]), {"confirm": "yes"}, follow=True)
    assert resp.status_code == 200
    assert not SocialAccount.objects.filter(id=sa.id).exists()
    content = resp.content.decode("utf-8")
    assert "Compte social délié avec succès" in content

