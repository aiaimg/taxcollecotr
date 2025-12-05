from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient


class APIKeyRateLimitTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from api.models import APIKey
        self.key = APIKey.objects.create(
            key=APIKey.generate_key(),
            name="RL Test",
            organization="Org",
            contact_email="rl@example.com",
            is_active=True,
            rate_limit_per_hour=1,
            rate_limit_per_day=1000,
        )

    def test_per_api_key_rate_limit_enforced_with_headers_and_audit(self):
        self.client.credentials(HTTP_X_API_KEY=self.key.key)
        r1 = self.client.get("/api/v1/throttled/")
        self.assertEqual(r1.status_code, 200)
        # First request allowed

        r2 = self.client.get("/api/v1/throttled/")
        self.assertEqual(r2.status_code, 429)
        self.assertEqual(r2.get("Content-Type"), "application/problem+json")
        body = r2.json()
        self.assertEqual(body.get("code"), "rate_limit")
        self.assertIn("correlationId", body)

        # Audit log contains rate limit info
        from api.models import APIAuditLog
        cid = r2["X-Correlation-ID"]
        log = APIAuditLog.objects.filter(correlation_id=cid, endpoint="/api/v1/throttled/").first()
        self.assertIsNotNone(log)
        resp_body = log.response_body or {}
        self.assertEqual(resp_body.get("code"), "rate_limit")
