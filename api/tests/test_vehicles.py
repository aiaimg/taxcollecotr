"""
Tests for Vehicle API endpoints
"""

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from vehicles.models import VehicleType, Vehicule


class VehicleAPITestCase(TestCase):
    """Test vehicle API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.vehicle_type = VehicleType.objects.create(nom="Voiture", est_actif=True)
        self.vehicle = Vehicule.objects.create(
            plaque_immatriculation="1234 TAA",
            proprietaire=self.user,
            puissance_fiscale_cv=10,
            cylindree_cm3=1500,
            source_energie="Essence",
            date_premiere_circulation="2020-01-01",
            categorie_vehicule="Personnel",
            type_vehicule=self.vehicle_type,
        )

        # Get access token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_list_vehicles(self):
        """Test listing vehicles"""
        response = self.client.get("/api/v1/vehicles/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("data", response.data)
        self.assertIn("pagination", response.data)

    def test_get_vehicle_detail(self):
        """Test getting vehicle detail"""
        response = self.client.get(f"/api/v1/vehicles/{self.vehicle.plaque_immatriculation}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["plaque_immatriculation"], "1234 TAA")

    def test_create_vehicle(self):
        """Test creating a vehicle"""
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "plaque_immatriculation": "5678 TBB",
                "puissance_fiscale_cv": 8,
                "cylindree_cm3": 1200,
                "source_energie": "Diesel",
                "date_premiere_circulation": "2021-01-01",
                "categorie_vehicule": "Personnel",
                "type_vehicule_id": self.vehicle_type.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["plaque_immatriculation"], "5678 TBB")

    def test_get_vehicle_tax_info(self):
        """Test getting vehicle tax information"""
        response = self.client.get(f"/api/v1/vehicles/{self.vehicle.plaque_immatriculation}/tax_info/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("tax_info", response.data["data"])

    def test_vehicle_ownership(self):
        """Test that users can only see their own vehicles"""
        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")
        other_vehicle = Vehicule.objects.create(
            plaque_immatriculation="9999 TCC",
            proprietaire=other_user,
            puissance_fiscale_cv=12,
            cylindree_cm3=1800,
            source_energie="Essence",
            date_premiere_circulation="2020-01-01",
            categorie_vehicule="Personnel",
            type_vehicule=self.vehicle_type,
        )

        response = self.client.get("/api/v1/vehicles/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehicle_plates = [v["plaque_immatriculation"] for v in response.data["data"]]
        self.assertIn("1234 TAA", vehicle_plates)
        self.assertNotIn("9999 TCC", vehicle_plates)
