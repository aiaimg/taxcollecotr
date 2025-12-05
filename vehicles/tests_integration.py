"""
Integration tests for multi-vehicle tax declaration system.

These tests verify the complete flow from vehicle creation through tax calculation,
payment processing, and QR code generation for all vehicle categories.
"""

import time
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from notifications.models import Notification
from payments.models import PaiementTaxe, QRCode
from vehicles.models import GrilleTarifaire, VehicleType, Vehicule
from vehicles.services import TaxCalculationService


class BaseIntegrationTest(TestCase):
    """Base class for integration tests with common setup"""

    @staticmethod
    def generate_temp_plate(prefix="TEST"):
        """Generate a valid TEMP plate for testing"""
        import random
        import string

        chars = string.ascii_uppercase + string.digits
        remaining = 8 - len(prefix)
        if remaining < 0:
            prefix = prefix[:8]
            remaining = 0
        suffix = "".join(random.choices(chars, k=remaining))
        return f"TEMP-{prefix}{suffix}"

    def setUp(self):
        """Set up common test data"""
        # Create test user
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Create vehicle types
        self.type_voiture, _ = VehicleType.objects.get_or_create(
            nom="Voiture", defaults={"description": "Véhicule terrestre", "ordre_affichage": 1}
        )
        self.type_avion, _ = VehicleType.objects.get_or_create(
            nom="Avion", defaults={"description": "Aéronef à voilure fixe", "ordre_affichage": 100}
        )
        self.type_helicoptere, _ = VehicleType.objects.get_or_create(
            nom="Hélicoptère", defaults={"description": "Aéronef à voilure tournante", "ordre_affichage": 101}
        )
        self.type_bateau, _ = VehicleType.objects.get_or_create(
            nom="Bateau de plaisance", defaults={"description": "Embarcation de loisir", "ordre_affichage": 200}
        )
        self.type_jetski, _ = VehicleType.objects.get_or_create(
            nom="Jet-ski", defaults={"description": "Moto nautique", "ordre_affichage": 203}
        )

        # Create tax grids
        current_year = timezone.now().year

        # Terrestrial progressive grid
        self.grid_terrestrial = GrilleTarifaire.objects.create(
            grid_type="PROGRESSIVE",
            puissance_min_cv=5,
            puissance_max_cv=15,
            source_energie="Essence",
            age_min_annees=0,
            age_max_annees=5,
            montant_ariary=Decimal("60000"),
            annee_fiscale=current_year,
            est_active=True,
        )

        # Aerial flat rate grid
        self.grid_aerial = GrilleTarifaire.objects.create(
            grid_type="FLAT_AERIAL",
            aerial_type="ALL",
            montant_ariary=Decimal("2000000"),
            annee_fiscale=current_year,
            est_active=True,
        )

        # Maritime flat rate grids
        self.grid_maritime_navire = GrilleTarifaire.objects.create(
            grid_type="FLAT_MARITIME",
            maritime_category="NAVIRE_PLAISANCE",
            longueur_min_metres=Decimal("7.00"),
            puissance_min_cv_maritime=Decimal("22.00"),
            puissance_min_kw_maritime=Decimal("90.00"),
            montant_ariary=Decimal("200000"),
            annee_fiscale=current_year,
            est_active=True,
        )

        self.grid_maritime_jetski = GrilleTarifaire.objects.create(
            grid_type="FLAT_MARITIME",
            maritime_category="JETSKI",
            puissance_min_kw_maritime=Decimal("90.00"),
            montant_ariary=Decimal("200000"),
            annee_fiscale=current_year,
            est_active=True,
        )

        self.grid_maritime_autres = GrilleTarifaire.objects.create(
            grid_type="FLAT_MARITIME",
            maritime_category="AUTRES_ENGINS",
            montant_ariary=Decimal("1000000"),
            annee_fiscale=current_year,
            est_active=True,
        )

        self.service = TaxCalculationService()
        self.current_year = current_year


class AerialVehicleIntegrationTests(BaseIntegrationTest):
    """Integration tests for complete aerial vehicle declaration flow"""

    def test_complete_aerial_declaration_flow(self):
        """
        Test complete flow: Create aerial vehicle → Calculate tax → Create payment → Generate QR
        Requirements: 3.1-3.7, 5.3
        """
        # Step 1: Create aerial vehicle
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("AIR"),
            proprietaire=self.user,
            nom_proprietaire="Jean Dupont",
            marque="Cessna",
            modele="172",
            puissance_fiscale_cv=100,
            cylindree_cm3=5000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_avion,
            vehicle_category="AERIEN",
            immatriculation_aerienne="5R-ABC",
            masse_maximale_decollage_kg=1200,
            numero_serie_aeronef="17280123",
            puissance_moteur_kw=Decimal("120.50"),
        )

        self.assertEqual(vehicule.vehicle_category, "AERIEN")
        self.assertEqual(vehicule.immatriculation_aerienne, "5R-ABC")

        # Step 2: Calculate tax
        tax_info = self.service.calculate_aerial_tax(vehicule, self.current_year)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("2000000"))
        self.assertEqual(tax_info["calculation_method"], "Tarif forfaitaire aérien")
        self.assertIsNotNone(tax_info["grid"])

        # Step 3: Create payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=vehicule,
            annee_fiscale=self.current_year,
            montant_du_ariary=tax_info["amount"],
            statut="EN_ATTENTE",
            type_paiement="TAXE_VEHICULE",
        )

        self.assertEqual(payment.statut, "EN_ATTENTE")
        self.assertEqual(payment.montant_du_ariary, Decimal("2000000"))
        self.assertIsNotNone(payment.transaction_id)

        # Step 4: Simulate payment completion
        payment.statut = "PAYE"
        payment.montant_paye_ariary = tax_info["amount"]
        payment.date_paiement = timezone.now()
        payment.methode_paiement = "mvola"
        payment.save()

        self.assertTrue(payment.est_paye())

        # Step 5: Generate QR code
        qr_code = QRCode.objects.create(
            type_code="TAXE_VEHICULE", vehicule_plaque=vehicule, annee_fiscale=self.current_year
        )

        self.assertIsNotNone(qr_code.token)
        self.assertTrue(qr_code.est_actif)
        self.assertTrue(qr_code.est_valide())

        # Step 6: Verify notification was created (if notification system is active)
        # Note: This depends on signals being set up
        notifications = Notification.objects.filter(user=self.user, type_notification="VEHICLE_ADDED")
        # We don't assert here as notifications might be created via signals

        # Final verification: Complete flow worked
        self.assertTrue(vehicule.paiements.filter(statut="PAYE").exists())
        self.assertTrue(vehicule.qr_codes.filter(est_actif=True).exists())

    def test_aerial_vehicle_with_different_aircraft_types(self):
        """Test that all aircraft types receive the same 2M Ar tax"""
        aircraft_types = [
            (self.type_avion, "Avion", "AVI"),
            (self.type_helicoptere, "Hélicoptère", "HEL"),
        ]

        for vehicle_type, type_name, prefix in aircraft_types:
            with self.subTest(aircraft_type=type_name):
                vehicule = Vehicule.objects.create(
                    plaque_immatriculation=self.generate_temp_plate(prefix),
                    proprietaire=self.user,
                    nom_proprietaire="Test Owner",
                    marque="Test Manufacturer",
                    modele="Test Model",
                    puissance_fiscale_cv=100,
                    cylindree_cm3=5000,
                    source_energie="Essence",
                    date_premiere_circulation=date.today() - timedelta(days=365),
                    categorie_vehicule="Personnel",
                    type_vehicule=vehicle_type,
                    vehicle_category="AERIEN",
                    immatriculation_aerienne=f"5R-{prefix}",
                    masse_maximale_decollage_kg=5000,
                    numero_serie_aeronef=f"SN{prefix}123",
                )

                tax_info = self.service.calculate_aerial_tax(vehicule, self.current_year)

                self.assertEqual(tax_info["amount"], Decimal("2000000"), f"{type_name} should have 2M Ar tax")


class MaritimeVehicleIntegrationTests(BaseIntegrationTest):
    """Integration tests for complete maritime vehicle declaration flow"""

    def test_complete_maritime_declaration_navire_plaisance(self):
        """
        Test complete flow for navire de plaisance: Create → Classify → Calculate → Pay → QR
        Requirements: 4.1-4.7, 5.4, 10.1-10.7
        """
        # Step 1: Create maritime vehicle (navire de plaisance - length ≥ 7m)
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Marie Dubois",
            marque="Beneteau",
            modele="Oceanis 40",
            puissance_fiscale_cv=25,
            cylindree_cm3=3000,
            source_energie="Diesel",
            date_premiere_circulation=date.today() - timedelta(days=730),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-12345",
            nom_navire="Sea Breeze",
            longueur_metres=Decimal("8.50"),
            tonnage_tonneaux=Decimal("5.20"),
            puissance_moteur_kw=Decimal("18.38"),  # 25 CV * 0.735
        )

        self.assertEqual(vehicule.vehicle_category, "MARITIME")
        self.assertEqual(vehicule.numero_francisation, "FR-12345")

        # Step 2: Automatic classification
        classification = self.service._classify_maritime_vehicle(vehicule)

        self.assertEqual(classification, "NAVIRE_PLAISANCE")

        # Store classification in vehicle
        vehicule.specifications_techniques["maritime_classification"] = classification
        vehicule.save()

        # Step 3: Calculate tax
        tax_info = self.service.calculate_maritime_tax(vehicule, self.current_year)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("200000"))
        self.assertEqual(tax_info["maritime_category"], "NAVIRE_PLAISANCE")
        self.assertIn("Tarif forfaitaire maritime", tax_info["calculation_method"])

        # Step 4: Create payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=vehicule,
            annee_fiscale=self.current_year,
            montant_du_ariary=tax_info["amount"],
            statut="EN_ATTENTE",
            type_paiement="TAXE_VEHICULE",
        )

        self.assertEqual(payment.montant_du_ariary, Decimal("200000"))

        # Step 5: Complete payment
        payment.statut = "PAYE"
        payment.montant_paye_ariary = tax_info["amount"]
        payment.date_paiement = timezone.now()
        payment.methode_paiement = "cash"
        payment.save()

        self.assertTrue(payment.est_paye())

        # Step 6: Generate QR code
        qr_code = QRCode.objects.create(
            type_code="TAXE_VEHICULE",
            vehicule_plaque=vehicule,
            annee_fiscale=self.current_year,
            data={"maritime_classification": classification},
        )

        self.assertTrue(qr_code.est_valide())
        self.assertEqual(qr_code.data.get("maritime_classification"), "NAVIRE_PLAISANCE")

        # Final verification
        self.assertEqual(vehicule.specifications_techniques.get("maritime_classification"), "NAVIRE_PLAISANCE")
        self.assertTrue(vehicule.paiements.filter(statut="PAYE").exists())

    def test_complete_maritime_declaration_jetski(self):
        """
        Test complete flow for jet-ski: Create → Classify → Calculate → Pay → QR
        Requirements: 4.1-4.7, 5.4, 10.2
        """
        # Create jet-ski (power ≥ 90 kW)
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("JET"),
            proprietaire=self.user,
            nom_proprietaire="Pierre Martin",
            marque="Kawasaki",
            modele="Ultra 310",
            puissance_fiscale_cv=122,  # ~90 kW
            cylindree_cm3=1500,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_jetski,
            vehicle_category="MARITIME",
            numero_francisation="FR-JET01",
            nom_navire="Jet Racer",
            longueur_metres=Decimal("3.50"),
            tonnage_tonneaux=Decimal("0.50"),
            puissance_moteur_kw=Decimal("95.00"),
        )

        # Classification
        classification = self.service._classify_maritime_vehicle(vehicule)
        self.assertEqual(classification, "JETSKI")

        # Calculate tax
        tax_info = self.service.calculate_maritime_tax(vehicule, self.current_year)
        self.assertEqual(tax_info["amount"], Decimal("200000"))
        self.assertEqual(tax_info["maritime_category"], "JETSKI")

        # Create and complete payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=vehicule,
            annee_fiscale=self.current_year,
            montant_du_ariary=tax_info["amount"],
            statut="PAYE",
            montant_paye_ariary=tax_info["amount"],
            date_paiement=timezone.now(),
            methode_paiement="mvola",
            type_paiement="TAXE_VEHICULE",
        )

        # Generate QR
        qr_code = QRCode.objects.create(
            type_code="TAXE_VEHICULE", vehicule_plaque=vehicule, annee_fiscale=self.current_year
        )

        # Verify
        self.assertTrue(payment.est_paye())
        self.assertTrue(qr_code.est_valide())
        self.assertEqual(payment.montant_du_ariary, Decimal("200000"))

    def test_complete_maritime_declaration_autres_engins(self):
        """
        Test complete flow for autres engins: Create → Classify → Calculate → Pay → QR
        Requirements: 4.1-4.7, 5.4, 10.3
        """
        # Create small boat (< 7m and < 22 CV)
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("SML"),
            proprietaire=self.user,
            nom_proprietaire="Luc Bernard",
            marque="Zodiac",
            modele="Pro",
            puissance_fiscale_cv=10,
            cylindree_cm3=1000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-SMALL",
            nom_navire="Small Boat",
            longueur_metres=Decimal("5.00"),
            tonnage_tonneaux=Decimal("1.00"),
            puissance_moteur_kw=Decimal("7.35"),  # 10 CV * 0.735
        )

        # Classification
        classification = self.service._classify_maritime_vehicle(vehicule)
        self.assertEqual(classification, "AUTRES_ENGINS")

        # Calculate tax
        tax_info = self.service.calculate_maritime_tax(vehicule, self.current_year)
        self.assertEqual(tax_info["amount"], Decimal("1000000"))
        self.assertEqual(tax_info["maritime_category"], "AUTRES_ENGINS")

        # Create and complete payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=vehicule,
            annee_fiscale=self.current_year,
            montant_du_ariary=tax_info["amount"],
            statut="PAYE",
            montant_paye_ariary=tax_info["amount"],
            date_paiement=timezone.now(),
            methode_paiement="carte_bancaire",
            type_paiement="TAXE_VEHICULE",
        )

        # Generate QR
        qr_code = QRCode.objects.create(
            type_code="TAXE_VEHICULE", vehicule_plaque=vehicule, annee_fiscale=self.current_year
        )

        # Verify
        self.assertTrue(payment.est_paye())
        self.assertTrue(qr_code.est_valide())
        self.assertEqual(payment.montant_du_ariary, Decimal("1000000"))

    def test_maritime_classification_all_categories(self):
        """Test that all three maritime categories are correctly classified and taxed"""
        test_cases = [
            {
                "name": "NAVIRE_PLAISANCE by length",
                "longueur_metres": Decimal("8.00"),
                "puissance_cv": 15,
                "puissance_kw": Decimal("11.03"),
                "expected_category": "NAVIRE_PLAISANCE",
                "expected_amount": Decimal("200000"),
            },
            {
                "name": "NAVIRE_PLAISANCE by power",
                "longueur_metres": Decimal("6.00"),
                "puissance_cv": 25,
                "puissance_kw": Decimal("18.38"),
                "expected_category": "NAVIRE_PLAISANCE",
                "expected_amount": Decimal("200000"),
            },
            {
                "name": "JETSKI",
                "longueur_metres": Decimal("3.50"),
                "puissance_cv": 122,
                "puissance_kw": Decimal("95.00"),
                "expected_category": "JETSKI",
                "expected_amount": Decimal("200000"),
                "type_vehicule": self.type_jetski,
            },
            {
                "name": "AUTRES_ENGINS",
                "longueur_metres": Decimal("5.00"),
                "puissance_cv": 10,
                "puissance_kw": Decimal("7.35"),
                "expected_category": "AUTRES_ENGINS",
                "expected_amount": Decimal("1000000"),
            },
        ]

        for i, test_case in enumerate(test_cases):
            with self.subTest(case=test_case["name"]):
                vehicule = Vehicule.objects.create(
                    plaque_immatriculation=self.generate_temp_plate(f"TC{i}"),
                    proprietaire=self.user,
                    nom_proprietaire="Test Owner",
                    marque="Test",
                    modele="Model",
                    puissance_fiscale_cv=test_case["puissance_cv"],
                    cylindree_cm3=2000,
                    source_energie="Essence",
                    date_premiere_circulation=date.today() - timedelta(days=365),
                    categorie_vehicule="Personnel",
                    type_vehicule=test_case.get("type_vehicule", self.type_bateau),
                    vehicle_category="MARITIME",
                    numero_francisation=f"FR-TC{i}",
                    nom_navire=f"Test Boat {i}",
                    longueur_metres=test_case["longueur_metres"],
                    tonnage_tonneaux=Decimal("2.00"),
                    puissance_moteur_kw=test_case["puissance_kw"],
                )

                classification = self.service._classify_maritime_vehicle(vehicule)
                tax_info = self.service.calculate_maritime_tax(vehicule, self.current_year)

                self.assertEqual(classification, test_case["expected_category"])
                self.assertEqual(tax_info["amount"], test_case["expected_amount"])
                self.assertEqual(tax_info["maritime_category"], test_case["expected_category"])


class TerrestrialVehicleRegressionTests(BaseIntegrationTest):
    """Regression tests to ensure terrestrial vehicle functionality still works"""

    def test_terrestrial_vehicle_flow_unchanged(self):
        """
        Verify that terrestrial vehicles still work correctly after multi-vehicle changes
        Requirements: 2.1-2.7, 5.2
        """
        # Create terrestrial vehicle
        vehicule = Vehicule.objects.create(
            plaque_immatriculation="1234TAA",
            proprietaire=self.user,
            nom_proprietaire="Sophie Laurent",
            marque="Toyota",
            modele="Corolla",
            puissance_fiscale_cv=13,
            cylindree_cm3=1600,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=1095),  # 3 years
            categorie_vehicule="Personnel",
            type_vehicule=self.type_voiture,
            vehicle_category="TERRESTRE",
        )

        # Calculate tax using progressive grid
        tax_info = self.service.calculate_tax(vehicule, self.current_year)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("60000"))
        self.assertIsNotNone(tax_info["grid"])
        self.assertEqual(tax_info["grid"].grid_type, "PROGRESSIVE")

        # Create payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=vehicule,
            annee_fiscale=self.current_year,
            montant_du_ariary=tax_info["amount"],
            statut="PAYE",
            montant_paye_ariary=tax_info["amount"],
            date_paiement=timezone.now(),
            methode_paiement="mvola",
            type_paiement="TAXE_VEHICULE",
        )

        # Generate QR
        qr_code = QRCode.objects.create(
            type_code="TAXE_VEHICULE", vehicule_plaque=vehicule, annee_fiscale=self.current_year
        )

        # Verify everything works
        self.assertTrue(payment.est_paye())
        self.assertTrue(qr_code.est_valide())
        self.assertEqual(payment.montant_du_ariary, Decimal("60000"))

    def test_existing_terrestrial_payments_not_affected(self):
        """Verify that existing terrestrial vehicle payments remain valid"""
        # Create terrestrial vehicle with existing payment
        vehicule = Vehicule.objects.create(
            plaque_immatriculation="5678TBA",
            proprietaire=self.user,
            nom_proprietaire="Marc Durand",
            marque="Renault",
            modele="Clio",
            puissance_fiscale_cv=13,
            cylindree_cm3=1400,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=730),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_voiture,
            vehicle_category="TERRESTRE",
        )

        # Create existing payment (from previous year)
        last_year = self.current_year - 1
        old_payment = PaiementTaxe.objects.create(
            vehicule_plaque=vehicule,
            annee_fiscale=last_year,
            montant_du_ariary=Decimal("55000"),
            statut="PAYE",
            montant_paye_ariary=Decimal("55000"),
            date_paiement=timezone.now() - timedelta(days=200),
            methode_paiement="mvola",
            type_paiement="TAXE_VEHICULE",
        )

        # Verify old payment is still valid
        self.assertTrue(old_payment.est_paye())
        self.assertEqual(old_payment.annee_fiscale, last_year)

        # Create new payment for current year
        new_payment = PaiementTaxe.objects.create(
            vehicule_plaque=vehicule,
            annee_fiscale=self.current_year,
            montant_du_ariary=Decimal("60000"),
            statut="PAYE",
            montant_paye_ariary=Decimal("60000"),
            date_paiement=timezone.now(),
            methode_paiement="mvola",
            type_paiement="TAXE_VEHICULE",
        )

        # Verify both payments exist and are valid
        self.assertEqual(vehicule.paiements.filter(statut="PAYE").count(), 2)
        self.assertTrue(new_payment.est_paye())

    def test_existing_qr_codes_still_valid(self):
        """Verify that existing QR codes for terrestrial vehicles remain valid"""
        # Create terrestrial vehicle
        vehicule = Vehicule.objects.create(
            plaque_immatriculation="9012TCA",
            proprietaire=self.user,
            nom_proprietaire="Anne Petit",
            marque="Peugeot",
            modele="208",
            puissance_fiscale_cv=13,
            cylindree_cm3=1200,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_voiture,
            vehicle_category="TERRESTRE",
        )

        # Create payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=vehicule,
            annee_fiscale=self.current_year,
            montant_du_ariary=Decimal("60000"),
            statut="PAYE",
            montant_paye_ariary=Decimal("60000"),
            date_paiement=timezone.now(),
            methode_paiement="cash",
            type_paiement="TAXE_VEHICULE",
        )

        # Create QR code
        qr_code = QRCode.objects.create(
            type_code="TAXE_VEHICULE", vehicule_plaque=vehicule, annee_fiscale=self.current_year
        )

        # Verify QR code is valid
        self.assertTrue(qr_code.est_valide())
        self.assertTrue(qr_code.est_actif)
        self.assertIsNotNone(qr_code.token)

        # Simulate QR code scan
        qr_code.increment_scan_count()
        self.assertEqual(qr_code.nombre_scans, 1)
        self.assertIsNotNone(qr_code.derniere_verification)


class PerformanceTests(BaseIntegrationTest):
    """Performance tests for multi-vehicle operations"""

    def test_maritime_classification_performance(self):
        """
        Test that classifying 1000 maritime vehicles takes less than 1 second
        Requirements: Performance
        """
        # Create 1000 maritime vehicles with varying characteristics
        vehicles = []
        for i in range(1000):
            # Vary characteristics to test different classification paths
            if i % 3 == 0:
                # NAVIRE_PLAISANCE
                longueur = Decimal("8.00")
                puissance_cv = 25
                puissance_kw = Decimal("18.38")
            elif i % 3 == 1:
                # JETSKI
                longueur = Decimal("3.50")
                puissance_cv = 122
                puissance_kw = Decimal("95.00")
            else:
                # AUTRES_ENGINS
                longueur = Decimal("5.00")
                puissance_cv = 10
                puissance_kw = Decimal("7.35")

            vehicule = Vehicule(
                plaque_immatriculation=self.generate_temp_plate(f"P{i:04d}"),
                proprietaire=self.user,
                nom_proprietaire="Performance Test",
                marque="Test",
                modele="Model",
                puissance_fiscale_cv=puissance_cv,
                cylindree_cm3=2000,
                source_energie="Essence",
                date_premiere_circulation=date.today() - timedelta(days=365),
                categorie_vehicule="Personnel",
                type_vehicule=self.type_bateau,
                vehicle_category="MARITIME",
                numero_francisation=f"FR-P{i:04d}",
                nom_navire=f"Perf Test {i}",
                longueur_metres=longueur,
                tonnage_tonneaux=Decimal("2.00"),
                puissance_moteur_kw=puissance_kw,
            )
            vehicles.append(vehicule)

        # Bulk create for efficiency
        Vehicule.objects.bulk_create(vehicles)

        # Measure classification time
        start_time = time.time()

        for vehicule in Vehicule.objects.filter(vehicle_category="MARITIME"):
            self.service._classify_maritime_vehicle(vehicule)

        duration = time.time() - start_time

        # Should classify 1000 vehicles in less than 1 second
        self.assertLess(duration, 1.0, f"Classification took {duration:.2f}s, should be < 1.0s")

    def test_tax_calculation_bulk_performance(self):
        """
        Test that calculating taxes for 300 mixed vehicles takes less than 2 seconds
        Requirements: Performance
        """
        vehicles = []

        # Create 100 of each type
        for i in range(100):
            # Aerial vehicle
            vehicles.append(
                Vehicule(
                    plaque_immatriculation=self.generate_temp_plate(f"A{i:03d}"),
                    proprietaire=self.user,
                    nom_proprietaire="Bulk Test",
                    marque="Test",
                    modele="Aerial",
                    puissance_fiscale_cv=100,
                    cylindree_cm3=5000,
                    source_energie="Essence",
                    date_premiere_circulation=date.today() - timedelta(days=365),
                    categorie_vehicule="Personnel",
                    type_vehicule=self.type_avion,
                    vehicle_category="AERIEN",
                    immatriculation_aerienne=f"5R-A{i:03d}",
                    masse_maximale_decollage_kg=5000,
                    numero_serie_aeronef=f"SNA{i:03d}",
                )
            )

            # Maritime vehicle
            vehicles.append(
                Vehicule(
                    plaque_immatriculation=self.generate_temp_plate(f"M{i:03d}"),
                    proprietaire=self.user,
                    nom_proprietaire="Bulk Test",
                    marque="Test",
                    modele="Maritime",
                    puissance_fiscale_cv=25,
                    cylindree_cm3=3000,
                    source_energie="Diesel",
                    date_premiere_circulation=date.today() - timedelta(days=365),
                    categorie_vehicule="Personnel",
                    type_vehicule=self.type_bateau,
                    vehicle_category="MARITIME",
                    numero_francisation=f"FR-M{i:03d}",
                    nom_navire=f"Boat {i}",
                    longueur_metres=Decimal("8.00"),
                    tonnage_tonneaux=Decimal("5.00"),
                    puissance_moteur_kw=Decimal("18.38"),
                )
            )

            # Terrestrial vehicle
            vehicles.append(
                Vehicule(
                    plaque_immatriculation=f"{i:04d}TAA",
                    proprietaire=self.user,
                    nom_proprietaire="Bulk Test",
                    marque="Test",
                    modele="Terrestrial",
                    puissance_fiscale_cv=8,
                    cylindree_cm3=1600,
                    source_energie="Essence",
                    date_premiere_circulation=date.today() - timedelta(days=1095),
                    categorie_vehicule="Personnel",
                    type_vehicule=self.type_voiture,
                    vehicle_category="TERRESTRE",
                )
            )

        # Bulk create
        Vehicule.objects.bulk_create(vehicles)

        # Measure tax calculation time
        start_time = time.time()

        for vehicule in Vehicule.objects.all():
            self.service.calculate_tax(vehicule, self.current_year)

        duration = time.time() - start_time

        # Should calculate 300 taxes in less than 2 seconds
        self.assertLess(duration, 2.0, f"Tax calculation took {duration:.2f}s, should be < 2.0s")

    def test_vehicle_list_loading_performance(self):
        """
        Test that loading a list of 1000 vehicles takes less than 3 seconds
        Requirements: Performance
        """
        vehicles = []

        # Create 1000 mixed vehicles
        for i in range(1000):
            if i % 3 == 0:
                # Aerial
                vehicles.append(
                    Vehicule(
                        plaque_immatriculation=self.generate_temp_plate(f"L{i:04d}"),
                        proprietaire=self.user,
                        nom_proprietaire="Load Test",
                        marque="Test",
                        modele="Model",
                        puissance_fiscale_cv=100,
                        cylindree_cm3=5000,
                        source_energie="Essence",
                        date_premiere_circulation=date.today() - timedelta(days=365),
                        categorie_vehicule="Personnel",
                        type_vehicule=self.type_avion,
                        vehicle_category="AERIEN",
                        immatriculation_aerienne=f"5R-L{i:04d}",
                        masse_maximale_decollage_kg=5000,
                    )
                )
            elif i % 3 == 1:
                # Maritime
                vehicles.append(
                    Vehicule(
                        plaque_immatriculation=self.generate_temp_plate(f"L{i:04d}"),
                        proprietaire=self.user,
                        nom_proprietaire="Load Test",
                        marque="Test",
                        modele="Model",
                        puissance_fiscale_cv=25,
                        cylindree_cm3=3000,
                        source_energie="Diesel",
                        date_premiere_circulation=date.today() - timedelta(days=365),
                        categorie_vehicule="Personnel",
                        type_vehicule=self.type_bateau,
                        vehicle_category="MARITIME",
                        numero_francisation=f"FR-L{i:04d}",
                        nom_navire=f"Boat {i}",
                        longueur_metres=Decimal("8.00"),
                    )
                )
            else:
                # Terrestrial
                vehicles.append(
                    Vehicule(
                        plaque_immatriculation=f"{i:04d}TLA",
                        proprietaire=self.user,
                        nom_proprietaire="Load Test",
                        marque="Test",
                        modele="Model",
                        puissance_fiscale_cv=8,
                        cylindree_cm3=1600,
                        source_energie="Essence",
                        date_premiere_circulation=date.today() - timedelta(days=1095),
                        categorie_vehicule="Personnel",
                        type_vehicule=self.type_voiture,
                        vehicle_category="TERRESTRE",
                    )
                )

        # Bulk create
        Vehicule.objects.bulk_create(vehicles)

        # Measure query time with select_related and prefetch_related
        start_time = time.time()

        queryset = (
            Vehicule.objects.select_related("proprietaire", "type_vehicule")
            .prefetch_related("paiements", "qr_codes")
            .all()
        )

        # Force evaluation
        list(queryset)

        duration = time.time() - start_time

        # Should load 1000 vehicles in less than 3 seconds
        self.assertLess(duration, 3.0, f"Vehicle list loading took {duration:.2f}s, should be < 3.0s")


class MixedVehicleIntegrationTests(BaseIntegrationTest):
    """Integration tests with mixed vehicle types"""

    def test_user_with_multiple_vehicle_types(self):
        """Test a user with terrestrial, aerial, and maritime vehicles"""
        # Create one of each type
        terrestrial = Vehicule.objects.create(
            plaque_immatriculation="1111TAA",
            proprietaire=self.user,
            nom_proprietaire="Multi Owner",
            marque="Toyota",
            modele="Corolla",
            puissance_fiscale_cv=13,
            cylindree_cm3=1600,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=1095),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_voiture,
            vehicle_category="TERRESTRE",
        )

        aerial = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MIX1"),
            proprietaire=self.user,
            nom_proprietaire="Multi Owner",
            marque="Cessna",
            modele="172",
            puissance_fiscale_cv=100,
            cylindree_cm3=5000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_avion,
            vehicle_category="AERIEN",
            immatriculation_aerienne="5R-MIX",
            masse_maximale_decollage_kg=1200,
        )

        maritime = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MIX2"),
            proprietaire=self.user,
            nom_proprietaire="Multi Owner",
            marque="Beneteau",
            modele="Oceanis",
            puissance_fiscale_cv=25,
            cylindree_cm3=3000,
            source_energie="Diesel",
            date_premiere_circulation=date.today() - timedelta(days=730),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-MIX",
            nom_navire="Mixed Fleet",
            longueur_metres=Decimal("8.50"),
            puissance_moteur_kw=Decimal("18.38"),
        )

        # Calculate taxes for all
        tax_terrestrial = self.service.calculate_tax(terrestrial, self.current_year)
        tax_aerial = self.service.calculate_tax(aerial, self.current_year)
        tax_maritime = self.service.calculate_tax(maritime, self.current_year)

        # Verify correct amounts
        self.assertEqual(tax_terrestrial["amount"], Decimal("60000"))
        self.assertEqual(tax_aerial["amount"], Decimal("2000000"))
        self.assertEqual(tax_maritime["amount"], Decimal("200000"))

        # Verify user has all three vehicles
        user_vehicles = Vehicule.objects.filter(proprietaire=self.user)
        self.assertEqual(user_vehicles.count(), 3)
        self.assertEqual(user_vehicles.filter(vehicle_category="TERRESTRE").count(), 1)
        self.assertEqual(user_vehicles.filter(vehicle_category="AERIEN").count(), 1)
        self.assertEqual(user_vehicles.filter(vehicle_category="MARITIME").count(), 1)

        # Calculate total tax burden
        total_tax = tax_terrestrial["amount"] + tax_aerial["amount"] + tax_maritime["amount"]
        self.assertEqual(total_tax, Decimal("2260000"))
