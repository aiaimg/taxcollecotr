"""
Signal handlers for automatic notification creation
"""

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import NotificationService


@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    """
    Create welcome notification when a new user is created
    """
    if created:
        # Create UserProfile if it doesn't exist
        from core.models import UserProfile

        if not hasattr(instance, "profile"):
            # Get user_type from the request if available (set in RegisterView)
            user_type = getattr(instance, "_user_type", "individual")  # Default to individual
            UserProfile.objects.create(user=instance, user_type=user_type)

        # Get user's preferred language if profile exists
        langue = "fr"
        if hasattr(instance, "profile"):
            langue = instance.profile.langue_preferee

        # Create welcome notification
        NotificationService.create_welcome_notification(user=instance, langue=langue)


@receiver(user_logged_in)
def create_login_notification(sender, request, user, **kwargs):
    """
    Create notification when user logs in
    """
    # Get user's preferred language if profile exists
    langue = "fr"
    if hasattr(user, "profile"):
        langue = user.profile.langue_preferee

    # Create login notification
    NotificationService.create_login_notification(user=user, langue=langue)


@receiver(user_logged_out)
def create_logout_notification(sender, request, user, **kwargs):
    """
    Create notification when user logs out
    """
    if user:  # user might be None if anonymous
        # Get user's preferred language if profile exists
        langue = "fr"
        if hasattr(user, "profile"):
            langue = user.profile.langue_preferee

        # Create logout notification
        NotificationService.create_logout_notification(user=user, langue=langue)
