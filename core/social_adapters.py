from django.contrib.auth import get_user_model
from django.http import HttpResponse

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def complete_login(self, request, app, token, response, **kwargs):
        login = super().complete_login(request, app, token, response, **kwargs)

        email = login.user and getattr(login.user, "email", None)
        if not email:
            email = login.account.extra_data.get("email")

        if email:
            if hasattr(login, "email_addresses") and login.email_addresses:
                for addr in login.email_addresses:
                    if addr.email == email:
                        addr.verified = True
                        addr.primary = True
            else:
                login.email_addresses = [
                    EmailAddress(email=email, verified=True, primary=True)
                ]

        data = login.account.extra_data or {}
        login.user.first_name = data.get("given_name") or login.user.first_name
        login.user.last_name = data.get("family_name") or login.user.last_name

        return login


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        User = get_user_model()
        email = sociallogin.user and getattr(sociallogin.user, "email", None)
        if not email:
            email = sociallogin.account.extra_data.get("email")

        if email:
            existing = User.objects.filter(email=email).first()
            if existing and not sociallogin.is_existing:
                sociallogin.connect(request, existing)

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        import logging
        logger = logging.getLogger(__name__)
        logger.error("OAuth authentication error", extra={"provider": getattr(provider, "id", provider), "error": str(error or exception)})
