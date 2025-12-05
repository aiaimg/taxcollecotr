"""
Property 31: ISO 8601 Date Format

Validates: Requirements 14.1
"""

import re
from django.utils import timezone
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient

from django.contrib.auth.models import User
from vehicles.models import VehicleType, Vehicule
from payments.models import PaiementTaxe


ISO8601_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


class ISO8601DateFormatPropertyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="iso", email="iso@example.com", password="pass12345")
        self.client.force_authenticate(user=self.user)

        vt, _ = VehicleType.objects.get_or_create(nom="Voiture", defaults={"description": "", "ordre_affichage": 1})
        self.vehicle = Vehicule.objects.create(
            plaque_immatriculation="1234TAA",
            proprietaire=self.user,
            puissance_fiscale_cv=13,
            cylindree_cm3=1200,
            source_energie="Essence",
            date_premiere_circulation=timezone.now().date(),
            categorie_vehicule="Personnel",
            type_vehicule=vt,
            marque="TEST",
        )

    def test_health_timestamp_iso8601_again(self):
        res = self.client.get("/api/v1/health/")
        self.assertEqual(res.status_code, 200)
        ts = res.json()["data"]["timestamp"]
        self.assertTrue(ISO8601_REGEX.match(ts))

    def test_health_timestamp_iso8601(self):
        res = self.client.get("/api/v1/health/")
        self.assertEqual(res.status_code, 200)
        ts = res.json()["data"]["timestamp"]
        self.assertTrue(ISO8601_REGEX.match(ts))
