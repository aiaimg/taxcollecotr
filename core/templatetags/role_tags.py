"""
Template tags for role detection and permission checks
"""

from django import template

from core.utils import is_agent_government, is_agent_partenaire, is_any_agent

register = template.Library()


@register.filter
def is_agent_partenaire_user(user):
    """Check if user is an Agent Partenaire"""
    if not user or not user.is_authenticated:
        return False
    return is_agent_partenaire(user)


@register.filter
def is_agent_government_user(user):
    """Check if user is an Agent Gouvernement"""
    if not user or not user.is_authenticated:
        return False
    return is_agent_government(user)


@register.filter
def is_any_agent_user(user):
    """Check if user is any type of agent"""
    if not user or not user.is_authenticated:
        return False
    return is_any_agent(user)


@register.filter
def has_admin_permission(user, permission):
    """Check if user has a specific admin permission"""
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not user.is_staff:
        return False

    # Map permission names to Django permissions
    permission_map = {
        "manage_users": "auth.change_user",
        "manage_vehicles": "vehicles.change_vehicule",
        "manage_payments": "payments.change_paiementtaxe",
        "manage_agents": "payments.change_agentpartenaireprofile",
        "view_analytics": True,  # Staff can view analytics
        "manage_finance": "payments.change_paiementtaxe",
    }

    django_permission = permission_map.get(permission)
    if django_permission is True:
        return user.is_staff
    elif django_permission:
        return user.has_perm(django_permission)

    return False


@register.filter
def get_user_role_display(user):
    """Get human-readable role name for user"""
    if not user or not user.is_authenticated:
        return "Non connecté"

    if user.is_superuser:
        return "Super Administrateur"
    elif user.is_staff:
        return "Administrateur"
    elif is_agent_partenaire(user):
        return "Agent Partenaire"
    elif is_agent_government(user):
        return "Agent Gouvernement"
    elif hasattr(user, "profile"):
        user_type = user.profile.user_type
        if user_type == "company":
            return "Entreprise"
        elif user_type == "public_institution":
            return "Administration Publique"
        elif user_type == "international_organization":
            return "Organisation Internationale"
        else:
            return "Client"

    return "Client"
