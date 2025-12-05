"""
Property 34: Content Negotiation via Accept Header

Validates: Requirements 14.4
"""

from hypothesis import settings
from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient

from django.contrib.auth.models import User


class ContentNegotiationPropertyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="accept", email="accept@example.com", password="pass12345")
        self.client.force_authenticate(user=self.user)

    def test_accept_application_json(self):
        res = self.client.get("/api/v1/vehicles/", HTTP_ACCEPT="application/json")
        self.assertIn(res.status_code, [200, 204])
        ct = res.headers.get("Content-Type") or res._headers.get("content-type", (None, None))[1]
        self.assertTrue(ct.startswith("application/json"))

    def test_accept_problem_json_on_error(self):
        res = self.client.delete("/api/v1/vehicles/UNKNOWN-PLATE/", HTTP_ACCEPT="application/problem+json")
        self.assertEqual(res.status_code, 404)
        ct = res.headers.get("Content-Type") or res._headers.get("content-type", (None, None))[1]
        self.assertTrue(ct.startswith("application/problem+json"))

    def test_unsupported_accept_returns_406(self):
        res = self.client.get("/api/v1/vehicles/", HTTP_ACCEPT="text/html")
        self.assertEqual(res.status_code, 406)
