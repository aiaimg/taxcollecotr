import csv
import os
import json
import time
from datetime import datetime, timedelta
import hashlib
import hmac

import requests

from celery import shared_task
from django.conf import settings
from django.db.models import Count

from django.utils import timezone

from api.models import APIAuditLog, WebhookDelivery


BACKOFF_SCHEDULE = [5, 30, 120]


def _compute_signature(secret: str, body_bytes: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()


@shared_task(bind=True)
def deliver_webhook_event(self, delivery_id: str):
    try:
        delivery = WebhookDelivery.objects.select_related("subscription").get(id=delivery_id)
    except WebhookDelivery.DoesNotExist:
        return

    sub = delivery.subscription
    url = sub.target_url
    body_bytes = json.dumps(delivery.payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = _compute_signature(sub.secret, body_bytes)

    # Update signature in case payload changed
    if delivery.signature != signature:
        delivery.signature = signature
        delivery.save(update_fields=["signature"])

    headers = {
        "Content-Type": "application/json",
        "X-TC-Signature": signature,
        "X-TC-Event": delivery.event_type,
        "X-TC-Timestamp": str(int(time.time())),
    }

    try:
        resp = requests.post(url, data=body_bytes, headers=headers, timeout=10)
        delivery.response_code = resp.status_code
        # Avoid logging huge bodies
        delivery.response_body = resp.text[:4000] if resp.text else ""
        delivery.attempt_count = (delivery.attempt_count or 0) + 1

        if 200 <= resp.status_code < 300:
            delivery.status = WebhookDelivery.STATUS_SUCCESS
            delivery.error_message = ""
            delivery.next_attempt_at = None
        else:
            delivery.status = WebhookDelivery.STATUS_FAILED
            delivery.error_message = f"HTTP {resp.status_code}"
            # Schedule retry if attempts remain
            attempts = delivery.attempt_count
            if attempts < 3:
                delay = BACKOFF_SCHEDULE[min(attempts - 1, len(BACKOFF_SCHEDULE) - 1)]
                delivery.next_attempt_at = timezone.now() + timedelta(seconds=delay)
                delivery.save()
                deliver_webhook_event.apply_async(args=[delivery_id], countdown=delay)
                return
        delivery.save()
    except Exception as e:
        delivery.attempt_count = (delivery.attempt_count or 0) + 1
        delivery.status = WebhookDelivery.STATUS_FAILED
        delivery.error_message = str(e)[:2000]
        attempts = delivery.attempt_count
        if attempts < 3:
            delay = BACKOFF_SCHEDULE[min(attempts - 1, len(BACKOFF_SCHEDULE) - 1)]
            delivery.next_attempt_at = timezone.now() + timedelta(seconds=delay)
            delivery.save()
            deliver_webhook_event.apply_async(args=[delivery_id], countdown=delay)
            return
        delivery.next_attempt_at = None
        delivery.save()


@shared_task
def generate_monthly_audit_report():
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)

    qs = APIAuditLog.objects.filter(
        timestamp__gte=first_day_last_month, timestamp__lte=last_day_last_month
    )

    by_endpoint = qs.values('endpoint').annotate(count=Count('id')).order_by('-count')
    by_status = qs.values('status_code').annotate(count=Count('id')).order_by('-count')
    by_api_key = qs.values('api_key__key').annotate(count=Count('id')).order_by('-count')

    reports_dir = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(reports_dir, exist_ok=True)
    filename = os.path.join(reports_dir, f"audit_report_{first_day_last_month.strftime('%Y_%m')}.csv")

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Section', 'Key', 'Count'])
        for row in by_endpoint:
            writer.writerow(['endpoint', row['endpoint'], row['count']])
        for row in by_status:
            writer.writerow(['status_code', row['status_code'], row['count']])
        for row in by_api_key:
            writer.writerow(['api_key', row['api_key__key'] or '', row['count']])


@shared_task
def purge_old_audit_logs():
    years = getattr(settings, 'AUDIT_LOG_RETENTION_YEARS', 3)
    cutoff = datetime.now() - timedelta(days=365 * years)
    APIAuditLog.objects.filter(timestamp__lt=cutoff).delete()
