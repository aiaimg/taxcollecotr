"""
Context processors for the core app
"""

from core.utils import is_agent_government, is_agent_partenaire
from django.conf import settings
from allauth.socialaccount.models import SocialApp


def user_role_context(request):
    """
    Add comprehensive user role information to template context
    """
    context = {
        "is_admin_user": False,
        "is_superuser": False,
        "user_type": None,
        "user_role": None,
        "is_agent_partenaire": False,
        "is_agent_government": False,
        "is_any_agent": False,
        "user_role_display": None,
        "admin_permissions": {
            "can_manage_users": False,
            "can_manage_vehicles": False,
            "can_manage_payments": False,
            "can_manage_agents": False,
            "can_view_analytics": False,
            "can_manage_finance": False,
        },
    }

    if request.user.is_authenticated:
        user = request.user

        # Basic admin checks
        context["is_superuser"] = user.is_superuser
        context["is_admin_user"] = user.is_staff or user.is_superuser

        # Get user type from profile if available
        if hasattr(user, "profile"):
            context["user_type"] = user.profile.user_type
        else:
            context["user_type"] = "individual"  # Default

        # Check agent types
        context["is_agent_partenaire"] = is_agent_partenaire(user)
        context["is_agent_government"] = is_agent_government(user)
        context["is_any_agent"] = context["is_agent_partenaire"] or context["is_agent_government"]

        # Determine user role (prioritize agent roles over admin)
        # Agents can have is_staff=True but should be treated as agents first
        if context["is_agent_partenaire"]:
            context["user_role"] = "agent_partenaire"
            context["user_role_display"] = "Agent Partenaire"
        elif context["is_agent_government"]:
            context["user_role"] = "agent_government"
            context["user_role_display"] = "Agent Gouvernement"
        elif context["is_superuser"]:
            context["user_role"] = "super_admin"
            context["user_role_display"] = "Super Administrateur"
            # Superuser has all permissions
            context["admin_permissions"] = {
                "can_manage_users": True,
                "can_manage_vehicles": True,
                "can_manage_payments": True,
                "can_manage_agents": True,
                "can_view_analytics": True,
                "can_manage_finance": True,
            }
        elif context["is_admin_user"]:
            context["user_role"] = "admin"
            context["user_role_display"] = "Administrateur"
            # Check admin permissions based on groups
            # For now, staff users have basic admin permissions
            # This can be enhanced with Django groups/permissions later
            context["admin_permissions"] = {
                "can_manage_users": user.has_perm("auth.change_user") or user.is_staff,
                "can_manage_vehicles": user.has_perm("vehicles.change_vehicule") or user.is_staff,
                "can_manage_payments": user.has_perm("payments.change_paiementtaxe") or user.is_staff,
                "can_manage_agents": user.has_perm("payments.change_agentpartenaireprofile") or user.is_staff,
                "can_view_analytics": user.is_staff,
                "can_manage_finance": user.has_perm("payments.change_paiementtaxe") or user.is_staff,
            }
        elif context["user_type"] == "company":
            context["user_role"] = "company"
            context["user_role_display"] = "Entreprise"
        else:
            context["user_role"] = "client"
            context["user_role_display"] = "Client"

    return context


def oauth_context(request):
    configured = bool(getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "") and getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", ""))
    if not configured:
        configured = SocialApp.objects.filter(provider="google", client_id__gt="", secret__gt="").exists()
    return {
        "GOOGLE_OAUTH_CONFIGURED": configured,
    }
