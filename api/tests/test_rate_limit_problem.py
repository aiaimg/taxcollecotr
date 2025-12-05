from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient


class RateLimitProblemTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from api.models import APIKey
        key = APIKey.objects.create(key=APIKey.generate_key(), name="Test", organization="Org", contact_email="t@example.com", is_active=True, rate_limit_per_hour=1)
        self.client.credentials(HTTP_X_API_KEY=key.key)
        from django.core.cache import cache
        cache.clear()

    def test_rate_limit_returns_problem_details(self):
        r1 = self.client.get("/api/v1/throttled/")
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.get("/api/v1/throttled/")
        self.assertEqual(r2.status_code, 429)
        self.assertEqual(r2.get("Content-Type"), "application/problem+json")
        body = r2.json()
        self.assertEqual(body.get("code"), "rate_limit")
        self.assertIn("correlationId", body)
