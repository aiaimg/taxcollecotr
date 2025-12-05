"""
Custom decorators for administration views
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from core.utils import is_agent_government, is_agent_partenaire

from .mixins import is_admin_user


def admin_required(view_func):
    """
    Decorator that checks if user is an admin (excluding agents).
    Redirects agents to their appropriate dashboards.
    """

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("administration:admin_login")

        # Check if user is an agent first
        if is_agent_partenaire(request.user):
            messages.error(request, _("Accès refusé. Cette section est réservée aux administrateurs."))
            return redirect("payments:cash_dashboard")
        elif is_agent_government(request.user):
            messages.error(request, _("Accès refusé. Cette section est réservée aux administrateurs."))
            return redirect("payments:qr_verification_dashboard")

        # Check if user is admin
        if not is_admin_user(request.user):
            messages.error(request, _("Accès refusé. Seuls les administrateurs peuvent accéder à cette section."))
            return redirect("administration:admin_login")

        return view_func(request, *args, **kwargs)

    return wrapped_view
