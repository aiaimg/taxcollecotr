import pytest
from django.utils import timezone
from datetime import timedelta

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.contrib.sites.models import Site


def setup_request_with_session():
    request = RequestFactory().get("/")
    mw = SessionMiddleware(lambda r: None)
    mw.process_request(request)
    request.session.save()
    return request


def ensure_google_app():
    app = SocialApp.objects.filter(provider="google").first()
    if app is None:
        app = SocialApp.objects.create(provider="google", name="Google", client_id="test", secret="test")
        site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "localhost", "name": "TaxCollector"})
        app.sites.add(site)
    return app


@pytest.mark.django_db
def test_automatic_token_refresh_updates_stored_token():
    request = setup_request_with_session()
    app = ensure_google_app()
    provider = GoogleProvider(request, app=app)
    data = {
        "sub": "tok-uid",
        "email": "tokenuser@example.com",
        "email_verified": True,
        "given_name": "Token",
        "family_name": "User",
    }
    login = provider.sociallogin_from_response(request, data)
    login.save(request)

    # Existing stored token (expired)
    account = login.account
    existing = SocialToken.objects.create(
        app=app,
        account=account,
        token="old_access",
        token_secret="old_refresh",
        expires_at=timezone.now() - timedelta(days=1),
    )

    # New token from provider (refreshed)
    new_token = SocialToken(app=app, token="new_access", token_secret="new_refresh", expires_at=timezone.now() + timedelta(days=30))
    login.token = new_token
    # Store/refresh
    from allauth.socialaccount import app_settings as sc_app_settings
    sc_app_settings.STORE_TOKENS = True
    login._store_token()

    refreshed = SocialToken.objects.get(app=app, account=account)
    assert refreshed.token == "new_access"
    assert refreshed.token_secret == "new_refresh"
    assert refreshed.expires_at is not None and refreshed.expires_at > timezone.now()
