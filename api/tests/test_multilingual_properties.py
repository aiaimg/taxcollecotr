from django.test import TestCase
from django.utils.translation import override, gettext as _
from rest_framework.test import APIClient


class MultilingualAPIResponsesPropertyTest(TestCase):
    """
    Property 25: Multilingual API Responses
    Validates: Requirements 10.1, 10.2
    """

    def setUp(self):
        self.client = APIClient()

    def test_accept_language_mg(self):
        resp = self.client.post(
            "/api/v1/auth/login/",
            {"email": "nope@example.com", "password": "wrong"},
            format="json",
            HTTP_ACCEPT_LANGUAGE="mg",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp["Content-Language"], "mg")
        body = resp.json()
        self.assertEqual(body["error"]["code"], "validation_error")
        self.assertNotEqual(body["error"]["message"], "Invalid credentials")

    def test_accept_language_fr(self):
        resp = self.client.post(
            "/api/v1/auth/login/",
            {"email": "nope@example.com", "password": "wrong"},
            format="json",
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp["Content-Language"], "fr")
        body = resp.json()
        self.assertEqual(body["error"]["message"], "Identifiants invalides")


class DefaultLanguageFallbackPropertyTest(TestCase):
    """
    Property 26: Default Language Fallback
    Validates: Requirements 10.4
    """

    def setUp(self):
        self.client = APIClient()

    def test_no_accept_language_defaults_to_french(self):
        resp = self.client.post(
            "/api/v1/auth/login/",
            {"email": "nope@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp["Content-Language"], "fr")
        body = resp.json()
        self.assertEqual(body["error"]["message"], "Identifiants invalides")

    def test_unknown_language_fallback_to_french(self):
        resp = self.client.post(
            "/api/v1/auth/login/",
            {"email": "nope@example.com", "password": "wrong"},
            format="json",
            HTTP_ACCEPT_LANGUAGE="en",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp["Content-Language"], "fr")
        body = resp.json()
        self.assertEqual(body["error"]["message"], "Identifiants invalides")


class TranslationCompletenessPropertyTest(TestCase):
    """
    Property 27: Translation Completeness
    Validates: Requirements 10.3
    """

    def test_error_title_translations_exist(self):
        keys = [
            "error.title.validation_error",
            "error.title.authentication_error",
            "error.title.permission_denied",
            "error.title.not_found",
            "error.title.rate_limit",
            "error.title.bad_request",
            "error.title.internal_error",
            "error.title.error",
        ]
        with override("fr"):
            for k in keys:
                val = _(k)
                self.assertNotEqual(val, k)
        with override("mg"):
            for k in keys:
                val = _(k)
                self.assertNotEqual(val, k)

    def test_api_message_translations_exist(self):
        msgs = [
            "Invalid credentials",
            "Invalid refresh token",
            "Token is required",
            "QR code is invalid or expired",
            "Cannot update API key value",
            "API key updated successfully",
        ]
        with override("fr"):
            for m in msgs:
                val = _(m)
                self.assertNotEqual(val, m)
        with override("mg"):
            for m in msgs:
                val = _(m)
                self.assertNotEqual(val, m)

