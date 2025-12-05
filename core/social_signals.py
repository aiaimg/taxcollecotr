import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.signals import social_account_added, social_account_removed

from .models import AuditLog, UserProfile


logger = logging.getLogger(__name__)


@receiver(social_account_added)
def handle_social_account_added(sender, request, sociallogin, **kwargs):
    user = sociallogin.user

    if not hasattr(user, "profile"):
        ctx = getattr(sociallogin, "state", {}) or {}
        user_type = ctx.get("registration_user_type")
        if user_type not in dict(UserProfile.USER_TYPE_CHOICES):
            user_type = "individual"
        UserProfile.objects.create(user=user, user_type=user_type)

    email = getattr(user, "email", None) or sociallogin.account.extra_data.get("email")
    if email:
        ea, _ = EmailAddress.objects.get_or_create(user=user, email=email)
        if sociallogin.account.provider == "google":
            ea.verified = True
            ea.primary = True
            ea.save()

    try:
        AuditLog.objects.create(
            user=user,
            action="CREATE",
            table_concernee="SocialAccount",
            objet_id=str(sociallogin.account.uid),
            donnees_apres=sociallogin.account.extra_data,
        )
    except Exception as e:
        logger.warning(f"Failed to write audit log for social_account_added: {e}")


@receiver(pre_delete, sender=SocialAccount)
def guard_social_account_unlink(sender, instance: SocialAccount, using, **kwargs):
    user = instance.user
    if not user.has_usable_password():
        raise PermissionDenied("Unlinking social account requires a usable password.")


@receiver(social_account_removed)
def handle_social_account_removed(sender, request, socialaccount, **kwargs):
    user = socialaccount.user
    try:
        AuditLog.objects.create(
            user=user,
            action="DELETE",
            table_concernee="SocialAccount",
            objet_id=str(socialaccount.uid),
            donnees_avant=socialaccount.extra_data,
        )
    except Exception as e:
        logger.warning(f"Failed to write audit log for social_account_removed: {e}")


@receiver(post_delete, sender=SocialAccount)
def log_social_account_post_delete(sender, instance: SocialAccount, using, **kwargs):
    try:
        AuditLog.objects.create(
            user=instance.user,
            action="DELETE",
            table_concernee="SocialAccount",
            objet_id=str(instance.uid),
            donnees_avant=instance.extra_data,
        )
    except Exception as e:
        logger.warning(f"Failed to write audit log in post_delete: {e}")
