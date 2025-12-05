from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import GrilleTarifaire, VehicleType, Vehicule
from .services import TaxCalculationService, convert_cv_to_kw, convert_kw_to_cv, validate_power_conversion


class TaxCalculationServiceTests(TestCase):
    """Tests for the TaxCalculationService"""

    @staticmethod
    def generate_temp_plate(prefix="TEST"):
        """Generate a valid TEMP plate for testing (TEMP-XXXXXXXX format)"""
        import random
        import string

        chars = string.ascii_uppercase + string.digits
        # Generate 8 characters total (prefix + random)
        remaining = 8 - len(prefix)
        if remaining < 0:
            prefix = prefix[:8]
            remaining = 0
        suffix = "".join(random.choices(chars, k=remaining))
        return f"TEMP-{prefix}{suffix}"

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create vehicle types
        self.type_voiture, _ = VehicleType.objects.get_or_create(
            nom="Voiture", defaults={"description": "Véhicule terrestre", "ordre_affichage": 1}
        )
        self.type_avion, _ = VehicleType.objects.get_or_create(
            nom="Avion", defaults={"description": "Aéronef à voilure fixe", "ordre_affichage": 100}
        )
        self.type_bateau, _ = VehicleType.objects.get_or_create(
            nom="Bateau de plaisance", defaults={"description": "Embarcation de loisir", "ordre_affichage": 200}
        )
        self.type_jetski, _ = VehicleType.objects.get_or_create(
            nom="Jet-ski", defaults={"description": "Moto nautique", "ordre_affichage": 203}
        )

        # Create tax grids
        current_year = timezone.now().year

        # Terrestrial progressive grids
        self.grid_terrestrial_low = GrilleTarifaire.objects.create(
            grid_type="PROGRESSIVE",
            puissance_min_cv=5,
            puissance_max_cv=10,
            source_energie="Essence",
            age_min_annees=0,
            age_max_annees=5,
            montant_ariary=Decimal("60000"),
            annee_fiscale=current_year,
            est_active=True,
        )

        self.grid_terrestrial_high = GrilleTarifaire.objects.create(
            grid_type="PROGRESSIVE",
            puissance_min_cv=11,
            puissance_max_cv=15,
            source_energie="Essence",
            age_min_annees=0,
            age_max_annees=5,
            montant_ariary=Decimal("80000"),
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

    def test_calculate_aerial_tax_returns_2m_ar(self):
        """Test that aerial tax always returns 2,000,000 Ar"""
        # Create aerial vehicle
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("AIR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Boeing",
            modele="737",
            puissance_fiscale_cv=1000,
            cylindree_cm3=10000,  # Large enough to match CV
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_avion,
            vehicle_category="AERIEN",
            immatriculation_aerienne="5R-ABC",
            masse_maximale_decollage_kg=50000,
            numero_serie_aeronef="ABC123",
        )

        tax_info = self.service.calculate_aerial_tax(vehicule)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("2000000"))
        self.assertEqual(tax_info["calculation_method"], "Tarif forfaitaire aérien")
        self.assertIsNotNone(tax_info["grid"])

    def test_calculate_maritime_tax_navire_plaisance_by_length(self):
        """Test maritime tax for navire de plaisance (length ≥ 7m)"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Beneteau",
            modele="Oceanis",
            puissance_fiscale_cv=15,
            cylindree_cm3=1000,
            source_energie="Diesel",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-12345",
            nom_navire="Sea Breeze",
            longueur_metres=Decimal("8.50"),
            puissance_moteur_kw=Decimal("50.00"),
        )

        tax_info = self.service.calculate_maritime_tax(vehicule)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("200000"))
        self.assertEqual(tax_info["maritime_category"], "NAVIRE_PLAISANCE")

    def test_calculate_maritime_tax_navire_plaisance_by_power_cv(self):
        """Test maritime tax for navire de plaisance (power ≥ 22 CV)"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Yamaha",
            modele="Marine",
            puissance_fiscale_cv=25,
            cylindree_cm3=3000,  # Adjusted for maritime
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-12346",
            nom_navire="Speed Boat",
            longueur_metres=Decimal("6.00"),
            puissance_moteur_kw=Decimal("18.38"),  # 25 CV * 0.735
        )

        tax_info = self.service.calculate_maritime_tax(vehicule)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("200000"))
        self.assertEqual(tax_info["maritime_category"], "NAVIRE_PLAISANCE")

    def test_calculate_maritime_tax_jetski(self):
        """Test maritime tax for jet-ski (power ≥ 90 kW)"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Kawasaki",
            modele="Ultra 310",
            puissance_fiscale_cv=122,  # ~90 kW
            cylindree_cm3=1000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_jetski,
            vehicle_category="MARITIME",
            numero_francisation="FR-12347",
            nom_navire="Jet Racer",
            longueur_metres=Decimal("3.50"),
            puissance_moteur_kw=Decimal("95.00"),
        )

        tax_info = self.service.calculate_maritime_tax(vehicule)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("200000"))
        self.assertEqual(tax_info["maritime_category"], "JETSKI")

    def test_calculate_maritime_tax_autres_engins(self):
        """Test maritime tax for autres engins (small boats)"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Zodiac",
            modele="Pro",
            puissance_fiscale_cv=10,
            cylindree_cm3=1000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-12348",
            nom_navire="Small Boat",
            longueur_metres=Decimal("5.00"),
            puissance_moteur_kw=Decimal("7.35"),  # 10 CV * 0.735
        )

        tax_info = self.service.calculate_maritime_tax(vehicule)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("1000000"))
        self.assertEqual(tax_info["maritime_category"], "AUTRES_ENGINS")

    def test_classify_maritime_vehicle_edge_case_7m(self):
        """Test classification at exactly 7m threshold"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Test",
            modele="Boat",
            puissance_fiscale_cv=10,
            cylindree_cm3=1000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-12349",
            nom_navire="Edge Case",
            longueur_metres=Decimal("7.00"),  # Exactly at threshold
            puissance_moteur_kw=Decimal("7.35"),
        )

        classification = self.service._classify_maritime_vehicle(vehicule)
        self.assertEqual(classification, "NAVIRE_PLAISANCE")

    def test_classify_maritime_vehicle_edge_case_22cv(self):
        """Test classification at exactly 22 CV threshold"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Test",
            modele="Boat",
            puissance_fiscale_cv=22,  # Exactly at threshold
            cylindree_cm3=1000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-12350",
            nom_navire="Edge Case 2",
            longueur_metres=Decimal("5.00"),
            puissance_moteur_kw=Decimal("16.17"),
        )

        classification = self.service._classify_maritime_vehicle(vehicule)
        self.assertEqual(classification, "NAVIRE_PLAISANCE")

    def test_classify_maritime_vehicle_kw_conversion(self):
        """Test classification with kW to CV conversion"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Test",
            modele="Boat",
            puissance_fiscale_cv=1,  # No CV provided
            cylindree_cm3=1000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-12351",
            nom_navire="kW Only",
            longueur_metres=Decimal("5.00"),
            puissance_moteur_kw=Decimal("95.00"),  # Should convert to ~129 CV
        )

        classification = self.service._classify_maritime_vehicle(vehicule)
        # 95 kW * 1.36 = 129.2 CV, which is ≥ 22 CV
        self.assertEqual(classification, "NAVIRE_PLAISANCE")

    def test_calculate_tax_routes_to_terrestrial(self):
        """Test that calculate_tax routes to terrestrial method"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation="1234TAA",
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Toyota",
            modele="Corolla",
            puissance_fiscale_cv=13,
            cylindree_cm3=1800,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_voiture,
            vehicle_category="TERRESTRE",
        )

        tax_info = self.service.calculate_tax(vehicule)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("80000"))  # 13 CV falls in 11-15 CV range

    def test_calculate_tax_routes_to_aerial(self):
        """Test that calculate_tax routes to aerial method"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("AIR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Cessna",
            modele="172",
            puissance_fiscale_cv=100,
            cylindree_cm3=1000,
            source_energie="Essence",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_avion,
            vehicle_category="AERIEN",
            immatriculation_aerienne="5R-XYZ",
            masse_maximale_decollage_kg=1200,
        )

        tax_info = self.service.calculate_tax(vehicule)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("2000000"))

    def test_calculate_tax_routes_to_maritime(self):
        """Test that calculate_tax routes to maritime method"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("MAR"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Beneteau",
            modele="First",
            puissance_fiscale_cv=30,
            cylindree_cm3=1000,
            source_energie="Diesel",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Personnel",
            type_vehicule=self.type_bateau,
            vehicle_category="MARITIME",
            numero_francisation="FR-12352",
            nom_navire="Sailor",
            longueur_metres=Decimal("9.00"),
        )

        tax_info = self.service.calculate_tax(vehicule)

        self.assertFalse(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("200000"))
        self.assertEqual(tax_info["maritime_category"], "NAVIRE_PLAISANCE")

    def test_exempt_vehicle_returns_zero(self):
        """Test that exempt vehicles return zero tax"""
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=self.generate_temp_plate("AMB"),
            proprietaire=self.user,
            nom_proprietaire="Test Owner",
            marque="Mercedes",
            modele="Sprinter",
            puissance_fiscale_cv=15,
            cylindree_cm3=2200,
            source_energie="Diesel",
            date_premiere_circulation=date.today() - timedelta(days=365),
            categorie_vehicule="Ambulance",  # Exempt category
            type_vehicule=self.type_voiture,
            vehicle_category="TERRESTRE",
        )

        tax_info = self.service.calculate_tax(vehicule)

        self.assertTrue(tax_info["is_exempt"])
        self.assertEqual(tax_info["amount"], Decimal("0.00"))
        self.assertEqual(tax_info["exemption_reason"], "Véhicule exonéré")


class PowerConversionTests(TestCase):
    """Tests for power conversion utility functions"""

    def test_convert_cv_to_kw(self):
        """Test CV to kW conversion"""
        # 22 CV should be ~16.17 kW
        result = convert_cv_to_kw(22)
        self.assertEqual(result, Decimal("16.17"))

    def test_convert_kw_to_cv(self):
        """Test kW to CV conversion"""
        # 90 kW should be ~122.4 CV
        result = convert_kw_to_cv(90)
        self.assertEqual(result, Decimal("122.40"))

    def test_convert_cv_to_kw_with_decimal(self):
        """Test CV to kW conversion with decimal input"""
        result = convert_cv_to_kw(Decimal("100"))
        self.assertEqual(result, Decimal("73.50"))

    def test_convert_kw_to_cv_with_decimal(self):
        """Test kW to CV conversion with decimal input"""
        result = convert_kw_to_cv(Decimal("100"))
        self.assertEqual(result, Decimal("136.00"))

    def test_convert_none_returns_none(self):
        """Test that None input returns None"""
        self.assertIsNone(convert_cv_to_kw(None))
        self.assertIsNone(convert_kw_to_cv(None))

    def test_power_conversion_roundtrip(self):
        """Test round-trip conversion CV -> kW -> CV"""
        original_cv = Decimal("50")
        kw = convert_cv_to_kw(original_cv)
        cv_back = convert_kw_to_cv(kw)

        # Should be very close (within 1%)
        tolerance = original_cv * Decimal("0.01")
        self.assertAlmostEqual(float(original_cv), float(cv_back), delta=float(tolerance))

    def test_validate_power_conversion_valid(self):
        """Test validation of valid CV/kW pair"""
        cv = 22
        kw = 16.17  # 22 * 0.735 = 16.17

        is_valid, message = validate_power_conversion(cv, kw)

        self.assertTrue(is_valid)
        self.assertIsNone(message)

    def test_validate_power_conversion_invalid(self):
        """Test validation of invalid CV/kW pair"""
        cv = 22
        kw = 50  # Way off from expected 16.17

        is_valid, message = validate_power_conversion(cv, kw)

        self.assertFalse(is_valid)
        self.assertIsNotNone(message)
        self.assertIn("Incohérence", message)

    def test_validate_power_conversion_with_none(self):
        """Test validation with None values"""
        is_valid, message = validate_power_conversion(None, 50)
        self.assertTrue(is_valid)

        is_valid, message = validate_power_conversion(22, None)
        self.assertTrue(is_valid)

        is_valid, message = validate_power_conversion(None, None)
        self.assertTrue(is_valid)

    def test_validate_power_conversion_within_tolerance(self):
        """Test validation within 1% tolerance"""
        cv = 100
        kw_exact = 73.5  # 100 * 0.735
        kw_within_tolerance = 73.8  # Within 1%

        is_valid, message = validate_power_conversion(cv, kw_within_tolerance)
        self.assertTrue(is_valid)


class VehiculeAerienFormTests(TestCase):
    """Tests for VehiculeAerienForm"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create aerial vehicle types
        self.type_avion, _ = VehicleType.objects.get_or_create(
            nom="Avion", defaults={"description": "Aéronef à voilure fixe", "ordre_affichage": 100}
        )
        self.type_helicoptere, _ = VehicleType.objects.get_or_create(
            nom="Hélicoptère", defaults={"description": "Aéronef à voilure tournante", "ordre_affichage": 101}
        )

    def test_form_validates_immatriculation_format_valid(self):
        """Test validation of valid aerial registration format"""
        from vehicles.forms import VehiculeAerienForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "immatriculation_aerienne": "5R-ABC",
            "type_vehicule": self.type_avion.id,
            "marque": "Cessna",
            "modele": "172",
            "numero_serie_aeronef": "17280123",
            "masse_maximale_decollage_kg": 1200,
            "puissance_moteur_kw": 120.5,
            "cylindree_cm3": 1000,  # Optional for aerial
            "source_energie": "Essence",  # Optional for aerial
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeAerienForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data["immatriculation_aerienne"], "5R-ABC")

    def test_form_validates_immatriculation_format_invalid(self):
        """Test validation of invalid aerial registration format"""
        from vehicles.forms import VehiculeAerienForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "immatriculation_aerienne": "INVALID",
            "type_vehicule": self.type_avion.id,
            "marque": "Cessna",
            "modele": "172",
            "numero_serie_aeronef": "17280123",
            "masse_maximale_decollage_kg": 1200,
            "puissance_moteur_kw": 120.5,
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeAerienForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("immatriculation_aerienne", form.errors)

    def test_form_validates_masse_maximale_min_limit(self):
        """Test validation of minimum mass limit"""
        from vehicles.forms import VehiculeAerienForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "immatriculation_aerienne": "5R-ABC",
            "type_vehicule": self.type_avion.id,
            "marque": "Cessna",
            "modele": "172",
            "numero_serie_aeronef": "17280123",
            "masse_maximale_decollage_kg": 5,  # Below minimum
            "puissance_moteur_kw": 120.5,
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeAerienForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("masse_maximale_decollage_kg", form.errors)

    def test_form_validates_masse_maximale_max_limit(self):
        """Test validation of maximum mass limit"""
        from vehicles.forms import VehiculeAerienForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "immatriculation_aerienne": "5R-ABC",
            "type_vehicule": self.type_avion.id,
            "marque": "Cessna",
            "modele": "172",
            "numero_serie_aeronef": "17280123",
            "masse_maximale_decollage_kg": 600000,  # Above maximum
            "puissance_moteur_kw": 120.5,
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeAerienForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("masse_maximale_decollage_kg", form.errors)

    def test_form_auto_sets_vehicle_category_aerien(self):
        """Test that form automatically sets vehicle_category to AERIEN"""
        from vehicles.forms import VehiculeAerienForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "immatriculation_aerienne": "5R-ABC",
            "type_vehicule": self.type_avion.id,
            "marque": "Cessna",
            "modele": "172",
            "numero_serie_aeronef": "17280123",
            "masse_maximale_decollage_kg": 1200,
            "puissance_moteur_kw": 120.5,
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeAerienForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["vehicle_category"], "AERIEN")


class VehiculeMaritimeFormTests(TestCase):
    """Tests for VehiculeMaritimeForm"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create maritime vehicle types
        self.type_bateau, _ = VehicleType.objects.get_or_create(
            nom="Bateau de plaisance", defaults={"description": "Embarcation de loisir", "ordre_affichage": 200}
        )
        self.type_jetski, _ = VehicleType.objects.get_or_create(
            nom="Jet-ski", defaults={"description": "Moto nautique", "ordre_affichage": 203}
        )

    def test_form_validates_francisation_format_valid(self):
        """Test validation of valid francisation format"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 8.5,
            "tonnage_tonneaux": 5.2,
            "puissance_fiscale_cv": 25,
            "cylindree_cm3": 3000,  # Add cylindree for form compatibility
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data["numero_francisation"], "FR-12345")

    def test_form_validates_francisation_format_invalid(self):
        """Test validation of invalid francisation format"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "INVALID@#$",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 8.5,
            "tonnage_tonneaux": 5.2,
            "puissance_fiscale_cv": 25,
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("numero_francisation", form.errors)

    def test_form_validates_longueur_min_limit(self):
        """Test validation of minimum length limit"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 0.5,  # Below minimum
            "tonnage_tonneaux": 5.2,
            "puissance_fiscale_cv": 25,
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("longueur_metres", form.errors)

    def test_form_validates_longueur_max_limit(self):
        """Test validation of maximum length limit"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 450,  # Above maximum
            "tonnage_tonneaux": 5.2,
            "puissance_fiscale_cv": 25,
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("longueur_metres", form.errors)

    def test_form_converts_cv_to_kw_automatically(self):
        """Test automatic conversion from CV to kW"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 8.5,
            "tonnage_tonneaux": 5.2,
            "puissance_fiscale_cv": 22,
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # Check that kW was calculated (22 CV * 0.735 = 16.17 kW)
        self.assertIsNotNone(form.cleaned_data["puissance_moteur_kw"])
        self.assertAlmostEqual(float(form.cleaned_data["puissance_moteur_kw"]), 16.17, places=2)

    def test_form_converts_kw_to_cv_automatically(self):
        """Test automatic conversion from kW to CV"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 8.5,
            "tonnage_tonneaux": 5.2,
            "puissance_moteur_kw": 90,
            "puissance_moteur_unit": "kW",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # Check that CV was calculated (90 kW * 1.36 = 122.4 CV)
        self.assertIsNotNone(form.cleaned_data["puissance_fiscale_cv"])
        self.assertEqual(form.cleaned_data["puissance_fiscale_cv"], 122)

    def test_form_detects_incoherent_conversion(self):
        """Test detection of incoherent CV/kW conversion"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 8.5,
            "tonnage_tonneaux": 5.2,
            "puissance_fiscale_cv": 22,
            "puissance_moteur_kw": 50,  # Should be ~16.17, not 50
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        # Should have errors on both power fields
        self.assertTrue("puissance_fiscale_cv" in form.errors or "puissance_moteur_kw" in form.errors)

    def test_form_classification_navire_plaisance(self):
        """Test automatic classification for navire de plaisance"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 8.5,  # ≥ 7m
            "tonnage_tonneaux": 5.2,
            "puissance_fiscale_cv": 15,
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        classification = form.get_maritime_classification()
        self.assertEqual(classification, "NAVIRE_PLAISANCE")

    def test_form_classification_jetski(self):
        """Test automatic classification for jet-ski"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Jet Racer",
            "type_vehicule": self.type_jetski.id,
            "marque": "Kawasaki",
            "modele": "Ultra 310",
            "longueur_metres": 3.5,
            "tonnage_tonneaux": 0.5,
            "puissance_moteur_kw": 95,  # ≥ 90 kW
            "puissance_moteur_unit": "kW",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        classification = form.get_maritime_classification()
        self.assertEqual(classification, "JETSKI")

    def test_form_classification_autres_engins(self):
        """Test automatic classification for autres engins"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Small Boat",
            "type_vehicule": self.type_bateau.id,
            "marque": "Zodiac",
            "modele": "Pro",
            "longueur_metres": 5.0,  # < 7m
            "tonnage_tonneaux": 1.0,
            "puissance_fiscale_cv": 10,  # < 22 CV
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        classification = form.get_maritime_classification()
        self.assertEqual(classification, "AUTRES_ENGINS")

    def test_form_auto_sets_vehicle_category_maritime(self):
        """Test that form automatically sets vehicle_category to MARITIME"""
        from vehicles.forms import VehiculeMaritimeForm

        form_data = {
            "nom_proprietaire": "Jean Dupont",
            "numero_francisation": "FR-12345",
            "nom_navire": "Sea Breeze",
            "type_vehicule": self.type_bateau.id,
            "marque": "Beneteau",
            "modele": "Oceanis 40",
            "longueur_metres": 8.5,
            "tonnage_tonneaux": 5.2,
            "puissance_fiscale_cv": 25,
            "puissance_moteur_unit": "CV",
            "date_premiere_circulation": date.today() - timedelta(days=365),
            "categorie_vehicule": "Personnel",
        }

        form = VehiculeMaritimeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["vehicle_category"], "MARITIME")
