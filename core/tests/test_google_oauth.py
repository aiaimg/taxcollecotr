import pytest
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.adapter import get_adapter


@pytest.mark.django_db
def test_google_oauth_registration_creates_verified_user(settings):
    request = RequestFactory().get("/")
    mw = SessionMiddleware(lambda r: None)
    mw.process_request(request)
    request.session.save()

    app = SocialApp.objects.filter(provider="google").first()
    if app is None:
        app = SocialApp.objects.create(provider="google", name="Google", client_id="test", secret="test")
        site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "localhost", "name": "TaxCollector"})
        app.sites.add(site)

    provider = GoogleProvider(request, app=app)
    data = {
        "sub": "1234567890",
        "email": "newuser@example.com",
        "email_verified": True,
        "given_name": "New",
        "family_name": "User",
        "picture": "https://example.com/avatar.png",
    }

    login = provider.sociallogin_from_response(request, data)
    from core.social_adapters import CustomSocialAccountAdapter
    CustomSocialAccountAdapter().pre_social_login(request, login)
    # Ensure our social adapter is active
    adapter = get_adapter()
    assert adapter is not None

    login.save(request)

    User = get_user_model()
    user = User.objects.get(email="newuser@example.com")
    email_obj = EmailAddress.objects.get(user=user, email="newuser@example.com")
    assert email_obj.verified is True
    assert email_obj.primary is True


@pytest.mark.django_db
def test_email_uniqueness_on_oauth_registration_links_existing_user(settings):
    request = RequestFactory().get("/")
    mw = SessionMiddleware(lambda r: None)
    mw.process_request(request)
    request.session.save()
    User = get_user_model()
    existing = User.objects.create_user(username="existing", email="existing@example.com", password="x")

    app = SocialApp.objects.filter(provider="google").first()
    if app is None:
        app = SocialApp.objects.create(provider="google", name="Google", client_id="test", secret="test")
        site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "localhost", "name": "TaxCollector"})
        app.sites.add(site)

    provider = GoogleProvider(request, app=app)
    data = {
        "sub": "abc-xyz",
        "email": "existing@example.com",
        "email_verified": True,
        "given_name": "Existing",
        "family_name": "User",
    }
    login = provider.sociallogin_from_response(request, data)
    from core.social_adapters import CustomSocialAccountAdapter
    CustomSocialAccountAdapter().pre_social_login(request, login)
    login.save(request, connect=True)

    # No duplicate user created
    assert User.objects.filter(email="existing@example.com").count() == 1
    # Social account linked to existing user
    assert login.account.user_id == existing.id
