"""
Tests for Multi-Vehicle Category API endpoints
Tests aerial and maritime vehicle API functionality
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from vehicles.models import GrilleTarifaire, VehicleType, Vehicule


class AerialVehicleAPITestCase(TestCase):
    """Test aerial vehicle API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create aerial vehicle type
        self.aerial_type, _ = VehicleType.objects.get_or_create(
            nom="Avion", defaults={"description": "Aéronef à voilure fixe", "est_actif": True, "ordre_affichage": 100}
        )

        # Create aerial tariff grid
        self.aerial_grid = GrilleTarifaire.objects.create(
            grid_type="FLAT_AERIAL",
            aerial_type="ALL",
            montant_ariary=Decimal("2000000"),
            annee_fiscale=2026,
            est_active=True,
        )

        # Get access token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_aerial_vehicle(self):
        """Test creating an aerial vehicle via API"""
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "vehicle_category": "AERIEN",
                "immatriculation_aerienne": "5R-ABC",
                "type_vehicule_id": self.aerial_type.id,
                "marque": "Cessna",
                "modele": "172",
                "numero_serie_aeronef": "C172-12345",
                "masse_maximale_decollage_kg": 1200,
                "puissance_moteur_kw": 120,
                "date_premiere_circulation": "2020-01-01",
                "categorie_vehicule": "Personnel",
                "plaque_immatriculation": "5R-ABC",  # Using aerial registration as plate
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get("success", True))

        # Verify data
        data = response.data.get("data", response.data)
        self.assertEqual(data["vehicle_category"], "AERIEN")
        self.assertEqual(data["immatriculation_aerienne"], "5R-ABC")
        self.assertEqual(data["masse_maximale_decollage_kg"], 1200)

    def test_aerial_vehicle_tax_calculation(self):
        """Test tax calculation for aerial vehicle returns 2M Ar"""
        # Create aerial vehicle
        aerial_vehicle = Vehicule.objects.create(
            plaque_immatriculation="5R-XYZ",
            vehicle_category="AERIEN",
            immatriculation_aerienne="5R-XYZ",
            proprietaire=self.user,
            type_vehicule=self.aerial_type,
            masse_maximale_decollage_kg=1500,
            puissance_moteur_kw=150,
            date_premiere_circulation=date(2020, 1, 1),
            categorie_vehicule="Personnel",
        )

        response = self.client.get(f"/api/v1/vehicles/{aerial_vehicle.plaque_immatriculation}/calculate-tax/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        data = response.data["data"]
        self.assertEqual(data["vehicle_category"], "AERIEN")
        self.assertEqual(float(data["amount"]), 2000000.0)
        self.assertEqual(data["calculation_method"], "Tarif forfaitaire aérien")

    def test_aerial_vehicle_serializer_includes_tax_amount(self):
        """Test that aerial vehicle serializer includes calculated tax amount"""
        aerial_vehicle = Vehicule.objects.create(
            plaque_immatriculation="5R-TEST",
            vehicle_category="AERIEN",
            immatriculation_aerienne="5R-TEST",
            proprietaire=self.user,
            type_vehicule=self.aerial_type,
            masse_maximale_decollage_kg=2000,
            puissance_moteur_kw=200,
            date_premiere_circulation=date(2021, 1, 1),
            categorie_vehicule="Personnel",
        )

        response = self.client.get(f"/api/v1/vehicles/{aerial_vehicle.plaque_immatriculation}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", response.data)
        self.assertIn("tax_amount", data)
        self.assertEqual(float(data["tax_amount"]), 2000000.0)

    def test_aerial_vehicle_validation(self):
        """Test aerial vehicle validation"""
        # Test invalid immatriculation format
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "vehicle_category": "AERIEN",
                "immatriculation_aerienne": "INVALID",
                "type_vehicule_id": self.aerial_type.id,
                "masse_maximale_decollage_kg": 1200,
                "date_premiere_circulation": "2020-01-01",
                "categorie_vehicule": "Personnel",
                "plaque_immatriculation": "INVALID",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid masse (too low)
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "vehicle_category": "AERIEN",
                "immatriculation_aerienne": "5R-ABC",
                "type_vehicule_id": self.aerial_type.id,
                "masse_maximale_decollage_kg": 5,  # Too low
                "date_premiere_circulation": "2020-01-01",
                "categorie_vehicule": "Personnel",
                "plaque_immatriculation": "5R-ABC",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MaritimeVehicleAPITestCase(TestCase):
    """Test maritime vehicle API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create maritime vehicle types
        self.yacht_type, _ = VehicleType.objects.get_or_create(
            nom="Yacht", defaults={"description": "Bateau de luxe", "est_actif": True, "ordre_affichage": 200}
        )

        self.jetski_type, _ = VehicleType.objects.get_or_create(
            nom="Jet-ski", defaults={"description": "Moto nautique", "est_actif": True, "ordre_affichage": 203}
        )

        # Create maritime tariff grids
        self.navire_plaisance_grid = GrilleTarifaire.objects.create(
            grid_type="FLAT_MARITIME",
            maritime_category="NAVIRE_PLAISANCE",
            longueur_min_metres=Decimal("7.00"),
            puissance_min_cv_maritime=Decimal("22.00"),
            puissance_min_kw_maritime=Decimal("90.00"),
            montant_ariary=Decimal("200000"),
            annee_fiscale=2026,
            est_active=True,
        )

        self.jetski_grid = GrilleTarifaire.objects.create(
            grid_type="FLAT_MARITIME",
            maritime_category="JETSKI",
            puissance_min_kw_maritime=Decimal("90.00"),
            montant_ariary=Decimal("200000"),
            annee_fiscale=2026,
            est_active=True,
        )

        self.autres_engins_grid = GrilleTarifaire.objects.create(
            grid_type="FLAT_MARITIME",
            maritime_category="AUTRES_ENGINS",
            montant_ariary=Decimal("1000000"),
            annee_fiscale=2026,
            est_active=True,
        )

        # Get access token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_maritime_vehicle(self):
        """Test creating a maritime vehicle via API"""
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "vehicle_category": "MARITIME",
                "numero_francisation": "FR-12345",
                "nom_navire": "Sea Breeze",
                "type_vehicule_id": self.yacht_type.id,
                "marque": "Beneteau",
                "modele": "Oceanis 40",
                "longueur_metres": 12.5,
                "tonnage_tonneaux": 8.5,
                "puissance_fiscale_cv": 50,
                "date_premiere_circulation": "2019-01-01",
                "categorie_vehicule": "Personnel",
                "plaque_immatriculation": "FR-12345",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get("success", True))

        data = response.data.get("data", response.data)
        self.assertEqual(data["vehicle_category"], "MARITIME")
        self.assertEqual(data["numero_francisation"], "FR-12345")
        self.assertEqual(data["nom_navire"], "Sea Breeze")

    def test_maritime_vehicle_classification_navire_plaisance(self):
        """Test maritime vehicle classification for navire de plaisance"""
        maritime_vehicle = Vehicule.objects.create(
            plaque_immatriculation="FR-YACHT",
            vehicle_category="MARITIME",
            numero_francisation="FR-YACHT",
            nom_navire="Luxury Yacht",
            proprietaire=self.user,
            type_vehicule=self.yacht_type,
            longueur_metres=Decimal("10.0"),  # >= 7m
            puissance_fiscale_cv=Decimal("30.0"),
            date_premiere_circulation=date(2020, 1, 1),
            categorie_vehicule="Personnel",
        )

        response = self.client.get(f"/api/v1/vehicles/{maritime_vehicle.plaque_immatriculation}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", response.data)
        self.assertEqual(data["maritime_classification"], "NAVIRE_PLAISANCE")
        self.assertEqual(float(data["tax_amount"]), 200000.0)

    def test_maritime_vehicle_classification_jetski(self):
        """Test maritime vehicle classification for jet-ski"""
        jetski_vehicle = Vehicule.objects.create(
            plaque_immatriculation="JS-001",
            vehicle_category="MARITIME",
            numero_francisation="JS-001",
            nom_navire="Speed Jet",
            proprietaire=self.user,
            type_vehicule=self.jetski_type,
            longueur_metres=Decimal("3.5"),
            puissance_moteur_kw=Decimal("95.0"),  # >= 90kW
            date_premiere_circulation=date(2021, 1, 1),
            categorie_vehicule="Personnel",
        )

        response = self.client.get(f"/api/v1/vehicles/{jetski_vehicle.plaque_immatriculation}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", response.data)
        self.assertEqual(data["maritime_classification"], "JETSKI")
        self.assertEqual(float(data["tax_amount"]), 200000.0)

    def test_maritime_vehicle_classification_autres_engins(self):
        """Test maritime vehicle classification for autres engins"""
        small_boat = Vehicule.objects.create(
            plaque_immatriculation="SB-001",
            vehicle_category="MARITIME",
            numero_francisation="SB-001",
            nom_navire="Small Boat",
            proprietaire=self.user,
            type_vehicule=self.yacht_type,
            longueur_metres=Decimal("5.0"),  # < 7m
            puissance_fiscale_cv=Decimal("15.0"),  # < 22CV
            date_premiere_circulation=date(2021, 1, 1),
            categorie_vehicule="Personnel",
        )

        response = self.client.get(f"/api/v1/vehicles/{small_boat.plaque_immatriculation}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", response.data)
        self.assertEqual(data["maritime_classification"], "AUTRES_ENGINS")
        self.assertEqual(float(data["tax_amount"]), 1000000.0)

    def test_maritime_vehicle_power_conversion(self):
        """Test automatic power conversion CV <-> kW"""
        # Create with only CV
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "vehicle_category": "MARITIME",
                "numero_francisation": "FR-CONV",
                "nom_navire": "Converter",
                "type_vehicule_id": self.yacht_type.id,
                "longueur_metres": 8.0,
                "puissance_fiscale_cv": 30,  # Only CV provided
                "date_premiere_circulation": "2020-01-01",
                "categorie_vehicule": "Personnel",
                "plaque_immatriculation": "FR-CONV",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data.get("data", response.data)

        # Should have auto-calculated kW
        self.assertIsNotNone(data.get("puissance_moteur_kw"))
        # 30 CV * 0.735 = 22.05 kW
        self.assertAlmostEqual(float(data["puissance_moteur_kw"]), 22.05, places=1)

    def test_maritime_vehicle_tax_calculation(self):
        """Test tax calculation endpoint for maritime vehicle"""
        maritime_vehicle = Vehicule.objects.create(
            plaque_immatriculation="FR-TAX",
            vehicle_category="MARITIME",
            numero_francisation="FR-TAX",
            nom_navire="Tax Test",
            proprietaire=self.user,
            type_vehicule=self.yacht_type,
            longueur_metres=Decimal("9.0"),
            puissance_fiscale_cv=Decimal("25.0"),
            date_premiere_circulation=date(2020, 1, 1),
            categorie_vehicule="Personnel",
        )

        response = self.client.get(f"/api/v1/vehicles/{maritime_vehicle.plaque_immatriculation}/calculate-tax/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        data = response.data["data"]
        self.assertEqual(data["vehicle_category"], "MARITIME")
        self.assertEqual(data["maritime_category"], "NAVIRE_PLAISANCE")
        self.assertEqual(float(data["amount"]), 200000.0)


class VehicleByCategoryAPITestCase(TestCase):
    """Test by_category endpoint"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create vehicle types
        self.car_type, _ = VehicleType.objects.get_or_create(nom="Voiture", defaults={"est_actif": True})
        self.plane_type, _ = VehicleType.objects.get_or_create(nom="Avion", defaults={"est_actif": True})
        self.boat_type, _ = VehicleType.objects.get_or_create(nom="Bateau", defaults={"est_actif": True})

        # Create vehicles of different categories
        Vehicule.objects.create(
            plaque_immatriculation="1234 TAA",
            vehicle_category="TERRESTRE",
            proprietaire=self.user,
            type_vehicule=self.car_type,
            puissance_fiscale_cv=10,
            source_energie="Essence",
            date_premiere_circulation=date(2020, 1, 1),
            categorie_vehicule="Personnel",
        )

        Vehicule.objects.create(
            plaque_immatriculation="5R-ABC",
            vehicle_category="AERIEN",
            immatriculation_aerienne="5R-ABC",
            proprietaire=self.user,
            type_vehicule=self.plane_type,
            masse_maximale_decollage_kg=1500,
            date_premiere_circulation=date(2020, 1, 1),
            categorie_vehicule="Personnel",
        )

        Vehicule.objects.create(
            plaque_immatriculation="FR-123",
            vehicle_category="MARITIME",
            numero_francisation="FR-123",
            nom_navire="Sea Star",
            proprietaire=self.user,
            type_vehicule=self.boat_type,
            longueur_metres=Decimal("8.0"),
            date_premiere_circulation=date(2020, 1, 1),
            categorie_vehicule="Personnel",
        )

        # Get access token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_filter_by_terrestrial_category(self):
        """Test filtering vehicles by TERRESTRE category"""
        response = self.client.get("/api/v1/vehicles/by-category/?category=TERRESTRE")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["vehicle_category"], "TERRESTRE")

    def test_filter_by_aerial_category(self):
        """Test filtering vehicles by AERIEN category"""
        response = self.client.get("/api/v1/vehicles/by-category/?category=AERIEN")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["vehicle_category"], "AERIEN")
        self.assertIn("immatriculation_aerienne", data[0])

    def test_filter_by_maritime_category(self):
        """Test filtering vehicles by MARITIME category"""
        response = self.client.get("/api/v1/vehicles/by-category/?category=MARITIME")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["vehicle_category"], "MARITIME")
        self.assertIn("numero_francisation", data[0])
        self.assertIn("maritime_classification", data[0])

    def test_invalid_category(self):
        """Test filtering with invalid category"""
        response = self.client.get("/api/v1/vehicles/by-category/?category=INVALID")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_default_category(self):
        """Test default category is TERRESTRE"""
        response = self.client.get("/api/v1/vehicles/by-category/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        data = response.data["data"]
        for vehicle in data:
            self.assertEqual(vehicle["vehicle_category"], "TERRESTRE")
