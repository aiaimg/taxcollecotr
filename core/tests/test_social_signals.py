import pytest
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.contrib.sites.models import Site

from core.models import AuditLog, UserProfile


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
def test_account_linking_creates_socialaccount():
    request = setup_request_with_session()
    User = get_user_model()
    user = User.objects.create_user(username="linked", email="linked@example.com", password="x")

    app = ensure_google_app()
    provider = GoogleProvider(request, app=app)
    data = {
        "sub": "link-uid",
        "email": "linked@example.com",
        "email_verified": True,
        "given_name": "Linked",
        "family_name": "User",
    }
    login = provider.sociallogin_from_response(request, data)
    login.connect(request, user)

    assert SocialAccount.objects.filter(user=user, provider="google").exists()
    assert AuditLog.objects.filter(action="CREATE", table_concernee="SocialAccount").exists()
    # Profile created or existing
    assert hasattr(user, "profile")


@pytest.mark.django_db
def test_unlink_requires_password():
    request = setup_request_with_session()
    User = get_user_model()
    user = User.objects.create_user(username="nopass", email="nopass@example.com", password=None)
    user.set_unusable_password()
    user.save()

    app = ensure_google_app()
    sa = SocialAccount.objects.create(user=user, provider="google", uid="unlink-uid", extra_data={})

    with pytest.raises(Exception):
        sa.delete()


@pytest.mark.django_db
def test_unlink_removes_socialaccount_with_password():
    request = setup_request_with_session()
    User = get_user_model()
    user = User.objects.create_user(username="withpass", email="withpass@example.com", password="x")

    app = ensure_google_app()
    sa = SocialAccount.objects.create(user=user, provider="google", uid="unlink2-uid", extra_data={})

    sa.delete()

    assert not SocialAccount.objects.filter(user=user, provider="google").exists()
    assert AuditLog.objects.filter(action="DELETE", table_concernee="SocialAccount", user=user).exists()

