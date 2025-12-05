"""
Property 33: Pagination Link Headers

Validates: Requirements 14.3
"""

from hypothesis import settings
from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.utils import timezone
from vehicles.models import VehicleType, Vehicule


class PaginationLinkHeadersPropertyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="pgh", email="pgh@example.com", password="pass12345")
        self.client.force_authenticate(user=self.user)

        vt, _ = VehicleType.objects.get_or_create(nom="Moto", defaults={"description": "", "ordre_affichage": 2})

        # Create multiple vehicles to paginate
        for i in range(1, 6):
            Vehicule.objects.create(
                plaque_immatriculation=Vehicule.generate_temp_plate(),
                proprietaire=self.user,
                puissance_fiscale_cv=2,
                cylindree_cm3=110 + i,
                source_energie="Essence",
                date_premiere_circulation=timezone.now().date(),
                categorie_vehicule="Personnel",
                type_vehicule=vt,
                marque="TEST",
            )

    def test_link_headers_present(self):
        res = self.client.get("/api/v1/vehicles/?page=1&page_size=2")
        self.assertEqual(res.status_code, 200)
        link = res.headers.get("Link") or res._headers.get("link", (None, None))[1]
        self.assertTrue(link)
        self.assertIn('rel="first"', link)
        self.assertIn('rel="last"', link)
        self.assertIn('rel="next"', link)

        # Middle page should have prev and next
        res2 = self.client.get("/api/v1/vehicles/?page=2&page_size=2")
        link2 = res2.headers.get("Link") or res2._headers.get("link", (None, None))[1]
        self.assertIn('rel="prev"', link2)
        self.assertIn('rel="next"', link2)

        # Last page should have prev but not next
        res3 = self.client.get("/api/v1/vehicles/?page=3&page_size=2")
        link3 = res3.headers.get("Link") or res3._headers.get("link", (None, None))[1]
        self.assertIn('rel="prev"', link3)
        self.assertNotIn('rel="next"', link3)
