from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from core.models import UserProfile
from core.utils import is_agent_government, is_agent_partenaire


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


class AdminLoginView(auth_views.LoginView):
    """Custom admin login view with admin-specific validation"""

    template_name = "administration/auth/admin_login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("administration:dashboard")

    def form_valid(self, form):
        """Validate that the user is an admin before logging in"""
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            if is_admin_user(user):
                login(self.request, user)
                messages.success(self.request, _("Connexion administrateur réussie"))
                return redirect(self.get_success_url())
            else:
                messages.error(
                    self.request, _("Accès refusé. Seuls les administrateurs peuvent accéder à cette section.")
                )
                return self.form_invalid(form)
        else:
            messages.error(self.request, _("Nom d'utilisateur ou mot de passe incorrect"))
            return self.form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        """Redirect already authenticated admin users"""
        if request.user.is_authenticated and is_admin_user(request.user):
            return redirect(self.get_success_url())
        elif request.user.is_authenticated and not is_admin_user(request.user):
            messages.warning(request, _("Vous devez vous connecter avec un compte administrateur"))
            # Log out the non-admin user
            from django.contrib.auth import logout

            logout(request)

        return super().dispatch(request, *args, **kwargs)


class AdminLogoutView(LoginRequiredMixin, TemplateView):
    """Custom admin logout view"""

    template_name = "administration/auth/admin_logout.html"

    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout

        logout(request)
        messages.success(request, _("Déconnexion administrateur réussie"))
        return render(request, self.template_name)


@login_required
def admin_required_view(request):
    """View to check admin access and redirect appropriately"""
    if is_admin_user(request.user):
        return redirect("administration:dashboard")
    else:
        messages.error(request, _("Accès refusé. Seuls les administrateurs peuvent accéder à cette section."))
        return redirect("administration:admin_login")


class AgentPartenaireLoginView(auth_views.LoginView):
    """Login view for Agent Partenaire"""

    template_name = "administration/auth/agent_partenaire_login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        # Redirect to cash session management or dashboard
        try:
            from payments.cash_views import CashSessionService

            agent = self.request.user.agent_partenaire_profile
            active_session = CashSessionService.get_active_session(agent)
            if active_session:
                return reverse_lazy("payments:cash_session_detail", kwargs={"pk": active_session.id})
        except (ImportError, AttributeError):
            pass
        # Fallback to cash session open page
        return reverse_lazy("payments:cash_session_open")

    def form_valid(self, form):
        """Validate that the user is an active Agent Partenaire before logging in"""
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            if is_agent_partenaire(user):
                login(self.request, user)
                messages.success(self.request, _("Connexion Agent Partenaire réussie"))
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, _("Accès refusé. Ce compte n'est pas un Agent Partenaire actif."))
                return self.form_invalid(form)
        else:
            messages.error(self.request, _("Nom d'utilisateur ou mot de passe incorrect"))
            return self.form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        """Redirect already authenticated agent partenaire users"""
        if request.user.is_authenticated and is_agent_partenaire(request.user):
            return redirect(self.get_success_url())
        elif request.user.is_authenticated and not is_agent_partenaire(request.user):
            messages.warning(request, _("Vous devez vous connecter avec un compte Agent Partenaire"))
            from django.contrib.auth import logout

            logout(request)

        return super().dispatch(request, *args, **kwargs)


class AgentGovernmentLoginView(auth_views.LoginView):
    """Login view for Agent Gouvernement (verification agents)"""

    template_name = "administration/auth/agent_government_login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        # Redirect to QR verification dashboard
        return reverse_lazy("payments:qr_verification_dashboard")

    def form_valid(self, form):
        """Validate that the user is an active Agent Gouvernement before logging in"""
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            if is_agent_government(user):
                login(self.request, user)
                messages.success(self.request, _("Connexion Agent Gouvernement réussie"))
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, _("Accès refusé. Ce compte n'est pas un Agent Gouvernement actif."))
                return self.form_invalid(form)
        else:
            messages.error(self.request, _("Nom d'utilisateur ou mot de passe incorrect"))
            return self.form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        """Redirect already authenticated agent government users"""
        if request.user.is_authenticated and is_agent_government(request.user):
            return redirect(self.get_success_url())
        elif request.user.is_authenticated and not is_agent_government(request.user):
            messages.warning(request, _("Vous devez vous connecter avec un compte Agent Gouvernement"))
            from django.contrib.auth import logout

            logout(request)

        return super().dispatch(request, *args, **kwargs)
