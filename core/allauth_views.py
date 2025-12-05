from django.contrib import messages
from django.contrib.auth import authenticate
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from allauth.account.utils import get_next_redirect_url
from allauth.account.views import LoginView as AllauthLoginView


def is_admin_user(user):
    """Check if user is admin or staff"""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or hasattr(user, "adminuserprofile")


class CustomAllauthLoginView(AllauthLoginView):
    """Custom allauth login view that excludes admin users"""

    def form_valid(self, form):
        """Override form validation to exclude admin users"""
        # Get the credentials from the form
        login = form.cleaned_data.get("login")
        password = form.cleaned_data.get("password")

        # Try to authenticate the user
        user = authenticate(self.request, email=login, password=password)
        if not user:
            # Try with username if email authentication fails
            user = authenticate(self.request, username=login, password=password)

        if user is not None:
            # Check if user is an admin
            if is_admin_user(user):
                # Add error message and return form as invalid
                form.add_error(None, _("Utilisateur non trouvé. Veuillez vérifier vos identifiants."))
                return self.form_invalid(form)

        # Proceed with normal allauth login process
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect based on user role after login"""
        ret = get_next_redirect_url(self.request, None)
        if ret:
            return ret

        user = self.request.user

        # Import agent utilities
        from core.utils import is_agent_government, is_agent_partenaire

        # Check user role and redirect accordingly
        if user.is_superuser or user.is_staff:
            # Admin users should use admin login
            return reverse_lazy("administration:dashboard")
        elif is_agent_partenaire(user):
            # Agent Partenaire -> Cash Dashboard
            return reverse_lazy("payments:cash_dashboard")
        elif is_agent_government(user):
            # Agent Gouvernement -> QR Verification Dashboard
            return reverse_lazy("payments:qr_verification_dashboard")
        elif hasattr(user, "profile"):
            user_type = user.profile.user_type
            if user_type in ["company", "public_institution", "international_organization"]:
                # Fleet managers -> Fleet Dashboard
                return reverse_lazy("core:fleet_dashboard")

        # Regular clients (individual) -> Main Dashboard
        return reverse_lazy("core:velzon_dashboard")
