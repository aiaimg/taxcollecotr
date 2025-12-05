from django.contrib import messages
from django.contrib.auth import authenticate
from django.urls import reverse
from django.utils.translation import gettext as _

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_pk_to_url_str


def is_admin_user(user):
    """Check if user is admin or staff"""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or hasattr(user, "adminuserprofile")


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom allauth adapter that prevents admin users from logging in via regular login"""

    def authenticate(self, request, **credentials):
        """Override authenticate to exclude admin users"""
        user = authenticate(request, **credentials)

        if user is not None and is_admin_user(user):
            # Return None to indicate authentication failed
            return None

        return user

    def login(self, request, user):
        """Override login to add additional checks"""
        if is_admin_user(user):
            messages.error(request, _("Utilisateur non trouvé. Veuillez vérifier vos identifiants."))
            return None

        return super().login(request, user)

    def get_login_redirect_url(self, request):
        """Redirect based on user role after login"""
        user = request.user

        # Import agent utilities
        from django.urls import reverse

        from core.utils import is_agent_government, is_agent_partenaire

        # Check user role and redirect accordingly
        if user.is_superuser or user.is_staff:
            # Admin users should use admin login
            return reverse("administration:dashboard")
        elif is_agent_partenaire(user):
            # Agent Partenaire -> Cash Dashboard
            return reverse("payments:cash_dashboard")
        elif is_agent_government(user):
            # Agent Gouvernement -> QR Verification Dashboard
            return reverse("payments:qr_verification_dashboard")
        elif hasattr(user, "profile"):
            user_type = user.profile.user_type
            if user_type in ["company", "public_institution", "international_organization"]:
                # Fleet managers -> Fleet Dashboard
                return reverse("core:fleet_dashboard")

        # Regular clients (individual) -> Main Dashboard
        return reverse("core:velzon_dashboard")
