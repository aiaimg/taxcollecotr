"""
Custom Permissions for API
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        if hasattr(obj, "proprietaire"):
            return obj.proprietaire == request.user
        elif hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "vehicule_plaque"):
            return obj.vehicule_plaque.proprietaire == request.user

        return False


class IsAdminOrReadOnly(BasePermission):
    """
    Permission that allows admin users to edit, others can only read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsVerifiedUser(BasePermission):
    """
    Permission that requires user to be verified.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has a profile and is verified
        if hasattr(request.user, "profile"):
            return request.user.profile.is_verified

        # Allow if user is staff/admin
        return request.user.is_staff or request.user.is_superuser


class IsOwner(BasePermission):
    """
    Permission that only allows owners to access the object.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "proprietaire"):
            return obj.proprietaire == request.user
        elif hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "vehicule_plaque"):
            return obj.vehicule_plaque.proprietaire == request.user

        return False
