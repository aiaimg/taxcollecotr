from hypothesis.extra.django import TestCase
from django.utils.translation import override
from rest_framework.test import APIClient


class RFC7807FormatPropertyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth.models import User
        u = User.objects.create_user(username="t1", email="t1@example.com", password="pass12345")
        from rest_framework_simplejwt.tokens import RefreshToken
        self.token = RefreshToken.for_user(u).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_401_authentication_error_problem_details(self):
        c = APIClient()
        res = c.post("/api/v1/vehicles/", {}, format="json")
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.get("Content-Type"), "application/problem+json")
        body = res.json()
        for key in ("type", "title", "status", "code"):
            self.assertIn(key, body)
        self.assertIn("correlationId", body)

    def test_404_not_found_problem_details(self):
        res = self.client.delete("/api/v1/vehicles/UNKNOWN-PLATE/")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.get("Content-Type"), "application/problem+json")
        body = res.json()
        self.assertEqual(body.get("code"), "not_found")
        for key in ("type", "title", "status", "code", "correlationId"):
            self.assertIn(key, body)


class ErrorResponseCompletenessPropertyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth.models import User
        u = User.objects.create_user(username="t2", email="t2@example.com", password="pass12345")
        from rest_framework_simplejwt.tokens import RefreshToken
        self.token = RefreshToken.for_user(u).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_problem_response_completeness(self):
        res = self.client.delete("/api/v1/vehicles/NONEXISTENT/")
        self.assertEqual(res.get("Content-Type"), "application/problem+json")
        body = res.json()
        for key in ("type", "title", "status", "detail", "code", "correlationId"):
            self.assertIn(key, body)


class MultilingualErrorMessagesPropertyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth.models import User
        u = User.objects.create_user(username="t3", email="t3@example.com", password="pass12345")
        from rest_framework_simplejwt.tokens import RefreshToken
        self.token = RefreshToken.for_user(u).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_malagasy_title_for_not_found(self):
        with override("mg"):
            res = self.client.delete("/api/v1/vehicles/UNKNOWN-PLATE/")
            self.assertEqual(res.status_code, 404)
            body = res.json()
            self.assertTrue(body.get("title"))
            self.assertEqual(body.get("code"), "not_found")
            self.assertIn("correlationId", body)


class ValidationErrorDetailPropertyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth.models import User
        u = User.objects.create_user(username="t4", email="t4@example.com", password="pass12345")
        from rest_framework_simplejwt.tokens import RefreshToken
        self.token = RefreshToken.for_user(u).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_validation_error_contains_errors(self):
        from django.contrib.auth.models import User
        from vehicles.models import Vehicule, VehicleType
        u = User.objects.get(username="t4")
        vt, _ = VehicleType.objects.get_or_create(nom="Terrestre", defaults={"est_actif": True})
        v = Vehicule.objects.create(
            plaque_immatriculation="1234TAA",
            proprietaire=u,
            type_vehicule=vt,
            date_premiere_circulation="2020-01-01",
            puissance_fiscale_cv=10,
            source_energie="Diesel",
            categorie_vehicule="Personnel",
            marque="Test",
        )
        plaque = v.plaque_immatriculation
        res = self.client.patch(
            f"/api/v1/vehicles/{plaque}/",
            {"puissance_fiscale_cv": 0},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        body = res.json()
        self.assertEqual(body.get("code"), "validation_error")
        self.assertIn("errors", body)
        self.assertEqual(res.get("Content-Type"), "application/problem+json")
