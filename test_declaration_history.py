#!/usr/bin/env python
"""
Test script for declaration history functionality.
Tests Requirements: 17.1-17.7
"""

import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone

from payments.models import PaiementTaxe
from vehicles.models import GrilleTarifaire, VehicleType, Vehicule
from vehicles.views import DeclarationHistoryExportView, DeclarationHistoryView


class DeclarationHistoryTests(TestCase):
    """Test declaration history functionality"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        # Create user
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create vehicle types
        self.terrestrial_type, _ = VehicleType.objects.get_or_create(
            nom="Voiture", defaults={"description": "Voiture particulière", "ordre_affichage": 1}
        )

        self.aerial_type, _ = VehicleType.objects.get_or_create(
            nom="Avion", defaults={"description": "Avion privé", "ordre_affichage": 100}
        )

        self.maritime_type, _ = VehicleType.objects.get_or_create(
            nom="Yacht", defaults={"description": "Yacht de plaisance", "ordre_affichage": 200}
        )

        # Create tariff grids
        GrilleTarifaire.objects.create(
            grid_type="FLAT_AERIAL",
            aerial_type="ALL",
            montant_ariary=Decimal("2000000"),
            annee_fiscale=2026,
            est_active=True,
        )

        GrilleTarifaire.objects.create(
            grid_type="FLAT_MARITIME",
            maritime_category="NAVIRE_PLAISANCE",
            montant_ariary=Decimal("200000"),
            annee_fiscale=2026,
            est_active=True,
        )

        # Create test vehicles
        self.terrestrial_vehicle = Vehicule.objects.create(
            plaque_immatriculation="1234TAA",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.terrestrial_type,
            marque="Toyota",
            modele="Corolla",
            vehicle_category="TERRESTRE",
            puissance_fiscale_cv=11,
            cylindree_cm3=1000,
            source_energie="Essence",
            date_premiere_circulation=timezone.now().date(),
            statut_declaration="VALIDEE",
        )

        self.aerial_vehicle = Vehicule.objects.create(
            plaque_immatriculation="5678TAA",
            immatriculation_aerienne="5R-ABC",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.aerial_type,
            marque="Cessna",
            modele="172",
            vehicle_category="AERIEN",
            masse_maximale_decollage_kg=1000,
            puissance_fiscale_cv=1,
            source_energie="Essence",
            date_premiere_circulation=timezone.now().date(),
            statut_declaration="SOUMISE",
        )

        self.maritime_vehicle = Vehicule.objects.create(
            plaque_immatriculation="9012TAA",
            numero_francisation="MAR-001",
            nom_navire="Sea Breeze",
            proprietaire=self.user,
            nom_proprietaire="Test User",
            type_vehicule=self.maritime_type,
            marque="Beneteau",
            modele="Oceanis 40",
            vehicle_category="MARITIME",
            longueur_metres=Decimal("12.5"),
            puissance_fiscale_cv=50,
            source_energie="Diesel",
            date_premiere_circulation=timezone.now().date(),
            statut_declaration="VALIDEE",
        )

        # Create payments for current year
        current_year = timezone.now().year
        PaiementTaxe.objects.create(
            vehicule_plaque=self.terrestrial_vehicle,
            annee_fiscale=current_year,
            montant_du_ariary=Decimal("60000"),
            statut="PAYE",
            date_paiement=timezone.now(),
            methode_paiement="mvola",
            type_paiement="TAXE_VEHICULE",
        )

        PaiementTaxe.objects.create(
            vehicule_plaque=self.maritime_vehicle,
            annee_fiscale=current_year,
            montant_du_ariary=Decimal("200000"),
            statut="PAYE",
            date_paiement=timezone.now(),
            methode_paiement="mvola",
            type_paiement="TAXE_VEHICULE",
        )

    def test_declaration_history_view_loads(self):
        """Test that declaration history view loads successfully"""
        request = self.factory.get("/vehicles/history/")
        request.user = self.user

        view = DeclarationHistoryView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        print("✓ Declaration history view loads successfully")

    def test_filter_by_category(self):
        """Test filtering by vehicle category"""
        request = self.factory.get("/vehicles/history/?category=AERIEN")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().vehicle_category, "AERIEN")
        print("✓ Filter by category works correctly")

    def test_filter_by_status(self):
        """Test filtering by declaration status"""
        request = self.factory.get("/vehicles/history/?status=VALIDEE")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 2)
        for vehicle in queryset:
            self.assertEqual(vehicle.statut_declaration, "VALIDEE")
        print("✓ Filter by status works correctly")

    def test_search_by_identifier(self):
        """Test searching by vehicle identifier"""
        # Search by plaque
        request = self.factory.get("/vehicles/history/?search=1234")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().plaque_immatriculation, "1234TAA")

        # Search by aerial immatriculation
        request = self.factory.get("/vehicles/history/?search=5R-ABC")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().immatriculation_aerienne, "5R-ABC")

        # Search by ship name
        request = self.factory.get("/vehicles/history/?search=Sea Breeze")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().nom_navire, "Sea Breeze")

        print("✓ Search by identifier works correctly")

    def test_grouping_by_fiscal_year_and_category(self):
        """Test that vehicles are grouped correctly"""
        request = self.factory.get("/vehicles/history/")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        view.kwargs = {}
        view.object_list = view.get_queryset()

        context = view.get_context_data()
        grouped_vehicles = context["grouped_vehicles"]

        # Should have one fiscal year (2026)
        self.assertIn(2026, grouped_vehicles)

        # Should have three categories
        year_data = grouped_vehicles[2026]
        self.assertIn("TERRESTRE", year_data)
        self.assertIn("AERIEN", year_data)
        self.assertIn("MARITIME", year_data)

        print("✓ Grouping by fiscal year and category works correctly")

    def test_vehicle_identifier_extraction(self):
        """Test that correct identifiers are extracted"""
        view = DeclarationHistoryView()

        # Terrestrial vehicle
        identifier = view._get_vehicle_identifier(self.terrestrial_vehicle)
        self.assertEqual(identifier, "1234TAA")

        # Aerial vehicle
        identifier = view._get_vehicle_identifier(self.aerial_vehicle)
        self.assertEqual(identifier, "5R-ABC")

        # Maritime vehicle
        identifier = view._get_vehicle_identifier(self.maritime_vehicle)
        self.assertEqual(identifier, "Sea Breeze")

        print("✓ Vehicle identifier extraction works correctly")

    def test_export_csv_functionality(self):
        """Test CSV export functionality"""
        request = self.factory.get("/vehicles/history/export/?export=csv")
        request.user = self.user

        view = DeclarationHistoryExportView()
        view.request = request

        response = view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("attachment", response["Content-Disposition"])

        print("✓ CSV export works correctly")

    def test_action_buttons_logic(self):
        """Test that action buttons are shown correctly"""
        view = DeclarationHistoryView()

        # Test has_receipt
        has_receipt = view._has_receipt(self.terrestrial_vehicle)
        self.assertTrue(has_receipt)

        has_receipt = view._has_receipt(self.aerial_vehicle)
        self.assertFalse(has_receipt)

        print("✓ Action button logic works correctly")

    def test_action_buttons_for_paid_vehicle(self):
        """Test action buttons for paid vehicle (Requirements: 17.7)"""
        request = self.factory.get("/vehicles/history/")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        view.kwargs = {}
        view.object_list = view.get_queryset()

        context = view.get_context_data()
        grouped_vehicles = context["grouped_vehicles"]

        # Find the terrestrial vehicle (which has a paid payment)
        terrestrial_data = None
        for fiscal_year, categories in grouped_vehicles.items():
            for category, vehicles in categories.items():
                for vehicle_data in vehicles:
                    if vehicle_data["vehicule"].plaque_immatriculation == "1234TAA":
                        terrestrial_data = vehicle_data
                        break
                if terrestrial_data:
                    break
            if terrestrial_data:
                break

        self.assertIsNotNone(terrestrial_data)

        # Check payment status
        payment_status = terrestrial_data["payment_status"]
        self.assertIn(payment_status["status"], ["valid", "expiring_soon", "expired"])

        # Check has_receipt and has_qr_code flags
        self.assertTrue(terrestrial_data["has_receipt"])

        # Check that payment object exists
        self.assertIsNotNone(payment_status["payment"])

        print("✓ Action buttons for paid vehicle work correctly")

    def test_action_buttons_for_unpaid_vehicle(self):
        """Test action buttons for unpaid vehicle (Requirements: 17.7)"""
        request = self.factory.get("/vehicles/history/")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        view.kwargs = {}
        view.object_list = view.get_queryset()

        context = view.get_context_data()
        grouped_vehicles = context["grouped_vehicles"]

        # Find the aerial vehicle (which has no payment)
        aerial_data = None
        for fiscal_year, categories in grouped_vehicles.items():
            for category, vehicles in categories.items():
                for vehicle_data in vehicles:
                    if vehicle_data["vehicule"].plaque_immatriculation == "5678TAA":
                        aerial_data = vehicle_data
                        break
                if aerial_data:
                    break
            if aerial_data:
                break

        self.assertIsNotNone(aerial_data)

        # Check payment status
        payment_status = aerial_data["payment_status"]
        self.assertEqual(payment_status["status"], "unpaid")

        # Check has_receipt and has_qr_code flags
        self.assertFalse(aerial_data["has_receipt"])
        self.assertFalse(aerial_data["has_qr_code"])

        # Check that payment object is None
        self.assertIsNone(payment_status["payment"])

        print("✓ Action buttons for unpaid vehicle work correctly")

    def test_view_details_button_always_visible(self):
        """Test that view details button is always visible (Requirements: 17.7)"""
        request = self.factory.get("/vehicles/history/")
        request.user = self.user

        view = DeclarationHistoryView()
        view.request = request
        view.kwargs = {}
        view.object_list = view.get_queryset()

        context = view.get_context_data()
        grouped_vehicles = context["grouped_vehicles"]

        # Check all vehicles have the necessary data for details button
        for fiscal_year, categories in grouped_vehicles.items():
            for category, vehicles in categories.items():
                for vehicle_data in vehicles:
                    # Every vehicle should have a plaque_immatriculation for the details link
                    self.assertIsNotNone(vehicle_data["vehicule"].plaque_immatriculation)

        print("✓ View details button is always available for all vehicles")


def run_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Testing Declaration History Functionality")
    print("=" * 60 + "\n")

    from django.conf import settings
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=True)

    failures = test_runner.run_tests(["__main__"])

    if failures == 0:
        print("\n" + "=" * 60)
        print("✓ All declaration history tests passed!")
        print("=" * 60 + "\n")
    else:
        print("\n" + "=" * 60)
        print(f"✗ {failures} test(s) failed")
        print("=" * 60 + "\n")

    return failures


if __name__ == "__main__":
    run_tests()
