import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_missing_credentials_hide_google_signup(settings):
    settings.GOOGLE_OAUTH_CLIENT_ID = ""
    settings.GOOGLE_OAUTH_CLIENT_SECRET = ""
    client = Client()
    resp = client.get(reverse("account_signup"))
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")
    assert "provider_login_url" not in content
    assert "ri-google-fill" not in content

