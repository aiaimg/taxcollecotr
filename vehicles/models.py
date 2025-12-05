import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from .utils import get_plage_cv_description, get_puissance_fiscale_from_cylindree, valider_coherence_cylindree_cv

# Constantes pour les catégories exonérées (selon PLF 2026, Article 02.09.03)
EXEMPT_VEHICLE_CATEGORIES = [
    "Convention_internationale",
    "Ambulance",
    "Sapeurs-pompiers",
    "Administratif",
]


class VehicleType(models.Model):
    """Dynamic vehicle type model to replace fixed choices"""

    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du type de véhicule",
        help_text="Ex: Voiture, Moto, Scooter, Camionnette, etc.",
    )
    description = models.TextField(
        blank=True, verbose_name="Description", help_text="Description optionnelle du type de véhicule"
    )
    est_actif = models.BooleanField(
        default=True, verbose_name="Est actif", help_text="Décochez pour désactiver ce type de véhicule"
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0, verbose_name="Ordre d'affichage", help_text="Ordre d'affichage dans les listes (0 = premier)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Type de véhicule"
        verbose_name_plural = "Types de véhicules"
        ordering = ["ordre_affichage", "nom"]
        indexes = [
            models.Index(fields=["est_actif"]),
            models.Index(fields=["ordre_affichage"]),
        ]

    def __str__(self):
        return self.nom

    @classmethod
    def get_active_types(cls):
        """Retourne tous les types de véhicules actifs"""
        return cls.objects.filter(est_actif=True).order_by("ordre_affichage", "nom")


class Vehicule(models.Model):
    """Vehicle model supporting all types (terrestrial, railway, maritime, aerial)"""

    SOURCE_ENERGIE_CHOICES = [
        ("Essence", "Essence"),
        ("Diesel", "Diesel"),
        ("Electrique", "Électrique"),
        ("Hybride", "Hybride"),
    ]

    CATEGORIE_CHOICES = [
        ("Personnel", "Personnel"),
        ("Commercial", "Commercial"),
        ("Ambulance", "Ambulance"),
        ("Sapeurs-pompiers", "Sapeurs-pompiers"),
        ("Administratif", "Administratif"),
        ("Convention_internationale", "Convention internationale"),
    ]

    VEHICLE_CATEGORY_CHOICES = [
        ("TERRESTRE", "Terrestre"),
        ("AERIEN", "Aérien"),
        ("MARITIME", "Maritime"),
    ]

    STATUT_DECLARATION_CHOICES = [
        ("BROUILLON", "Brouillon"),
        ("SOUMISE", "Soumise"),
        ("VALIDEE", "Validée"),
        ("REJETEE", "Rejetée"),
    ]

    # Vehicle types are now dynamic through VehicleType model

    plaque_immatriculation = models.CharField(
        max_length=20,
        primary_key=True,
        validators=[
            RegexValidator(
                r"^([0-9]{1,4}[A-Z]{2,3}|TEMP-[A-Z0-9]{8})$",
                "Format: 1234TAA (sans espace) ou TEMP-XXXXXXXX pour véhicules sans plaque",
            )
        ],
        verbose_name="Plaque d'immatriculation ou Identifiant",
        help_text="Format: 1234TAA (sans espace). Pour les véhicules sans plaque, utilisez TEMP-XXXXXXXX",
    )
    a_plaque_immatriculation = models.BooleanField(
        default=True,
        verbose_name="Possède une plaque d'immatriculation",
        help_text="Décochez pour les motos ou véhicules sans plaque officielle",
    )
    # User who manages this vehicle in the system (e.g., testuser1)
    proprietaire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicules",
        verbose_name="Utilisateur gestionnaire",
        help_text="L'utilisateur qui gère ce véhicule dans le système",
    )
    # Actual legal owner of the vehicle (e.g., Samoela)
    nom_proprietaire = models.CharField(
        max_length=200,
        default="",
        blank=True,
        verbose_name="Nom du propriétaire",
        help_text="Nom complet du propriétaire légal du véhicule",
    )

    # Essential vehicle details (from carte grise)
    marque = models.CharField(
        max_length=100, default="", verbose_name="Marque", help_text="Marque du véhicule (ex: TOYOTA, HONDA, YAMAHA)"
    )
    modele = models.CharField(
        max_length=100, blank=True, verbose_name="Modèle", help_text="Modèle du véhicule (ex: COROLLA, CIVIC, YZF)"
    )
    couleur = models.CharField(
        max_length=50, blank=True, verbose_name="Couleur", help_text="Couleur principale du véhicule"
    )
    vin = models.CharField(
        max_length=50, blank=True, verbose_name="VIN", help_text="Vehicle Identification Number (Numéro de châssis)"
    )

    puissance_fiscale_cv = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Puissance Fiscale (en CV)",
        help_text="Trouvez cette information sur votre carte grise. Elle est utilisée pour le calcul de la taxe.",
    )
    cylindree_cm3 = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cylindrée (en Cm3 ou cc)",
        help_text="Ex: 110 pour un scooter, 1900 pour une voiture",
        default=1000,  # Default value for existing records (typical small car engine)
    )
    source_energie = models.CharField(max_length=20, choices=SOURCE_ENERGIE_CHOICES, verbose_name="Source d'énergie")
    date_premiere_circulation = models.DateField(verbose_name="Date de première circulation")
    categorie_vehicule = models.CharField(
        max_length=50, choices=CATEGORIE_CHOICES, default="Personnel", verbose_name="Catégorie de véhicule"
    )
    type_vehicule = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
        verbose_name="Type de véhicule",
        help_text="Type spécifique du véhicule (Voiture, Moto, Scooter, etc.)",
        related_name="vehicules",
    )
    specifications_techniques = models.JSONField(default=dict, blank=True, verbose_name="Spécifications techniques")

    # Vehicle category (terrestrial, aerial, maritime)
    vehicle_category = models.CharField(
        max_length=20,
        choices=VEHICLE_CATEGORY_CHOICES,
        default="TERRESTRE",
        verbose_name="Catégorie de véhicule",
        help_text="Type général du véhicule (terrestre, aérien ou maritime)",
    )

    # Declaration status
    statut_declaration = models.CharField(
        max_length=20,
        choices=STATUT_DECLARATION_CHOICES,
        default="BROUILLON",
        verbose_name="Statut de la déclaration",
        help_text="État d'avancement de la déclaration fiscale",
    )

    # Aerial vehicle specific fields
    immatriculation_aerienne = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Numéro d'immatriculation aérienne",
        help_text="Ex: 5R-ABC pour Madagascar",
    )
    masse_maximale_decollage_kg = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Masse maximale au décollage (kg)",
        help_text="Masse maximale autorisée au décollage en kilogrammes",
    )
    numero_serie_aeronef = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Numéro de série de l'aéronef",
        help_text="Numéro de série constructeur de l'aéronef",
    )

    # Maritime vehicle specific fields
    numero_francisation = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Numéro de francisation",
        help_text="Numéro officiel de francisation du navire",
    )
    nom_navire = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Nom du navire",
        help_text="Nom officiel du navire ou de l'embarcation",
    )
    longueur_metres = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Longueur (mètres)",
        help_text="Longueur totale du navire en mètres",
    )
    tonnage_tonneaux = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Tonnage (tonneaux)",
        help_text="Tonnage du navire en tonneaux",
    )
    puissance_moteur_kw = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Puissance moteur (kW)",
        help_text="Puissance du moteur en kilowatts",
    )

    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        indexes = [
            models.Index(fields=["proprietaire"]),
            models.Index(fields=["categorie_vehicule"]),
            models.Index(fields=["type_vehicule"]),
            models.Index(fields=["source_energie"]),
            models.Index(fields=["puissance_fiscale_cv"]),
            models.Index(fields=["vehicle_category"], name="idx_vehicle_category"),
            models.Index(fields=["immatriculation_aerienne"], name="idx_immat_aerienne"),
            models.Index(fields=["numero_francisation"], name="idx_francisation"),
            models.Index(fields=["statut_declaration"], name="idx_statut_declaration"),
        ]

    def __str__(self):
        display_parts = []
        if self.a_plaque_immatriculation:
            display_parts.append(self.plaque_immatriculation)
        else:
            display_parts.append(f"Sans plaque ({self.plaque_immatriculation})")

        if self.marque:
            display_parts.append(self.marque)

        if self.nom_proprietaire:
            display_parts.append(self.nom_proprietaire)

        return " - ".join(display_parts)

    @staticmethod
    def generate_temp_plate():
        """Generate a temporary plate number for vehicles without registration"""
        import random
        import string

        chars = string.ascii_uppercase + string.digits
        temp_id = "".join(random.choices(chars, k=8))
        return f"TEMP-{temp_id}"

    @staticmethod
    def normalize_plate(plate):
        """Normalize plate number by removing spaces and converting to uppercase"""
        if not plate:
            return plate
        # Remove all spaces and convert to uppercase
        return plate.replace(" ", "").upper()

    def get_display_plate(self):
        """Get display-friendly plate number with space for readability"""
        if not self.a_plaque_immatriculation:
            return f"Sans plaque ({self.plaque_immatriculation})"

        plate = self.plaque_immatriculation
        # Format: 1234TAA -> 1234 TAA (add space before letters)
        if plate.startswith("TEMP-"):
            return plate

        # Find where letters start
        import re

        match = re.match(r"^(\d+)([A-Z]+)$", plate)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return plate

    def get_age_annees(self):
        """Calculate vehicle age in years"""
        today = timezone.now().date()
        return today.year - self.date_premiere_circulation.year

    def est_exonere(self):
        """
        Vérifie si le véhicule est exonéré de taxe selon l'Article 02.09.03 du PLF 2026.

        Catégories exonérées:
        1. Les véhicules non soumis à taxation en vertu des conventions internationales
        2. Les véhicules de catégorie "ambulance" et "sapeurs-pompiers"
        3. Les véhicules administratifs
        """
        return self.categorie_vehicule in EXEMPT_VEHICLE_CATEGORIES

    def auto_determine_puissance_fiscale(self):
        """
        Détermine automatiquement la puissance fiscale à partir de la cylindrée
        """
        return get_puissance_fiscale_from_cylindree(self.cylindree_cm3)

    def get_plage_cv_description(self):
        """
        Retourne la description de la plage de CV pour cette cylindrée
        """
        return get_plage_cv_description(self.cylindree_cm3)

    def clean(self):
        """
        Validation personnalisée pour vérifier la cohérence cylindrée/CV
        """
        super().clean()

        # Normalize plate number (remove spaces)
        if self.plaque_immatriculation:
            self.plaque_immatriculation = self.normalize_plate(self.plaque_immatriculation)

        # Only validate CV/cylindrée coherence for terrestrial vehicles
        if self.vehicle_category == "TERRESTRE" and self.cylindree_cm3 and self.puissance_fiscale_cv:
            est_coherent, message = valider_coherence_cylindree_cv(self.cylindree_cm3, self.puissance_fiscale_cv)
            if not est_coherent:
                raise ValidationError({"puissance_fiscale_cv": message})

    def save(self, *args, **kwargs):
        """
        Sauvegarde avec validation automatique et normalisation
        """
        # Normalize plate before validation and saving
        if self.plaque_immatriculation:
            self.plaque_immatriculation = self.normalize_plate(self.plaque_immatriculation)
            
        self.full_clean()
        super().save(*args, **kwargs)

    def get_current_payment_status(self):
        """
        Get payment status for current year
        Returns: dict with status, payment, days_until_expiry, is_expired
        """
        from datetime import date

        from payments.models import PaiementTaxe

        current_year = timezone.now().year
        current_date = timezone.now().date()

        # Check if vehicle is exempt
        if self.est_exonere():
            return {
                "status": "exempt",
                "payment": None,
                "days_until_expiry": None,
                "is_expired": False,
                "expiry_date": None,
            }

        # Get current year payment (check all statuses including EN_ATTENTE)
        payment = (
            PaiementTaxe.objects.filter(vehicule_plaque=self, annee_fiscale=current_year)
            .exclude(statut="ANNULE")
            .first()
        )

        if not payment:
            return {
                "status": "unpaid",
                "payment": None,
                "days_until_expiry": None,
                "is_expired": False,
                "expiry_date": None,
            }

        # Check if payment is pending (EN_ATTENTE)
        if payment.statut == "EN_ATTENTE":
            return {
                "status": "pending",
                "payment": payment,
                "days_until_expiry": None,
                "is_expired": False,
                "expiry_date": None,
            }

        # Payment is PAYE or EXONERE, but check if date_paiement exists
        if not payment.date_paiement:
            return {
                "status": "pending",
                "payment": payment,
                "days_until_expiry": None,
                "is_expired": False,
                "expiry_date": None,
            }

        # Calculate expiry date (1 year from payment date)
        payment_date = payment.date_paiement.date() if hasattr(payment.date_paiement, "date") else payment.date_paiement
        expiry_date = payment_date.replace(year=payment_date.year + 1)
        days_until_expiry = (expiry_date - current_date).days

        if days_until_expiry <= 0:
            status = "expired"
            is_expired = True
        elif days_until_expiry <= 30:
            status = "expiring_soon"
            is_expired = False
        else:
            status = "valid"
            is_expired = False

        return {
            "status": status,
            "payment": payment,
            "days_until_expiry": days_until_expiry,
            "is_expired": is_expired,
            "expiry_date": expiry_date,
        }

    @property
    def is_paid(self):
        """
        Check if vehicle has a paid payment for current year
        Returns True if payment exists and is PAYE or EXONERE
        Note: Exempt vehicles should use est_exonere() method, not is_paid
        """
        # Don't check payment status for exempt vehicles
        if self.est_exonere():
            return False

        status_info = self.get_current_payment_status()
        # Only return True for valid, expiring_soon, or expired payments (not pending or unpaid)
        return status_info["status"] in ["valid", "expiring_soon", "expired"]

    @property
    def has_pending_payment(self):
        """
        Check if vehicle has a pending payment (EN_ATTENTE) for current year
        """
        status_info = self.get_current_payment_status()
        return status_info["status"] == "pending"

    @property
    def current_payment(self):
        """
        Get current year payment if exists
        """
        from payments.models import PaiementTaxe

        current_year = timezone.now().year
        return (
            PaiementTaxe.objects.filter(vehicule_plaque=self, annee_fiscale=current_year)
            .exclude(statut="ANNULE")
            .first()
        )

    def needs_payment_reminder(self):
        """Check if vehicle needs a payment reminder"""
        status_info = self.get_current_payment_status()
        return status_info["status"] in ["unpaid", "expiring_soon", "expired"]

    def get_payment_status_badge(self):
        """Get HTML badge for payment status"""
        status_info = self.get_current_payment_status()
        status = status_info["status"]

        if status == "exempt":
            return '<span class="badge bg-info"><i class="ri-shield-check-line me-1"></i>Exonéré</span>'
        elif status == "valid":
            return '<span class="badge bg-success"><i class="ri-check-line me-1"></i>Payé</span>'
        elif status == "pending":
            return '<span class="badge bg-warning text-dark"><i class="ri-time-line me-1"></i>En attente</span>'
        elif status == "expiring_soon":
            days = status_info["days_until_expiry"]
            return (
                f'<span class="badge bg-warning text-dark"><i class="ri-time-line me-1"></i>Expire dans {days}j</span>'
            )
        elif status == "expired":
            return '<span class="badge bg-danger"><i class="ri-close-line me-1"></i>Expiré</span>'
        else:  # unpaid
            return '<span class="badge bg-warning text-dark"><i class="ri-alert-line me-1"></i>Taxe à payer</span>'

    def get_required_documents_by_category(self):
        """
        Return list of required document types based on vehicle_category.

        Returns:
            list: List of document type codes required for this vehicle category
        """
        if self.vehicle_category == "TERRESTRE":
            return ["carte_grise", "assurance", "controle_technique"]
        elif self.vehicle_category == "AERIEN":
            return ["certificat_navigabilite", "certificat_immatriculation_aerienne", "assurance_aerienne"]
        elif self.vehicle_category == "MARITIME":
            return ["certificat_francisation", "permis_navigation", "assurance_maritime"]
        else:
            # Default to terrestrial if category is unknown
            return ["carte_grise", "assurance", "controle_technique"]

    def validate_required_documents(self):
        """
        Validate that all required documents for this vehicle category are uploaded.

        Returns:
            tuple: (is_valid: bool, missing_documents: list)
                - is_valid: True if all required documents are present, False otherwise
                - missing_documents: List of missing document type codes with their display names
        """
        required_doc_types = self.get_required_documents_by_category()

        # Get all uploaded documents for this vehicle
        uploaded_doc_types = set(self.documents.values_list("document_type", flat=True))

        # Find missing documents
        missing_doc_types = [doc_type for doc_type in required_doc_types if doc_type not in uploaded_doc_types]

        # Get display names for missing documents
        from vehicles.models import DocumentVehicule

        doc_choices_dict = dict(DocumentVehicule.DOCUMENT_TYPE_CHOICES)
        missing_documents = [
            {"code": doc_type, "name": doc_choices_dict.get(doc_type, doc_type)} for doc_type in missing_doc_types
        ]

        is_valid = len(missing_documents) == 0

        return is_valid, missing_documents


class GrilleTarifaire(models.Model):
    """Tax grid for calculating vehicle taxes"""

    SOURCE_ENERGIE_CHOICES = [
        ("Essence", "Essence"),
        ("Diesel", "Diesel"),
        ("Electrique", "Électrique"),
        ("Hybride", "Hybride"),
    ]

    GRID_TYPE_CHOICES = [
        ("PROGRESSIVE", "Progressive (Terrestre)"),
        ("FLAT_AERIAL", "Forfaitaire Aérien"),
        ("FLAT_MARITIME", "Forfaitaire Maritime"),
    ]

    MARITIME_CATEGORY_CHOICES = [
        ("NAVIRE_PLAISANCE", "Navire de plaisance ≥7m ou ≥22CV/90kW"),
        ("JETSKI", "Jet-ski/moto nautique ≥90kW"),
        ("AUTRES_ENGINS", "Autres engins maritimes motorisés"),
    ]

    AERIAL_TYPE_CHOICES = [
        ("ALL", "Tous types d'aéronefs"),
        ("AVION", "Avion"),
        ("HELICOPTERE", "Hélicoptère"),
        ("DRONE", "Drone"),
        ("ULM", "ULM"),
        ("PLANEUR", "Planeur"),
        ("BALLON", "Ballon"),
    ]

    # Grid type (progressive for terrestrial, flat for aerial/maritime)
    grid_type = models.CharField(
        max_length=20,
        choices=GRID_TYPE_CHOICES,
        default="PROGRESSIVE",
        verbose_name="Type de grille",
        help_text="Type de grille tarifaire (progressive pour terrestres, forfaitaire pour aériens/maritimes)",
    )

    # Progressive grid fields (for terrestrial vehicles)
    puissance_min_cv = models.PositiveIntegerField(null=True, blank=True, verbose_name="Puissance min (CV)")
    puissance_max_cv = models.PositiveIntegerField(null=True, blank=True, verbose_name="Puissance max (CV)")
    source_energie = models.CharField(
        max_length=20, choices=SOURCE_ENERGIE_CHOICES, null=True, blank=True, verbose_name="Source d'énergie"
    )
    age_min_annees = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="Âge minimum (années)")
    age_max_annees = models.PositiveIntegerField(null=True, blank=True, verbose_name="Âge maximum (années)")

    # Flat rate fields (for aerial/maritime vehicles)
    maritime_category = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=MARITIME_CATEGORY_CHOICES,
        verbose_name="Catégorie maritime",
        help_text="Catégorie spécifique pour les véhicules maritimes",
    )
    aerial_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=AERIAL_TYPE_CHOICES,
        verbose_name="Type d'aéronef",
        help_text="Type spécifique d'aéronef (ALL pour tous types)",
    )

    # Maritime threshold fields
    longueur_min_metres = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Longueur minimale (mètres)",
        help_text="Seuil de longueur minimale pour cette catégorie maritime",
    )
    puissance_min_cv_maritime = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Puissance minimale (CV)",
        help_text="Seuil de puissance minimale en CV pour cette catégorie maritime",
    )
    puissance_min_kw_maritime = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Puissance minimale (kW)",
        help_text="Seuil de puissance minimale en kW pour cette catégorie maritime",
    )

    # Common fields
    montant_ariary = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], verbose_name="Montant (Ariary)"
    )
    annee_fiscale = models.PositiveIntegerField(verbose_name="Année fiscale")
    est_active = models.BooleanField(default=True, verbose_name="Est active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Grille tarifaire"
        verbose_name_plural = "Grilles tarifaires"
        indexes = [
            models.Index(fields=["annee_fiscale", "est_active"]),
            models.Index(fields=["puissance_min_cv", "puissance_max_cv", "source_energie"]),
            models.Index(fields=["grid_type"], name="idx_grid_type"),
            models.Index(fields=["maritime_category"], name="idx_maritime_category"),
            models.Index(fields=["aerial_type"], name="idx_aerial_type"),
        ]

    def __str__(self):
        puissance_range = f"{self.puissance_min_cv}"
        if self.puissance_max_cv:
            puissance_range += f"-{self.puissance_max_cv}"
        else:
            puissance_range += "+"

        age_range = f"{self.age_min_annees}"
        if self.age_max_annees:
            age_range += f"-{self.age_max_annees}"
        else:
            age_range += "+"

        return f"{puissance_range}CV {self.source_energie} {age_range}ans - {self.montant_ariary} Ar ({self.annee_fiscale})"

    def est_applicable(self, vehicule):
        """Check if this tax rate applies to a vehicle"""
        # Check power range
        if vehicule.puissance_fiscale_cv < self.puissance_min_cv:
            return False
        if self.puissance_max_cv and vehicule.puissance_fiscale_cv > self.puissance_max_cv:
            return False

        # Check energy source
        if vehicule.source_energie != self.source_energie:
            return False

        # Check age range
        age = vehicule.get_age_annees()
        if age < self.age_min_annees:
            return False
        if self.age_max_annees and age > self.age_max_annees:
            return False

        return True

    # Properties for template compatibility
    @property
    def rate(self):
        """Rate amount in Ariary (for template compatibility)"""
        return self.montant_ariary

    @property
    def name(self):
        """Grid name (for template compatibility)"""
        return f"{self.puissance_min_cv}CV {self.source_energie}"

    @property
    def code(self):
        """Grid code (for template compatibility)"""
        return f"GT-{self.puissance_min_cv}-{self.source_energie}"

    @property
    def fiscal_year(self):
        """Fiscal year (for template compatibility)"""
        return self.annee_fiscale

    @property
    def energy_source(self):
        """Energy source (for template compatibility)"""
        return self.source_energie

    @property
    def vehicle_category(self):
        """Vehicle category (for template compatibility)"""
        return "All Vehicles"  # Default since we don't have this field

    @property
    def is_active(self):
        """Active status (for template compatibility)"""
        return self.est_active

    @property
    def effective_date(self):
        """Effective date (for template compatibility)"""
        return self.created_at.date()

    @property
    def description(self):
        """Description (for template compatibility)"""
        age_range = f"{self.age_min_annees}"
        if self.age_max_annees:
            age_range += f"-{self.age_max_annees}"
        else:
            age_range += "+"

        puissance_range = f"{self.puissance_min_cv}"
        if self.puissance_max_cv:
            puissance_range += f"-{self.puissance_max_cv}"
        else:
            puissance_range += "+"

        return f"Tax rate for {puissance_range}CV {self.source_energie} vehicles, age {age_range} years"


class DocumentVehicule(models.Model):
    """Documents liés à un véhicule (carte grise, assurance, contrôle technique, etc.)"""

    DOCUMENT_TYPE_CHOICES = [
        # Terrestrial vehicle documents
        ("carte_grise", "Carte grise"),
        ("assurance", "Assurance"),
        ("controle_technique", "Contrôle technique"),
        ("photo_plaque", "Photo de la plaque"),
        # Aerial vehicle documents
        ("certificat_navigabilite", "Certificat de navigabilité"),
        ("certificat_immatriculation_aerienne", "Certificat d'immatriculation aérienne"),
        ("assurance_aerienne", "Assurance aérienne"),
        ("carnet_vol", "Carnet de vol"),
        # Maritime vehicle documents
        ("certificat_francisation", "Certificat de francisation"),
        ("permis_navigation", "Permis de navigation"),
        ("assurance_maritime", "Assurance maritime"),
        ("certificat_jaugeage", "Certificat de jaugeage"),
        # Common
        ("autre", "Autre document"),
    ]
    VERIFICATION_STATUS_CHOICES = [
        ("soumis", "Soumis"),
        ("verifie", "Vérifié"),
        ("rejete", "Rejeté"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicle_documents")
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    fichier = models.FileField(upload_to="vehicle_documents/%Y/%m/%d")
    note = models.TextField(blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default="soumis")
    verification_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document du véhicule"
        verbose_name_plural = "Documents du véhicule"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["vehicule"]),
            models.Index(fields=["document_type"]),
            models.Index(fields=["verification_status"]),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.vehicule.plaque_immatriculation}"

    def save(self, *args, **kwargs):
        """Override save to optimize images before saving"""
        # Check if this is an image file
        if self.fichier and hasattr(self.fichier, "file"):
            file_name = self.fichier.name.lower()
            image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]

            if any(file_name.endswith(ext) for ext in image_extensions):
                try:
                    from core.utils.image_optimizer import ImageOptimizer

                    # Optimize based on document type
                    if self.document_type in ["carte_grise", "assurance", "controle_technique"]:
                        # High quality for official documents
                        optimized = ImageOptimizer.optimize_document(self.fichier, document_type=self.document_type)
                    elif self.document_type == "photo_plaque":
                        # Medium quality for photos
                        optimized = ImageOptimizer.optimize_image(
                            self.fichier, max_width=1600, max_height=1200, quality=88
                        )
                    else:
                        # Default optimization
                        optimized = ImageOptimizer.optimize_image(self.fichier)

                    self.fichier = optimized

                except Exception as e:
                    # Log error but don't block save
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.error(f"Error optimizing vehicle document image: {str(e)}")

        super().save(*args, **kwargs)


class FleetImportBatch(models.Model):
    STATUTS = (
        ("PENDING", "PENDING"),
        ("PROCESSING", "PROCESSING"),
        ("COMPLETED", "COMPLETED"),
        ("FAILED", "FAILED"),
        ("ROLLED_BACK", "ROLLED_BACK"),
    )
    utilisateur = models.ForeignKey(User, on_delete=models.PROTECT)
    nom_fichier = models.CharField(max_length=255)
    type_fichier = models.CharField(max_length=16)
    mapping_colonnes = models.JSONField(default=dict)
    options = models.JSONField(default=dict)
    statut = models.CharField(max_length=16, choices=STATUTS, default="PENDING")
    total_lignes = models.PositiveIntegerField(default=0)
    reussites = models.PositiveIntegerField(default=0)
    echecs = models.PositiveIntegerField(default=0)
    cree_le = models.DateTimeField(auto_now_add=True)
    termine_le = models.DateTimeField(null=True, blank=True)
    resume_erreurs = models.TextField(blank=True)


class FleetImportRow(models.Model):
    STATUTS = (
        ("PENDING", "PENDING"),
        ("SUCCESS", "SUCCESS"),
        ("ERROR", "ERROR"),
        ("SKIPPED", "SKIPPED"),
    )
    lot = models.ForeignKey(FleetImportBatch, on_delete=models.CASCADE, related_name="lignes")
    numero_ligne = models.PositiveIntegerField()
    donnees = models.JSONField(default=dict)
    erreurs = models.JSONField(default=list)
    statut = models.CharField(max_length=16, choices=STATUTS, default="PENDING")
    vehicule = models.ForeignKey(Vehicule, null=True, blank=True, on_delete=models.SET_NULL)


class FleetAuditLog(models.Model):
    action_type = models.CharField(max_length=64)
    utilisateur = models.ForeignKey(User, on_delete=models.PROTECT)
    vehicule = models.ForeignKey(Vehicule, null=True, blank=True, on_delete=models.SET_NULL)
    lot_import = models.ForeignKey(FleetImportBatch, null=True, blank=True, on_delete=models.SET_NULL)
    operation_modification = models.ForeignKey("BulkEditOperation", null=True, blank=True, on_delete=models.SET_NULL)
    donnees_action = models.JSONField(default=dict)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    agent_utilisateur = models.CharField(max_length=255, blank=True)
    previous_hash = models.CharField(max_length=128, blank=True)
    current_hash = models.CharField(max_length=128, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)


class BulkEditOperation(models.Model):
    STATUTS = (
        ("PENDING", "PENDING"),
        ("APPLIED", "APPLIED"),
        ("ROLLED_BACK", "ROLLED_BACK"),
    )
    utilisateur = models.ForeignKey(User, on_delete=models.PROTECT)
    champs_modifies = models.JSONField(default=dict)
    selection = models.JSONField(default=list)
    statut = models.CharField(max_length=16, choices=STATUTS, default="PENDING")
    cree_le = models.DateTimeField(auto_now_add=True)
    applique_le = models.DateTimeField(null=True, blank=True)


class BulkEditChange(models.Model):
    operation = models.ForeignKey(BulkEditOperation, on_delete=models.CASCADE, related_name="changements")
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    avant = models.JSONField(default=dict)
    apres = models.JSONField(default=dict)
    cree_le = models.DateTimeField(auto_now_add=True)
