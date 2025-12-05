"""
Permission decorators for cash payment system
Provides function-based view decorators for role checking
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.translation import gettext as _


def agent_partenaire_required(view_func):
    """
    Decorator to ensure user is an active Agent Partenaire

    Checks:
    1. User is authenticated
    2. User has an active AgentPartenaireProfile
    3. User is in "Agent Partenaire" group OR is staff/superuser

    Usage:
        @agent_partenaire_required
        def my_view(request):
            # View code here
            pass
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Check if user has agent partenaire profile and is active
        has_profile = hasattr(user, "agent_partenaire_profile") and user.agent_partenaire_profile.is_active

        if not has_profile:
            messages.error(request, _("Vous devez être un Agent Partenaire actif pour accéder à cette page."))
            return redirect("core:dashboard")

        # Check if user is in Agent Partenaire group or is staff/superuser
        is_in_group = user.groups.filter(name="Agent Partenaire").exists()
        is_admin = user.is_staff or user.is_superuser

        if not (is_in_group or is_admin):
            messages.error(request, _("Vous n'avez pas les permissions nécessaires pour accéder à cette page."))
            return redirect("core:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_staff_required(view_func):
    """
    Decorator to ensure user is admin staff

    Checks:
    1. User is authenticated
    2. User is staff or superuser
    3. User is in "Admin Staff" group OR is superuser

    Usage:
        @admin_staff_required
        def my_view(request):
            # View code here
            pass
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Superusers always have access
        if user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if user is staff
        if not user.is_staff:
            messages.error(request, _("Vous devez être un administrateur pour accéder à cette page."))
            return redirect("core:dashboard")

        # Check if user is in Admin Staff group
        is_in_group = user.groups.filter(name="Admin Staff").exists()

        if not is_in_group:
            messages.error(request, _("Vous n'avez pas les permissions nécessaires pour accéder à cette page."))
            return redirect("core:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


def agent_partenaire_or_admin_required(view_func):
    """
    Decorator to ensure user is either an Agent Partenaire or Admin Staff

    Useful for views that both roles can access (e.g., viewing receipts)

    Usage:
        @agent_partenaire_or_admin_required
        def my_view(request):
            # View code here
            pass
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Superusers always have access
        if user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if user is admin staff
        is_admin = user.is_staff and user.groups.filter(name="Admin Staff").exists()

        # Check if user is agent partenaire
        is_agent = (
            hasattr(user, "agent_partenaire_profile")
            and user.agent_partenaire_profile.is_active
            and user.groups.filter(name="Agent Partenaire").exists()
        )

        if not (is_admin or is_agent):
            messages.error(
                request, _("Vous devez être un Agent Partenaire ou un administrateur pour accéder à cette page.")
            )
            return redirect("core:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper
