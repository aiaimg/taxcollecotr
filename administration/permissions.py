"""
Permission classes for agent authentication and authorization
"""

from rest_framework import permissions

from core.utils import is_agent_government, is_agent_partenaire, is_any_agent


class IsAgentPartenaire(permissions.BasePermission):
    """
    Permission class for Agent Partenaire
    Allows access only to users who are active Agent Partenaire
    """

    def has_permission(self, request, view):
        """Check if user is an active Agent Partenaire"""
        return is_agent_partenaire(request.user)


class IsAgentGovernment(permissions.BasePermission):
    """
    Permission class for Agent Gouvernement
    Allows access only to users who are active Agent Gouvernement (verification agents)
    """

    def has_permission(self, request, view):
        """Check if user is an active Agent Gouvernement"""
        return is_agent_government(request.user)


class IsAnyAgent(permissions.BasePermission):
    """
    Permission class for any type of agent
    Allows access to users who are either Agent Partenaire or Agent Gouvernement
    """

    def has_permission(self, request, view):
        """Check if user is any type of agent"""
        return is_any_agent(request.user)


class IsAgentPartenaireOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to everyone,
    but write access only to Agent Partenaire
    """

    def has_permission(self, request, view):
        """Check permissions based on request method"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_agent_partenaire(request.user)


class IsAgentGovernmentOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to everyone,
    but write access only to Agent Gouvernement
    """

    def has_permission(self, request, view):
        """Check permissions based on request method"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_agent_government(request.user)
