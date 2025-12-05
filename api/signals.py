from typing import Any
from datetime import date, datetime
from decimal import Decimal
import uuid

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete
import sys
from django.dispatch import receiver
from django.db import connection
from django.db.models.fields.files import FieldFile

from api.models import DataChangeLog, APIAuditLog, APIVersion
from api.utils.masking import mask_payload


def _instance_to_dict(instance) -> dict:
    data = {}
    for field in instance._meta.fields:
        key = field.attname
        try:
            val = getattr(instance, key)
            if isinstance(val, (datetime, date)):
                data[key] = val.isoformat()
            elif isinstance(val, Decimal):
                data[key] = float(val)
            elif isinstance(val, uuid.UUID):
                data[key] = str(val)
            elif isinstance(val, FieldFile):
                data[key] = val.name or None
            else:
                data[key] = val
        except Exception:
            pass
    return data


def _should_skip(sender: Any) -> bool:
    return sender in {DataChangeLog, APIAuditLog}


def _logging_available() -> bool:
    try:
        return DataChangeLog._meta.db_table in connection.introspection.table_names()
    except Exception:
        return False


@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    if _should_skip(sender) or ('migrate' in sys.argv) or (not _logging_available()):
        return

    try:
        ct = ContentType.objects.get_for_model(sender)
        new_data = _instance_to_dict(instance)
        previous_data = getattr(instance, "_pre_save_previous", {})
        changed_fields = getattr(instance, "_pre_save_changed", [])

        DataChangeLog.objects.create(
            content_type=ct,
            object_id=str(instance.pk),
            object_repr=str(instance),
            operation=DataChangeLog.OP_CREATE if created else DataChangeLog.OP_UPDATE,
            changed_fields=changed_fields,
            previous_data=mask_payload(previous_data),
            new_data=mask_payload(new_data),
        )
    except Exception:
        pass


@receiver(post_save, sender=APIVersion)
def notify_api_version(sender, instance: APIVersion, created, **kwargs):
    try:
        if not created:
            return
        from administration.email_utils import send_email
        recipients = []
        if instance.notify_emails:
            recipients = instance.notify_emails
        else:
            from django.contrib.auth.models import User
            recipients = list(User.objects.filter(is_superuser=True, is_active=True).exclude(email="").values_list("email", flat=True))
        if not recipients:
            return
        subject = f"TaxCollector API v{instance.version} released"
        message = (
            f"Version: {instance.version}\n"
            f"Released at: {instance.released_at.isoformat()}\n"
            f"Summary: {instance.summary}\n"
            f"Changes:\n" + "\n".join(f"- {c}" for c in (instance.changes or []))
        )
        send_email(subject=subject, message=message, recipient_list=recipients, html_message=None, email_type="api_changelog")
    except Exception:
        pass


@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    if _should_skip(sender) or ('migrate' in sys.argv) or (not _logging_available()):
        return
    try:
        ct = ContentType.objects.get_for_model(sender)
        DataChangeLog.objects.create(
            content_type=ct,
            object_id=str(instance.pk),
            object_repr=str(instance),
            operation=DataChangeLog.OP_DELETE,
            previous_data=mask_payload(_instance_to_dict(instance)),
            new_data={},
        )
    except Exception:
        pass


@receiver(pre_save)
def capture_pre_save(sender, instance, **kwargs):
    if _should_skip(sender) or ('migrate' in sys.argv) or (not _logging_available()):
        return
    try:
        if instance.pk:
            try:
                old = sender.objects.get(pk=instance.pk)
                old_data = _instance_to_dict(old)
                new_data = _instance_to_dict(instance)
                changed = [k for k in new_data.keys() if old_data.get(k) != new_data.get(k)]
                instance._pre_save_previous = old_data
                instance._pre_save_changed = changed
            except sender.DoesNotExist:
                instance._pre_save_previous = {}
                instance._pre_save_changed = []
        else:
            instance._pre_save_previous = {}
            instance._pre_save_changed = []
    except Exception:
        pass
