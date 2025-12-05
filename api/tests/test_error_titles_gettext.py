from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient


class ErrorTitleGettextTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth.models import User
        u = User.objects.create_user(username="tx", email="tx@example.com", password="pass12345")
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(u).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_fr_not_found_title_from_catalog(self):
        res = self.client.delete("/api/v1/vehicles/UNKNOWN-PLATE/", HTTP_ACCEPT_LANGUAGE="fr")
        self.assertEqual(res.status_code, 404)
        body = res.json()
        self.assertEqual(body.get("title"), "Ressource introuvable")

    def test_mg_validation_title_from_catalog(self):
        from django.contrib.auth.models import User
        from vehicles.models import Vehicule, VehicleType
        u = User.objects.get(username="tx")
        vt, _ = VehicleType.objects.get_or_create(nom="Terrestre", defaults={"est_actif": True})
        v = Vehicule.objects.create(
            plaque_immatriculation="5678TBB",
            proprietaire=u,
            type_vehicule=vt,
            date_premiere_circulation="2020-01-01",
            puissance_fiscale_cv=10,
            source_energie="Diesel",
            categorie_vehicule="Personnel",
            marque="Test",
        )
        res = self.client.patch(
            f"/api/v1/vehicles/{v.plaque_immatriculation}/",
            {"puissance_fiscale_cv": 0},
            format="json",
            HTTP_ACCEPT_LANGUAGE="mg",
        )
        self.assertEqual(res.status_code, 400)
        body = res.json()
        self.assertEqual(body.get("title"), "Hadisoana fanamarinana")
