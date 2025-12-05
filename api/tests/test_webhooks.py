import json
import time
from datetime import timedelta
from unittest.mock import patch, Mock

from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save
from django.utils import timezone

from api.models import WebhookSubscription, WebhookDelivery
from api.utils.webhooks import generate_signature, dispatch_webhook_event
from api.tasks import deliver_webhook_event


class WebhookSignaturePropertyTest(TestCase):
    """
    Property 36: Webhook HMAC Signature
    Validates: Requirements 15.3
    """

    def test_signature_hmac_sha256(self):
        secret = "testsecret"
        payload = {"a": 1, "b": 2}
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        sig = generate_signature(secret, body)
        import hashlib, hmac

        expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        self.assertEqual(sig, expected)


class WebhookEventDeliveryPropertyTest(TestCase):
    """
    Property 21: Webhook Event Delivery
    Validates: Requirements 8.3
    """

    def setUp(self):
        from notifications.signals import create_welcome_notification
        from api.signals import log_post_save, log_post_delete, capture_pre_save
        post_save.disconnect(create_welcome_notification, sender=User)
        post_save.disconnect(log_post_save)
        post_delete.disconnect(log_post_delete)
        pre_save.disconnect(capture_pre_save)

        self.user = User.objects.create_user(username="admin", password="pass")
        self.sub = WebhookSubscription.objects.create(
            name="Test",
            target_url="http://example.com/webhook",
            is_active=True,
            event_types=["test.event"],
            secret="secret123",
            created_by=self.user,
        )

    @patch("api.utils.webhooks.deliver_webhook_event.delay")
    def test_dispatch_creates_delivery(self, mock_delay):
        payload = {"hello": "world"}
        dispatch_webhook_event("test.event", payload)
        deliveries = WebhookDelivery.objects.filter(subscription=self.sub, event_type="test.event")
        self.assertGreaterEqual(deliveries.count(), 1)
        d = deliveries.latest("created_at")
        self.assertEqual(d.status, WebhookDelivery.STATUS_PENDING)
        self.assertIsInstance(d.signature, str)

    def tearDown(self):
        from notifications.signals import create_welcome_notification
        from api.signals import log_post_save, log_post_delete, capture_pre_save
        post_save.connect(create_welcome_notification, sender=User)
        post_save.connect(log_post_save)
        post_delete.connect(log_post_delete)
        pre_save.connect(capture_pre_save)


class WebhookRetryBackoffPropertyTest(TestCase):
    """
    Property 37: Webhook Retry with Exponential Backoff
    Validates: Requirements 15.4
    """

    def setUp(self):
        from notifications.signals import create_welcome_notification
        from api.signals import log_post_save, log_post_delete, capture_pre_save
        post_save.disconnect(create_welcome_notification, sender=User)
        post_save.disconnect(log_post_save)
        post_delete.disconnect(log_post_delete)
        pre_save.disconnect(capture_pre_save)

        self.user = User.objects.create_user(username="admin2", password="pass")
        self.sub = WebhookSubscription.objects.create(
            name="Test2",
            target_url="http://example.com/webhook",
            is_active=True,
            event_types=["test.event"],
            secret="secret456",
            created_by=self.user,
        )

    @patch("api.tasks.requests.post")
    def test_retry_exponential_backoff(self, mock_post):
        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_resp.text = "error"
        mock_post.return_value = mock_resp

        payload = {"k": "v"}
        dispatch_webhook_event("test.event", payload)
        d = WebhookDelivery.objects.filter(subscription=self.sub).latest("created_at")

        # First attempt
        deliver_webhook_event(str(d.id))
        d.refresh_from_db()
        self.assertEqual(d.attempt_count, 1)
        self.assertEqual(d.status, WebhookDelivery.STATUS_FAILED)
        self.assertIsNotNone(d.next_attempt_at)
        self.assertAlmostEqual(
            (d.next_attempt_at - timezone.now()).total_seconds(),
            5,
            delta=2,
        )

        # Second attempt
        deliver_webhook_event(str(d.id))
        d.refresh_from_db()
        self.assertEqual(d.attempt_count, 2)
        self.assertEqual(d.status, WebhookDelivery.STATUS_FAILED)
        self.assertAlmostEqual(
            (d.next_attempt_at - timezone.now()).total_seconds(),
            30,
            delta=3,
        )

    def tearDown(self):
        from notifications.signals import create_welcome_notification
        from api.signals import log_post_save, log_post_delete, capture_pre_save
        post_save.connect(create_welcome_notification, sender=User)
        post_save.connect(log_post_save)
        post_delete.connect(log_post_delete)
        pre_save.connect(capture_pre_save)
