from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from vehicles.models import VehicleType, Vehicule
from core.models import UserProfile


class FleetCategoryFilterTests(TestCase):
    def setUp(self):
        # Create user and mark as company (fleet manager)
        self.user = User.objects.create_user(username="fleetuser", password="testpass")
        UserProfile.objects.update_or_create(user=self.user, defaults={"user_type": "company"})

        # Create vehicle types
        self.type_car = VehicleType.objects.create(nom="Voiture")
        self.type_plane = VehicleType.objects.create(nom="Avion")
        self.type_boat = VehicleType.objects.create(nom="Bateau")

        # Create vehicles for each category
        Vehicule.objects.create(
            plaque_immatriculation="1234TAA",
            proprietaire=self.user,
            nom_proprietaire="Company Owner",
            marque="Toyota",
            modele="Corolla",
            puissance_fiscale_cv=8,
            cylindree_cm3=1800,
            source_energie="Essence",
            date_premiere_circulation=date(2020, 1, 1),
            categorie_vehicule="Commercial",
            type_vehicule=self.type_car,
            vehicle_category="TERRESTRE",
        )

        Vehicule.objects.create(
            plaque_immatriculation="2345TAB",
            proprietaire=self.user,
            nom_proprietaire="Company Owner",
            marque="Cessna",
            modele="172",
            puissance_fiscale_cv=1,
            cylindree_cm3=1200,
            source_energie="Essence",
            date_premiere_circulation=date(2019, 5, 10),
            categorie_vehicule="Commercial",
            type_vehicule=self.type_plane,
            vehicle_category="AERIEN",
        )

        Vehicule.objects.create(
            plaque_immatriculation="3456TAC",
            proprietaire=self.user,
            nom_proprietaire="Company Owner",
            marque="Beneteau",
            modele="Oceanis",
            puissance_fiscale_cv=1,
            cylindree_cm3=900,
            source_energie="Diesel",
            date_premiere_circulation=date(2018, 3, 20),
            categorie_vehicule="Commercial",
            type_vehicule=self.type_boat,
            vehicle_category="MARITIME",
        )

    def test_filter_aerial_category(self):
        self.client.force_login(self.user)
        url = reverse("core:fleet_vehicles") + "?category=AERIEN"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        vehicles = response.context.get("vehicles")
        self.assertIsNotNone(vehicles)
        self.assertTrue(all(v.vehicle_category == "AERIEN" for v in vehicles))

    def test_filter_maritime_category(self):
        self.client.force_login(self.user)
        url = reverse("core:fleet_vehicles") + "?category=MARITIME"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        vehicles = response.context.get("vehicles")
        self.assertIsNotNone(vehicles)
        self.assertTrue(all(v.vehicle_category == "MARITIME" for v in vehicles))

    def test_filter_terrestrial_category(self):
        self.client.force_login(self.user)
        url = reverse("core:fleet_vehicles") + "?category=TERRESTRE"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        vehicles = response.context.get("vehicles")
        self.assertIsNotNone(vehicles)
        self.assertTrue(all(v.vehicle_category == "TERRESTRE" for v in vehicles))