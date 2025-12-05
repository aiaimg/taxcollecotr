"""
Property 35: CORS Headers

Validates: Requirements 14.5
"""

from hypothesis import settings
from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient


class CORSHeadersPropertyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.origin = "http://localhost:3000"

    def test_preflight_options_includes_cors_headers(self):
        res = self.client.options(
            "/api/v1/vehicles/",
            HTTP_ORIGIN=self.origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="Authorization, Content-Type",
        )
        self.assertIn(res.status_code, [200, 204])
        allow_origin = res.headers.get("Access-Control-Allow-Origin") or res._headers.get("access-control-allow-origin", (None, None))[1]
        self.assertEqual(allow_origin, self.origin)

    def test_simple_get_includes_cors_headers(self):
        res = self.client.get("/api/v1/vehicles/", HTTP_ORIGIN=self.origin)
        self.assertIn(res.status_code, [200, 401])
        allow_origin = res.headers.get("Access-Control-Allow-Origin") or res._headers.get("access-control-allow-origin", (None, None))[1]
        self.assertEqual(allow_origin, self.origin)
