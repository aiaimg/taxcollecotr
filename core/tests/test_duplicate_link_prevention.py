import pytest
from django.db import IntegrityError
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model

from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.sites.models import Site
from allauth.socialaccount.providers.google.provider import GoogleProvider


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


@pytest.mark.django_db(transaction=True)
def test_duplicate_link_prevention():
    request = setup_request_with_session()
    User = get_user_model()
    user_a = User.objects.create_user(username="usera", email="a@example.com", password="x")
    user_b = User.objects.create_user(username="userb", email="b@example.com", password="x")

    app = ensure_google_app()

    # Existing linked account for user A
    SocialAccount.objects.create(
        user=user_a,
        provider="google",
        uid="dup-uid",
        extra_data={"email": "a@example.com", "email_verified": True},
    )

    provider = GoogleProvider(request, app=app)
    data = {
        "sub": "dup-uid",
        "email": "b@example.com",
        "email_verified": True,
        "given_name": "B",
        "family_name": "User",
    }
    login = provider.sociallogin_from_response(request, data)

    with pytest.raises(IntegrityError):
        login.connect(request, user_b)

    # Still linked to user A, not user B
    sa = SocialAccount.objects.get(provider="google", uid="dup-uid")
    assert sa.user_id == user_a.id
    assert not SocialAccount.objects.filter(user=user_b, provider="google").exists()
