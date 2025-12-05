"""
Tests for multi-vehicle notification functionality
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from notifications.services import NotificationService
from vehicles.models import VehicleType, Vehicule


class MultiVehicleNotificationTests(TestCase):
    """Tests for notifications with aerial and maritime vehicles"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create vehicle types
        self.aerial_type, _ = VehicleType.objects.get_or_create(
            nom="Avion", defaults={"description": "Aéronef à voilure fixe", "ordre_affichage": 100, "est_actif": True}
        )

        self.maritime_type, _ = VehicleType.objects.get_or_create(
            nom="Bateau de plaisance",
            defaults={"description": "Embarcation de loisir", "ordre_affichage": 200, "est_actif": True},
        )

        self.terrestrial_type, _ = VehicleType.objects.get_or_create(
            nom="Voiture", defaults={"description": "Véhicule terrestre", "ordre_affichage": 1, "est_actif": True}
        )

    def _create_vehicle_bypassing_validation(self, **kwargs):
        """Helper to create vehicle bypassing validation"""
        vehicle = Vehicule(**kwargs)
        # Call Django Model save directly, bypassing Vehicule.save()
        super(Vehicule, vehicle).save()
        return vehicle

    def test_aerial_vehicle_notification_french(self):
        """Test notification for aerial vehicle in French"""
        # Create aerial vehicle
        vehicle = self._create_vehicle_bypassing_validation(
            plaque_immatriculation="TEMP-AERIAL001",
            immatriculation_aerienne="5R-ABC",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.aerial_type,
            vehicle_category="AERIEN",
            marque="Boeing",
            modele="737",
            numero_serie_aeronef="SN12345",
            masse_maximale_decollage_kg=70000,
            puissance_moteur_kw=5000,
            source_energie="Autre",
            date_premiere_circulation=date(2020, 1, 1),
            puissance_fiscale_cv=100,
            cylindree_cm3=5000,
        )

        # Create notification
        notification = NotificationService.create_vehicle_added_notification(
            user=self.user, vehicle=vehicle, langue="fr"
        )

        # Verify notification
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertIn("Aéronef", notification.titre)
        self.assertIn("5R-ABC", notification.contenu)
        self.assertEqual(notification.metadata["vehicle_category"], "AERIEN")
        self.assertEqual(notification.metadata["vehicle_identifier"], "5R-ABC")

    def test_aerial_vehicle_notification_malagasy(self):
        """Test notification for aerial vehicle in Malagasy"""
        # Create aerial vehicle
        vehicle = self._create_vehicle_bypassing_validation(
            plaque_immatriculation="TEMP-AERIAL002",
            immatriculation_aerienne="5R-XYZ",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.aerial_type,
            vehicle_category="AERIEN",
            marque="Airbus",
            modele="A320",
            source_energie="Autre",
            date_premiere_circulation=date(2020, 1, 1),
            puissance_fiscale_cv=100,
        )

        # Create notification
        notification = NotificationService.create_vehicle_added_notification(
            user=self.user, vehicle=vehicle, langue="mg"
        )

        # Verify notification
        self.assertIsNotNone(notification)
        self.assertIn("Fiaramanidina", notification.titre)
        self.assertIn("5R-XYZ", notification.contenu)

    def test_maritime_vehicle_notification_with_classification(self):
        """Test notification for maritime vehicle with classification"""
        # Create maritime vehicle (navire de plaisance)
        vehicle = self._create_vehicle_bypassing_validation(
            plaque_immatriculation="TEMP-MARITIME01",
            numero_francisation="FR-12345",
            nom_navire="Sea Explorer",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.maritime_type,
            vehicle_category="MARITIME",
            marque="Beneteau",
            modele="Oceanis 40",
            longueur_metres=Decimal("12.50"),
            puissance_fiscale_cv=Decimal("50.00"),
            puissance_moteur_kw=Decimal("36.75"),
            source_energie="Diesel",
            date_premiere_circulation=date(2018, 6, 15),
            specifications_techniques={"maritime_classification": "NAVIRE_PLAISANCE"},
        )

        # Create notification
        notification = NotificationService.create_vehicle_added_notification(
            user=self.user, vehicle=vehicle, langue="fr"
        )

        # Verify notification
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertIn("Navire", notification.titre)
        self.assertIn("Sea Explorer", notification.contenu)
        self.assertIn("Classification", notification.contenu)
        self.assertEqual(notification.metadata["vehicle_category"], "MARITIME")
        self.assertEqual(notification.metadata["maritime_classification"], "NAVIRE_PLAISANCE")

    def test_maritime_vehicle_notification_jetski(self):
        """Test notification for jet-ski"""
        # Create jet-ski
        vehicle = self._create_vehicle_bypassing_validation(
            plaque_immatriculation="TEMP-JETSKI001",
            numero_francisation="FR-JS-001",
            nom_navire="Speed Racer",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.maritime_type,
            vehicle_category="MARITIME",
            marque="Yamaha",
            modele="VX Cruiser",
            longueur_metres=Decimal("3.50"),
            puissance_fiscale_cv=Decimal("70.00"),
            puissance_moteur_kw=Decimal("95.00"),
            source_energie="Essence",
            date_premiere_circulation=date(2021, 3, 10),
            specifications_techniques={"maritime_classification": "JETSKI"},
        )

        # Create notification
        notification = NotificationService.create_vehicle_added_notification(
            user=self.user, vehicle=vehicle, langue="fr"
        )

        # Verify notification
        self.assertIsNotNone(notification)
        self.assertIn("Navire", notification.titre)
        self.assertIn("Speed Racer", notification.contenu)
        self.assertEqual(notification.metadata["maritime_classification"], "JETSKI")

    def test_maritime_vehicle_notification_autres_engins(self):
        """Test notification for autres engins maritimes"""
        # Create small boat
        vehicle = self._create_vehicle_bypassing_validation(
            plaque_immatriculation="TEMP-BOAT0001",
            numero_francisation="FR-SB-001",
            nom_navire="Little Fisher",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.maritime_type,
            vehicle_category="MARITIME",
            marque="Zodiac",
            modele="Pro 420",
            longueur_metres=Decimal("4.20"),
            puissance_fiscale_cv=Decimal("15.00"),
            source_energie="Essence",
            date_premiere_circulation=date(2019, 5, 20),
            specifications_techniques={"maritime_classification": "AUTRES_ENGINS"},
        )

        # Create notification
        notification = NotificationService.create_vehicle_added_notification(
            user=self.user, vehicle=vehicle, langue="fr"
        )

        # Verify notification
        self.assertIsNotNone(notification)
        self.assertIn("Navire", notification.titre)
        self.assertEqual(notification.metadata["maritime_classification"], "AUTRES_ENGINS")

    def test_terrestrial_vehicle_notification_unchanged(self):
        """Test that terrestrial vehicle notifications still work"""
        # Create terrestrial vehicle
        vehicle = self._create_vehicle_bypassing_validation(
            plaque_immatriculation="1234TAA",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.terrestrial_type,
            vehicle_category="TERRESTRE",
            marque="Toyota",
            modele="Corolla",
            puissance_fiscale_cv=8,
            cylindree_cm3=1600,
            source_energie="Essence",
            date_premiere_circulation=date(2015, 8, 1),
        )

        # Create notification
        notification = NotificationService.create_vehicle_added_notification(
            user=self.user, vehicle=vehicle, langue="fr"
        )

        # Verify notification
        self.assertIsNotNone(notification)
        self.assertIn("Véhicule", notification.titre)
        self.assertIn("1234TAA", notification.contenu)
        self.assertEqual(notification.metadata["vehicle_category"], "TERRESTRE")

    def test_maritime_classification_notification(self):
        """Test maritime classification notification"""
        # Create maritime vehicle
        vehicle = self._create_vehicle_bypassing_validation(
            plaque_immatriculation="TEMP-MARITIME02",
            numero_francisation="FR-67890",
            nom_navire="Ocean Dream",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.maritime_type,
            vehicle_category="MARITIME",
            marque="Jeanneau",
            longueur_metres=Decimal("8.00"),
            puissance_fiscale_cv=Decimal("25.00"),
            source_energie="Diesel",
            date_premiere_circulation=date(2017, 4, 12),
        )

        # Create classification notification
        notification = NotificationService.create_maritime_classification_notification(
            user=self.user,
            vehicle=vehicle,
            classification="NAVIRE_PLAISANCE",
            tax_amount=Decimal("200000"),
            langue="fr",
        )

        # Verify notification
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertIn("Classification maritime", notification.titre)
        self.assertIn("Ocean Dream", notification.contenu)
        self.assertIn("Navire de plaisance", notification.contenu)
        self.assertIn("200,000", notification.contenu)
        self.assertEqual(notification.metadata["classification"], "NAVIRE_PLAISANCE")
        self.assertTrue(notification.metadata["allow_contestation"])

    def test_notification_metadata_structure(self):
        """Test that notification metadata has correct structure"""
        # Create aerial vehicle
        vehicle = self._create_vehicle_bypassing_validation(
            plaque_immatriculation="TEMP-META0001",
            immatriculation_aerienne="5R-META",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.aerial_type,
            vehicle_category="AERIEN",
            marque="Cessna",
            source_energie="Autre",
            date_premiere_circulation=date(2019, 1, 1),
            puissance_fiscale_cv=50,
        )

        # Create notification
        notification = NotificationService.create_vehicle_added_notification(
            user=self.user, vehicle=vehicle, langue="fr"
        )

        # Verify metadata structure
        self.assertIn("event", notification.metadata)
        self.assertIn("vehicle_id", notification.metadata)
        self.assertIn("vehicle_category", notification.metadata)
        self.assertIn("vehicle_identifier", notification.metadata)
        self.assertEqual(notification.metadata["event"], "vehicle_added")
        self.assertEqual(notification.metadata["vehicle_category"], "AERIEN")
