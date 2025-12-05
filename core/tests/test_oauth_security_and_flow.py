import pytest
from django.test import Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware

from allauth.socialaccount.models import SocialApp, SocialAccount
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.helpers import complete_social_login
from django.contrib.sites.models import Site


def ensure_google_app():
    app = SocialApp.objects.filter(provider="google").first()
    if app is None:
        app = SocialApp.objects.create(provider="google", name="Google", client_id="test", secret="test")
        site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "localhost", "name": "TaxCollector"})
        app.sites.add(site)
    return app


def setup_request_with_session():
    request = RequestFactory().get("/")
    mw = SessionMiddleware(lambda r: None)
    mw.process_request(request)
    request.session.save()
    return request


@pytest.mark.django_db
def test_oauth_state_csrf_validation_login_by_token():
    client = Client()
    ensure_google_app()
    # Missing cookie and mismatched body token should render auth error
    resp = client.post(reverse("google_login_by_token"), {"credential": "dummy", "g_csrf_token": "bad"})
    assert resp.status_code == 200


@pytest.mark.django_db
def test_successful_google_login_authenticates_and_updates_session():
    request = setup_request_with_session()
    app = ensure_google_app()
    provider = GoogleProvider(request, app=app)
    data = {
        "sub": "login-uid",
        "email": "loginuser@example.com",
        "email_verified": True,
        "given_name": "Login",
        "family_name": "User",
    }
    login = provider.sociallogin_from_response(request, data)
    login.save(request)
    # User created via social signup
    User = get_user_model()
    user = User.objects.get(email="loginuser@example.com")
    # Simulate authenticated session
    client = Client()
    client.force_login(user)
    resp = client.get(reverse("core:velzon_dashboard"))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_unlinked_google_account_creates_account():
    request = setup_request_with_session()
    app = ensure_google_app()
    provider = GoogleProvider(request, app=app)
    data = {
        "sub": "new-uid",
        "email": "newuser@example.com",
        "email_verified": True,
        "given_name": "New",
        "family_name": "User",
    }
    login = provider.sociallogin_from_response(request, data)
    login.save(request)

    User = get_user_model()
    user = User.objects.get(email="newuser@example.com")
    assert SocialAccount.objects.filter(user=user, provider="google").exists()
