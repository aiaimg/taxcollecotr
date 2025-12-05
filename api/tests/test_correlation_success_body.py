from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient


class CorrelationIdSuccessBodyTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_success_has_correlation_id_in_body(self):
        res = self.client.get("/api/v1/health/")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn("correlationId", body)

