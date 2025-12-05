"""
Vehicle tax calculation services
"""

from decimal import Decimal

from django.utils import timezone

from .models import GrilleTarifaire


class TaxCalculationService:
    """Service for calculating vehicle taxes (terrestrial, aerial, maritime)"""

    def calculate_tax(self, vehicule, year=None):
        """
        Calculate tax information for a vehicle - routes to appropriate method based on category

        Args:
            vehicule: Vehicule instance
            year: Tax year (defaults to current year)

        Returns:
            dict: Tax calculation information
        """
        if year is None:
            year = timezone.now().year

        # Route to appropriate calculation method based on vehicle category
        if vehicule.vehicle_category == "TERRESTRE":
            return self.calculate_terrestrial_tax(vehicule, year)
        elif vehicule.vehicle_category == "AERIEN":
            return self.calculate_aerial_tax(vehicule, year)
        elif vehicule.vehicle_category == "MARITIME":
            return self.calculate_maritime_tax(vehicule, year)
        else:
            return {
                "is_exempt": False,
                "amount": None,
                "exemption_reason": None,
                "year": year,
                "grid": None,
                "error": f"Catégorie de véhicule inconnue: {vehicule.vehicle_category}",
            }

    def calculate_terrestrial_tax(self, vehicule, year=None):
        """
        Calculate tax for terrestrial vehicles using progressive grid

        Args:
            vehicule: Vehicule instance
            year: Tax year (defaults to current year)

        Returns:
            dict: Tax calculation information
        """
        if year is None:
            year = timezone.now().year

        # Check if vehicle is exempt
        if vehicule.est_exonere():
            return {
                "is_exempt": True,
                "amount": Decimal("0.00"),
                "exemption_reason": "Véhicule exonéré",
                "year": year,
                "grid": None,
            }

        # Find applicable tax grid
        try:
            tax_grids = GrilleTarifaire.objects.filter(
                annee_fiscale=year, est_active=True, grid_type="PROGRESSIVE"
            ).order_by("puissance_min_cv")

            applicable_grid = None
            for grid in tax_grids:
                if grid.est_applicable(vehicule):
                    applicable_grid = grid
                    break

            if applicable_grid:
                return {
                    "is_exempt": False,
                    "amount": applicable_grid.montant_ariary,
                    "exemption_reason": None,
                    "year": year,
                    "grid": applicable_grid,
                    "calculation_method": "Grille progressive (terrestre)",
                }
            else:
                return {
                    "is_exempt": False,
                    "amount": None,
                    "exemption_reason": None,
                    "year": year,
                    "grid": None,
                    "error": "Aucune grille tarifaire applicable trouvée",
                }

        except Exception as e:
            return {
                "is_exempt": False,
                "amount": None,
                "exemption_reason": None,
                "year": year,
                "grid": None,
                "error": f"Erreur lors du calcul: {str(e)}",
            }

    def calculate_aerial_tax(self, vehicule, year=None):
        """
        Calculate tax for aerial vehicles using flat rate (2,000,000 Ar)

        Args:
            vehicule: Vehicule instance
            year: Tax year (defaults to current year)

        Returns:
            dict: Tax calculation information
        """
        if year is None:
            year = timezone.now().year

        # Check if vehicle is exempt
        if vehicule.est_exonere():
            return {
                "is_exempt": True,
                "amount": Decimal("0.00"),
                "exemption_reason": "Véhicule exonéré",
                "year": year,
                "grid": None,
            }

        # Find flat aerial tax grid
        try:
            grid = GrilleTarifaire.objects.get(grid_type="FLAT_AERIAL", annee_fiscale=year, est_active=True)

            return {
                "is_exempt": False,
                "amount": grid.montant_ariary,
                "exemption_reason": None,
                "year": year,
                "grid": grid,
                "calculation_method": "Tarif forfaitaire aérien",
            }
        except GrilleTarifaire.DoesNotExist:
            return {
                "is_exempt": False,
                "amount": None,
                "exemption_reason": None,
                "year": year,
                "grid": None,
                "error": "Grille tarifaire aérienne non configurée pour cette année fiscale",
            }
        except Exception as e:
            return {
                "is_exempt": False,
                "amount": None,
                "exemption_reason": None,
                "year": year,
                "grid": None,
                "error": f"Erreur lors du calcul: {str(e)}",
            }

    def calculate_maritime_tax(self, vehicule, year=None):
        """
        Calculate tax for maritime vehicles using flat rate with automatic classification

        Args:
            vehicule: Vehicule instance
            year: Tax year (defaults to current year)

        Returns:
            dict: Tax calculation information including maritime classification
        """
        if year is None:
            year = timezone.now().year

        # Check if vehicle is exempt
        if vehicule.est_exonere():
            return {
                "is_exempt": True,
                "amount": Decimal("0.00"),
                "exemption_reason": "Véhicule exonéré",
                "year": year,
                "grid": None,
                "maritime_category": None,
            }

        # Classify maritime vehicle
        category = self._classify_maritime_vehicle(vehicule)

        # Find flat maritime tax grid for this category
        try:
            grid = GrilleTarifaire.objects.get(
                grid_type="FLAT_MARITIME", maritime_category=category, annee_fiscale=year, est_active=True
            )

            return {
                "is_exempt": False,
                "amount": grid.montant_ariary,
                "exemption_reason": None,
                "year": year,
                "grid": grid,
                "maritime_category": category,
                "calculation_method": f"Tarif forfaitaire maritime ({category})",
            }
        except GrilleTarifaire.DoesNotExist:
            return {
                "is_exempt": False,
                "amount": None,
                "exemption_reason": None,
                "year": year,
                "grid": None,
                "maritime_category": category,
                "error": f"Grille tarifaire maritime non configurée pour la catégorie {category}",
            }
        except Exception as e:
            return {
                "is_exempt": False,
                "amount": None,
                "exemption_reason": None,
                "year": year,
                "grid": None,
                "maritime_category": None,
                "error": f"Erreur lors du calcul: {str(e)}",
            }

    def _classify_maritime_vehicle(self, vehicule):
        """
        Classify a maritime vehicle according to PLFI thresholds

        Classification rules:
        - JETSKI: Jet-ski/moto nautique/scooter des mers with power ≥ 90 kW
        - NAVIRE_PLAISANCE: Length ≥ 7m OR power ≥ 22 CV OR power ≥ 90 kW
        - AUTRES_ENGINS: All other motorized maritime vehicles

        Args:
            vehicule: Vehicule instance

        Returns:
            str: Maritime category (NAVIRE_PLAISANCE, JETSKI, AUTRES_ENGINS)
        """
        longueur = vehicule.longueur_metres or Decimal("0")
        puissance_cv = vehicule.puissance_fiscale_cv or 0
        puissance_kw = vehicule.puissance_moteur_kw or Decimal("0")

        # Convert kW to CV if necessary (kW × 1.36)
        if puissance_kw > 0 and puissance_cv == 0:
            puissance_cv = float(puissance_kw) * 1.36

        # Get vehicle type name
        type_name = vehicule.type_vehicule.nom.lower() if vehicule.type_vehicule else ""

        # Check for jet-ski/moto nautique with power ≥ 90 kW
        jetski_keywords = ["jet", "moto nautique", "scooter"]
        if any(keyword in type_name for keyword in jetski_keywords):
            if puissance_kw >= 90:
                return "JETSKI"

        # Check for navire de plaisance: length ≥ 7m OR power ≥ 22 CV OR power ≥ 90 kW
        if longueur >= 7 or puissance_cv >= 22 or puissance_kw >= 90:
            return "NAVIRE_PLAISANCE"

        # All other motorized maritime vehicles
        return "AUTRES_ENGINS"

    def get_tax_breakdown(self, vehicule, year=None):
        """
        Get detailed tax breakdown for a vehicle

        Args:
            vehicule: Vehicule instance
            year: Tax year (defaults to current year)

        Returns:
            dict: Detailed tax breakdown
        """
        tax_info = self.calculate_tax(vehicule, year)

        breakdown = {
            "vehicle_info": {
                "plaque": vehicule.plaque_immatriculation,
                "puissance_fiscale": vehicule.puissance_fiscale_cv,
                "source_energie": vehicule.get_source_energie_display(),
                "age": vehicule.get_age_annees(),
                "categorie": vehicule.get_categorie_vehicule_display(),
            },
            "tax_info": tax_info,
        }

        if tax_info.get("grid"):
            grid = tax_info["grid"]
            breakdown["grid_info"] = {
                "puissance_min": grid.puissance_fiscale_min,
                "puissance_max": grid.puissance_fiscale_max,
                "age_min": grid.age_vehicule_min,
                "age_max": grid.age_vehicule_max,
                "source_energie": grid.source_energie,
                "montant": grid.montant_ariary,
            }

        return breakdown


# Power conversion utility functions
def convert_cv_to_kw(cv):
    """
    Convert horsepower (CV) to kilowatts (kW)
    Formula: kW = CV × 0.735

    Args:
        cv: Power in CV (horsepower)

    Returns:
        Decimal: Power in kW, rounded to 2 decimal places
    """
    if cv is None:
        return None

    cv_decimal = Decimal(str(cv))
    kw = cv_decimal * Decimal("0.735")
    return kw.quantize(Decimal("0.01"))


def convert_kw_to_cv(kw):
    """
    Convert kilowatts (kW) to horsepower (CV)
    Formula: CV = kW × 1.36

    Args:
        kw: Power in kW (kilowatts)

    Returns:
        Decimal: Power in CV, rounded to 2 decimal places
    """
    if kw is None:
        return None

    kw_decimal = Decimal(str(kw))
    cv = kw_decimal * Decimal("1.36")
    return cv.quantize(Decimal("0.01"))


def validate_power_conversion(cv, kw, tolerance_percent=1):
    """
    Validate the coherence of CV and kW values
    Checks if the conversion between CV and kW is within acceptable tolerance

    Args:
        cv: Power in CV (horsepower)
        kw: Power in kW (kilowatts)
        tolerance_percent: Acceptable tolerance percentage (default: 1%)

    Returns:
        tuple: (is_valid: bool, message: str or None)
    """
    if cv is None or kw is None:
        return True, None

    # Convert CV to kW and check against provided kW
    calculated_kw = convert_cv_to_kw(cv)

    # Calculate tolerance
    tolerance = Decimal(str(tolerance_percent)) / Decimal("100")
    max_difference = calculated_kw * tolerance

    # Check if difference is within tolerance
    difference = abs(calculated_kw - Decimal(str(kw)))

    if difference > max_difference:
        return False, (
            f"Incohérence détectée dans la conversion CV/kW. "
            f"Pour {cv} CV, la puissance devrait être environ {calculated_kw} kW, "
            f"mais {kw} kW a été fourni."
        )

    return True, None
