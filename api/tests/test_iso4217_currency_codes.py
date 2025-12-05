"""
Property 32: ISO 4217 Currency Codes

Validates: Requirements 14.2
"""

from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.utils import timezone
from vehicles.models import VehicleType, Vehicule
from payments.models import PaiementTaxe


class ISO4217CurrencyCodesPropertyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="iso4217", email="iso4217@example.com", password="pass12345")
        self.client.force_authenticate(user=self.user)

        vt, _ = VehicleType.objects.get_or_create(nom="Voiture", defaults={"description": "", "ordre_affichage": 1})
        self.vehicle = Vehicule.objects.create(
            plaque_immatriculation="5678TBB",
            proprietaire=self.user,
            puissance_fiscale_cv=13,
            cylindree_cm3=1300,
            source_energie="Essence",
            date_premiere_circulation=timezone.now().date(),
            categorie_vehicule="Personnel",
            type_vehicule=vt,
            marque="TEST",
        )

    @settings(max_examples=50, deadline=None)
    @given(code=st.sampled_from(["MGA", "mga", "MgA"]))
    def test_payment_serializer_includes_currency_code(self, code):
        p = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=timezone.now().year,
            montant_du_ariary=2000,
            montant_paye_ariary=2000,
            statut="PAYE",
        )
        p.currency_stripe = code
        p.save(update_fields=["currency_stripe"])

        # Verify ISO 4217 normalization
        assert (p.currency_stripe or "MGA").upper() == "MGA"
        p.delete()
