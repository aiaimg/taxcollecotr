"""
Utility functions for agent authentication and authorization
"""

from django.contrib.auth import get_user_model

User = get_user_model()


def is_agent_partenaire(user):
    """
    Check if user is an active Agent Partenaire

    Args:
        user: User instance

    Returns:
        bool: True if user is an active Agent Partenaire, False otherwise
    """
    if not user or not user.is_authenticated:
        return False

    return hasattr(user, "agent_partenaire_profile") and user.agent_partenaire_profile.is_active


def is_agent_government(user):
    """
    Check if user is an active Agent Gouvernement (verification agent)

    Args:
        user: User instance

    Returns:
        bool: True if user is an active Agent Gouvernement, False otherwise
    """
    if not user or not user.is_authenticated:
        return False

    return hasattr(user, "agent_verification") and user.agent_verification.est_actif


def is_any_agent(user):
    """
    Check if user is any type of agent (partenaire or government)

    Args:
        user: User instance

    Returns:
        bool: True if user is any type of agent, False otherwise
    """
    return is_agent_partenaire(user) or is_agent_government(user)


def get_agent_partenaire_profile(user):
    """
    Get Agent Partenaire profile for user

    Args:
        user: User instance

    Returns:
        AgentPartenaireProfile or None
    """
    if is_agent_partenaire(user):
        return user.agent_partenaire_profile
    return None


def get_agent_government_profile(user):
    """
    Get Agent Gouvernement profile for user

    Args:
        user: User instance

    Returns:
        AgentVerification or None
    """
    if is_agent_government(user):
        return user.agent_verification
    return None
