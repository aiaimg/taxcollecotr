import hashlib
import hmac
import json
from typing import Dict

from django.utils import timezone

from api.models import WebhookSubscription, WebhookDelivery
from api.tasks import deliver_webhook_event


def generate_signature(secret: str, body_bytes: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()


def dispatch_webhook_event(event_type: str, payload: Dict):
    now = timezone.now()
    subs = WebhookSubscription.objects.filter(is_active=True)
    for sub in subs:
        if sub.event_types and event_type not in sub.event_types:
            continue

        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        signature = generate_signature(sub.secret, body)

        delivery = WebhookDelivery.objects.create(
            subscription=sub,
            event_type=event_type,
            payload=payload,
            signature=signature,
            status=WebhookDelivery.STATUS_PENDING,
            attempt_count=0,
            next_attempt_at=now,
        )

        deliver_webhook_event.delay(str(delivery.id))


def verify_signature(secret: str, body_bytes: bytes, signature: str) -> bool:
    return hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest() == signature
