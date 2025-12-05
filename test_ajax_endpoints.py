"""
Test script for AJAX endpoints
Tests the calculate_tax_ajax, classify_maritime_ajax, and convert_power_ajax endpoints
"""

import os

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from vehicles.models import GrilleTarifaire, VehicleType, Vehicule
from vehicles.views import calculate_tax_ajax, classify_maritime_ajax, convert_power_ajax

User = get_user_model()


class AJAXEndpointsTest(TestCase):
    """Test AJAX endpoints for multi-vehicle tax calculation"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        # Get or create test user
        self.user, _ = User.objects.get_or_create(
            username="testuser",
            defaults={
                "email": "test@example.com",
            },
        )
        if not self.user.has_usable_password():
            self.user.set_password("testpass123")
            self.user.save()

        # Get or create vehicle types
        self.aerial_type, _ = VehicleType.objects.get_or_create(
            nom="Avion", defaults={"description": "Aéronef à voilure fixe", "ordre_affichage": 100, "est_actif": True}
        )

        self.maritime_type, _ = VehicleType.objects.get_or_create(
            nom="Jet-ski", defaults={"description": "Moto nautique", "ordre_affichage": 200, "est_actif": True}
        )

        # Get or create tariff grids for current year
        from django.utils import timezone

        current_year = timezone.now().year

        GrilleTarifaire.objects.get_or_create(
            grid_type="FLAT_AERIAL",
            annee_fiscale=current_year,
            defaults={"aerial_type": "ALL", "montant_ariary": Decimal("2000000"), "est_active": True},
        )

        GrilleTarifaire.objects.get_or_create(
            grid_type="FLAT_MARITIME",
            maritime_category="JETSKI",
            annee_fiscale=current_year,
            defaults={
                "puissance_min_kw_maritime": Decimal("90.00"),
                "montant_ariary": Decimal("200000"),
                "est_active": True,
            },
        )

        GrilleTarifaire.objects.get_or_create(
            grid_type="FLAT_MARITIME",
            maritime_category="NAVIRE_PLAISANCE",
            annee_fiscale=current_year,
            defaults={
                "longueur_min_metres": Decimal("7.00"),
                "puissance_min_cv_maritime": Decimal("22.00"),
                "puissance_min_kw_maritime": Decimal("90.00"),
                "montant_ariary": Decimal("200000"),
                "est_active": True,
            },
        )

    def test_calculate_tax_ajax_aerial(self):
        """Test tax calculation for aerial vehicles"""
        request = self.factory.post(
            "/vehicles/ajax/calculate-tax/",
            {
                "vehicle_category": "AERIEN",
                "masse_maximale_decollage_kg": 1200,
                "puissance_moteur_kw": 120,
                "date_premiere_circulation": "2020-01-01",
                "categorie_vehicule": "Personnel",
            },
        )
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        request.user = self.user

        response = calculate_tax_ajax(request)
        data = json.loads(response.content)

        print("Aerial Tax Calculation:")
        print(f"  Success: {data.get('success')}")
        print(f"  Tax Amount: {data.get('tax_amount')}")
        print(f"  Calculation Method: {data.get('calculation_method')}")
        print(f"  Message: {data.get('message')}")
        print(f"  Full response: {data}")

        assert data["success"] == True
        assert data["tax_amount"] == "2000000.00"
        assert "aérien" in data["calculation_method"].lower()

    def test_classify_maritime_ajax_jetski(self):
        """Test maritime classification for jet-ski"""
        request = self.factory.post(
            "/vehicles/ajax/classify-maritime/",
            {
                "longueur_metres": 3,
                "puissance_fiscale_cv": 0,
                "puissance_moteur_kw": 95,
                "type_vehicule": self.maritime_type.id,
            },
        )
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        request.user = self.user

        response = classify_maritime_ajax(request)
        data = json.loads(response.content)

        print("\nMaritime Classification (Jet-ski):")
        print(f"  Success: {data.get('success')}")
        print(f"  Classification: {data.get('classification')}")
        print(f"  Tax Amount: {data.get('tax_amount')}")
        print(f"  Confidence: {data.get('confidence')}")
        print(f"  Explanation: {data.get('explanation')}")

        assert data["success"] == True
        assert data["classification"] == "JETSKI"
        assert data["tax_amount"] == "200000.00"

    def test_classify_maritime_ajax_navire_plaisance(self):
        """Test maritime classification for navire de plaisance"""
        # Create a non-jetski maritime type
        bateau_type, _ = VehicleType.objects.get_or_create(
            nom="Bateau de plaisance",
            defaults={"description": "Embarcation de loisir", "ordre_affichage": 201, "est_actif": True},
        )

        request = self.factory.post(
            "/vehicles/ajax/classify-maritime/",
            {
                "longueur_metres": 8,
                "puissance_fiscale_cv": 25,
                "puissance_moteur_kw": 0,
                "type_vehicule": bateau_type.id,
            },
        )
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        request.user = self.user

        response = classify_maritime_ajax(request)
        data = json.loads(response.content)

        print("\nMaritime Classification (Navire de plaisance):")
        print(f"  Success: {data.get('success')}")
        print(f"  Classification: {data.get('classification')}")
        print(f"  Tax Amount: {data.get('tax_amount')}")
        print(f"  Confidence: {data.get('confidence')}")

        assert data["success"] == True
        assert data["classification"] == "NAVIRE_PLAISANCE"
        assert data["tax_amount"] == "200000.00"

    def test_convert_power_ajax_cv_to_kw(self):
        """Test power conversion from CV to kW"""
        request = self.factory.post("/vehicles/ajax/convert-power/", {"value": 22, "source_unit": "CV"})
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        request.user = self.user

        response = convert_power_ajax(request)
        data = json.loads(response.content)

        print("\nPower Conversion (CV to kW):")
        print(f"  Success: {data.get('success')}")
        print(f"  Original: {data.get('original_value')} {data.get('original_unit')}")
        print(f"  Converted: {data.get('converted_value')} {data.get('converted_unit')}")
        print(f"  Formula: {data.get('formula')}")

        assert data["success"] == True
        assert data["original_unit"] == "CV"
        assert data["converted_unit"] == "kW"
        # 22 CV * 0.735 = 16.17 kW
        assert float(data["converted_value"]) == 16.17

    def test_convert_power_ajax_kw_to_cv(self):
        """Test power conversion from kW to CV"""
        request = self.factory.post("/vehicles/ajax/convert-power/", {"value": 90, "source_unit": "kW"})
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        request.user = self.user

        response = convert_power_ajax(request)
        data = json.loads(response.content)

        print("\nPower Conversion (kW to CV):")
        print(f"  Success: {data.get('success')}")
        print(f"  Original: {data.get('original_value')} {data.get('original_unit')}")
        print(f"  Converted: {data.get('converted_value')} {data.get('converted_unit')}")
        print(f"  Formula: {data.get('formula')}")

        assert data["success"] == True
        assert data["original_unit"] == "kW"
        assert data["converted_unit"] == "CV"
        # 90 kW * 1.36 = 122.4 CV
        assert float(data["converted_value"]) == 122.4


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Testing AJAX Endpoints for Multi-Vehicle Tax Calculation")
    print("=" * 60)

    test = AJAXEndpointsTest()
    test.setUp()

    try:
        test.test_calculate_tax_ajax_aerial()
        print("\n✓ Aerial tax calculation test passed")
    except AssertionError as e:
        print(f"\n✗ Aerial tax calculation test failed: {e}")
        sys.exit(1)

    try:
        test.test_classify_maritime_ajax_jetski()
        print("\n✓ Maritime classification (jet-ski) test passed")
    except AssertionError as e:
        print(f"\n✗ Maritime classification (jet-ski) test failed: {e}")
        sys.exit(1)

    try:
        test.test_classify_maritime_ajax_navire_plaisance()
        print("\n✓ Maritime classification (navire de plaisance) test passed")
    except AssertionError as e:
        print(f"\n✗ Maritime classification (navire de plaisance) test failed: {e}")
        sys.exit(1)

    try:
        test.test_convert_power_ajax_cv_to_kw()
        print("\n✓ Power conversion (CV to kW) test passed")
    except AssertionError as e:
        print(f"\n✗ Power conversion (CV to kW) test failed: {e}")
        sys.exit(1)

    try:
        test.test_convert_power_ajax_kw_to_cv()
        print("\n✓ Power conversion (kW to CV) test passed")
    except AssertionError as e:
        print(f"\n✗ Power conversion (kW to CV) test failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("All AJAX endpoint tests passed successfully!")
    print("=" * 60)
