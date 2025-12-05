from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient


class AcceptLanguageNegotiationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth.models import User
        u = User.objects.create_user(username="lng", email="lng@example.com", password="pass12345")
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(u).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_mg_title_with_accept_language_header(self):
        res = self.client.delete("/api/v1/vehicles/UNKNOWN-PLATE/", HTTP_ACCEPT_LANGUAGE="mg")
        self.assertEqual(res.status_code, 404)
        body = res.json()
        self.assertEqual(body.get("code"), "not_found")
        self.assertEqual(body.get("title"), "Tsy hita ny loharano")

