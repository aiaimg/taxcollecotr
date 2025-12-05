from django.test import TestCase
from rest_framework.test import APIClient


class DeprecationHeadersTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_deprecated_endpoint_has_headers(self):
        resp = self.client.get("/api/v1/health/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Deprecation", resp)
        self.assertIn("Sunset", resp)
        self.assertIn("Link", resp)

