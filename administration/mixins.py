from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from core.models import UserProfile
from core.utils import is_agent_government, is_agent_partenaire, is_any_agent


def is_admin_user(user):
    """Check if user is an admin (excluding agents)"""
    if not user.is_authenticated:
        return False

    # IMPORTANT: Agents should NOT be considered admins, even if they have is_staff=True
    # Check if user is an agent first - if so, they are NOT an admin
    if is_agent_partenaire(user) or is_agent_government(user):
        return False

    # Check if user is superuser (superusers are always admins)
    if user.is_superuser:
        return True

    # Check if user is staff (but not an agent - already checked above)
    if user.is_staff:
        return True

    # Note: Admin access is determined by is_staff or is_superuser flags
    # User types (public_institution, etc.) do not automatically grant admin access
    # Only staff users and superusers are admins
    pass

    return False


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires user to be an admin.
    Redirects to admin login page if not authenticated or not admin.
    """

    login_url = reverse_lazy("administration:admin_login")

    def test_func(self):
        """Test if user is an admin"""
        return is_admin_user(self.request.user)

    def handle_no_permission(self):
        """Handle cases where user doesn't have permission"""
        if not self.request.user.is_authenticated:
            # User not logged in - redirect to admin login
            return redirect(self.get_login_url())
        else:
            user = self.request.user

            # Check if user is an agent and redirect to appropriate dashboard
            if is_agent_partenaire(user):
                messages.error(self.request, _("Accès refusé. Cette section est réservée aux administrateurs."))
                return redirect("payments:cash_dashboard")
            elif is_agent_government(user):
                messages.error(self.request, _("Accès refusé. Cette section est réservée aux administrateurs."))
                return redirect("payments:qr_verification_dashboard")
            else:
                # Regular user (not admin, not agent) - show error and redirect to admin login
                messages.error(
                    self.request, _("Accès refusé. Seuls les administrateurs peuvent accéder à cette section.")
                )
                # Don't log out - just redirect to login
                return redirect("administration:admin_login")

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to handle admin access control"""
        if not request.user.is_authenticated:
            return redirect("administration:admin_login")

        if not is_admin_user(request.user):
            user = request.user

            # Check if user is an agent and redirect to appropriate dashboard
            if is_agent_partenaire(user):
                messages.error(request, _("Accès refusé. Cette section est réservée aux administrateurs."))
                return redirect("payments:cash_dashboard")
            elif is_agent_government(user):
                messages.error(request, _("Accès refusé. Cette section est réservée aux administrateurs."))
                return redirect("payments:qr_verification_dashboard")
            else:
                # Regular user (not admin, not agent) - show error
                messages.error(request, _("Accès refusé. Seuls les administrateurs peuvent accéder à cette section."))
                return redirect("administration:admin_login")

        return super().dispatch(request, *args, **kwargs)


class AdminLoginRequiredMixin(LoginRequiredMixin):
    """
    Simple mixin that just redirects to admin login if not authenticated.
    Use this for views that don't need the full admin check.
    """

    login_url = reverse_lazy("administration:admin_login")


class AgentPartenaireRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires user to be an active Agent Partenaire.
    Redirects to login page if not authenticated or not an agent partenaire.
    """

    login_url = reverse_lazy("administration:agent_partenaire_login")

    def test_func(self):
        """Test if user is an active Agent Partenaire"""
        return is_agent_partenaire(self.request.user)

    def handle_no_permission(self):
        """Handle cases where user doesn't have permission"""
        if not self.request.user.is_authenticated:
            return redirect(self.get_login_url())
        else:
            messages.error(
                self.request, _("Accès refusé. Vous devez être un Agent Partenaire actif pour accéder à cette section.")
            )
            return redirect("core:dashboard")

    def get_agent_profile(self):
        """Get the agent partenaire profile for the current user"""
        if is_agent_partenaire(self.request.user):
            return self.request.user.agent_partenaire_profile
        return None


class AgentGovernmentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires user to be an active Agent Gouvernement.
    Redirects to login page if not authenticated or not an agent government.
    """

    login_url = reverse_lazy("administration:agent_government_login")

    def test_func(self):
        """Test if user is an active Agent Gouvernement"""
        return is_agent_government(self.request.user)

    def handle_no_permission(self):
        """Handle cases where user doesn't have permission"""
        if not self.request.user.is_authenticated:
            return redirect(self.get_login_url())
        else:
            messages.error(
                self.request,
                _("Accès refusé. Vous devez être un Agent Gouvernement actif pour accéder à cette section."),
            )
            return redirect("core:dashboard")

    def get_agent_profile(self):
        """Get the agent government profile for the current user"""
        if is_agent_government(self.request.user):
            return self.request.user.agent_verification
        return None


class AnyAgentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires user to be any type of agent (partenaire or government).
    Redirects to login page if not authenticated or not an agent.
    """

    login_url = reverse_lazy("core:login")

    def test_func(self):
        """Test if user is any type of agent"""
        return is_any_agent(self.request.user)

    def handle_no_permission(self):
        """Handle cases where user doesn't have permission"""
        if not self.request.user.is_authenticated:
            return redirect(self.get_login_url())
        else:
            messages.error(self.request, _("Accès refusé. Vous devez être un agent pour accéder à cette section."))
            return redirect("core:dashboard")
